"""Google Wallet (generic pass) integration for ClaimSuite.

The pass shows the user's pending reimbursement balance and refreshes
whenever a Journal Entry's `custom_payment_to_employee` flag flips.

Credentials are loaded from site_config.json — never from the repo.
"""

import hashlib
import time

import frappe
import jwt
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from claimsuite.api import get_pending_for_user

WALLET_SCOPE = "https://www.googleapis.com/auth/wallet_object.issuer"
SAVE_URL_BASE = "https://pay.google.com/gp/v/save/"
CLASS_SUFFIX = "claimsuite_reimbursement_v1"


def _issuer_id():
	issuer = frappe.conf.get("google_wallet_issuer_id")
	if not issuer:
		frappe.throw("google_wallet_issuer_id not set in site_config.json")
	return str(issuer)


def _class_id():
	return f"{_issuer_id()}.{CLASS_SUFFIX}"


def _load_sa_credentials():
	inline = frappe.conf.get("google_wallet_service_account")
	if inline:
		return service_account.Credentials.from_service_account_info(
			inline, scopes=[WALLET_SCOPE]
		)
	path = frappe.conf.get("google_wallet_service_account_path")
	if path:
		return service_account.Credentials.from_service_account_file(
			path, scopes=[WALLET_SCOPE]
		)
	frappe.throw("Google Wallet service account not configured in site_config.json")


def _wallet_client():
	creds = _load_sa_credentials()
	return build("walletobjects", "v1", credentials=creds, cache_discovery=False)


def _object_id(user):
	digest = hashlib.md5(user.encode("utf-8")).hexdigest()[:16]
	return f"{_issuer_id()}.{digest}"


def _build_pass_object(user):
	amount, count = get_pending_for_user(user)
	full_name = frappe.db.get_value("User", user, "full_name") or user
	updated = frappe.utils.format_date(frappe.utils.today(), "d MMM yyyy")

	return {
		"id": _object_id(user),
		"classId": _class_id(),
		"state": "ACTIVE",
		"cardTitle": {"defaultValue": {"language": "en", "value": "ClaimSuite"}},
		"header": {"defaultValue": {"language": "en", "value": "Reimbursement Card"}},
		"subheader": {"defaultValue": {"language": "en", "value": full_name}},
		"textModulesData": [
			{"id": "amount", "header": "Pending", "body": f"AED {amount:,.2f}"},
			{"id": "count", "header": "Claims", "body": str(count)},
			{"id": "updated", "header": "Updated", "body": updated},
		],
		"barcode": {
			"type": "QR_CODE",
			"value": _object_id(user),
			"alternateText": user,
		},
		"hexBackgroundColor": "#29A38B",
	}


def ensure_pass_object(user):
	client = _wallet_client()
	oid = _object_id(user)
	try:
		client.genericobject().get(resourceId=oid).execute()
	except HttpError as e:
		if e.resp.status == 404:
			client.genericobject().insert(body=_build_pass_object(user)).execute()
		else:
			raise


def update_user_pass(doc, method=None):
	"""doc_events hook for Journal Entry on_update.

	Patches the issuing user's existing Wallet pass when the
	reimbursement-status flag flips. No-op for non-claim JEs or
	unrelated edits.
	"""
	try:
		if (doc.user_remark or "")[:15] != "Expense Claim -":
			return
		before = doc.get_doc_before_save()
		if not before:
			return
		old_status = (before.custom_payment_to_employee or "")
		new_status = (doc.custom_payment_to_employee or "")
		if old_status == new_status:
			return

		client = _wallet_client()
		oid = _object_id(doc.owner)
		# Only patch if the object exists upstream — if the user never tapped
		# "Save to Wallet", there's nothing to update.
		try:
			client.genericobject().get(resourceId=oid).execute()
		except HttpError as e:
			if e.resp.status == 404:
				return
			raise
		client.genericobject().patch(
			resourceId=oid, body=_build_pass_object(doc.owner)
		).execute()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "claimsuite.wallet.update_user_pass")


def _sa_signing_material():
	"""Return (client_email, private_key_pem) sourced from site config."""
	inline = frappe.conf.get("google_wallet_service_account")
	if inline:
		return inline["client_email"], inline["private_key"]
	path = frappe.conf.get("google_wallet_service_account_path")
	if path:
		import json
		with open(path) as f:
			data = json.load(f)
		return data["client_email"], data["private_key"]
	frappe.throw("Google Wallet service account not configured in site_config.json")


@frappe.whitelist()
def get_save_jwt():
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Login required")

	ensure_pass_object(user)

	client_email, private_key_pem = _sa_signing_material()
	payload = {
		"iss": client_email,
		"aud": "google",
		"typ": "savetowallet",
		"iat": int(time.time()),
		"payload": {
			"genericObjects": [
				{"id": _object_id(user), "classId": _class_id()}
			]
		},
	}
	token = jwt.encode(payload, private_key_pem, algorithm="RS256")
	return {"jwt": token, "save_url": f"{SAVE_URL_BASE}{token}"}
