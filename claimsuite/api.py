import frappe
from frappe import _


@frappe.whitelist()
def get_claim_settings():
	settings = frappe.get_single("Claim Settings")
	claim_types = frappe.get_all("Claim Type", pluck="name", order_by="name asc")

	account_map = {}
	for row in settings.account:
		account_map[row.claim_type] = row.account

	return {
		"claim_types": claim_types,
		"account_map": account_map,
		"default_payment_account": settings.default_payment_account,
		"default_vat_account": settings.default_vat_account,
	}


@frappe.whitelist()
def get_projects():
	projects = frappe.get_all(
		"Project",
		filters={"status": "Open"},
		fields=["name", "project_name"],
		order_by="project_name asc",
	)
	return [{"label": p.project_name or p.name, "value": p.name} for p in projects]


@frappe.whitelist()
def create_expense_claim(claim_type, amount, expense_date, description="", file_url="", project=""):
	amount = float(amount)
	if amount <= 0:
		frappe.throw(_("Amount must be greater than zero"))

	settings = frappe.get_single("Claim Settings")

	expense_account = None
	for row in settings.account:
		if row.claim_type == claim_type:
			expense_account = row.account
			break

	if not expense_account:
		frappe.throw(_("No account mapped for claim type: {0}").format(claim_type))

	if not settings.default_payment_account:
		frappe.throw(_("Default payment account not configured in Claim Settings"))

	company = frappe.db.get_value("Account", expense_account, "company")

	remark = f"Expense Claim - {claim_type} - {description} - {expense_date}"

	debit_row = {
		"account": expense_account,
		"debit_in_account_currency": amount,
		"credit_in_account_currency": 0,
	}
	credit_row = {
		"account": settings.default_payment_account,
		"debit_in_account_currency": 0,
		"credit_in_account_currency": amount,
	}
	if project:
		debit_row["project"] = project
		credit_row["project"] = project

	je = frappe.get_doc({
		"doctype": "Journal Entry",
		"voucher_type": "Journal Entry",
		"posting_date": expense_date,
		"company": company,
		"user_remark": remark,
		"accounts": [debit_row, credit_row],
	})
	je.insert()

	# Attach receipt file to the Journal Entry
	if file_url:
		frappe.get_doc({
			"doctype": "File",
			"file_url": file_url,
			"attached_to_doctype": "Journal Entry",
			"attached_to_name": je.name,
		}).save(ignore_permissions=True)

	return {"name": je.name, "amount": amount, "claim_type": claim_type}


@frappe.whitelist()
def upload_receipt():
	"""Upload a receipt file and return the file URL."""
	if not frappe.request.files:
		frappe.throw(_("No file uploaded"))

	file = frappe.request.files.get("file")
	if not file:
		frappe.throw(_("No file found in request"))

	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": file.filename,
		"content": file.stream.read(),
		"is_private": 1,
	})
	file_doc.save(ignore_permissions=True)

	return {"file_url": file_doc.file_url, "file_name": file_doc.file_name}


@frappe.whitelist()
def get_dashboard_stats():
	user = frappe.session.user

	filters = {
		"voucher_type": "Journal Entry",
		"owner": user,
		"user_remark": ["like", "Expense Claim -%"],
	}

	all_claims = frappe.get_all(
		"Journal Entry",
		filters=filters,
		fields=["name", "posting_date", "total_debit", "docstatus", "user_remark", "creation"],
		order_by="creation desc",
	)

	total_amount = 0
	draft_count = 0
	submitted_count = 0
	cancelled_count = 0

	for claim in all_claims:
		total_amount += claim.total_debit or 0
		if claim.docstatus == 0:
			draft_count += 1
		elif claim.docstatus == 1:
			submitted_count += 1
		elif claim.docstatus == 2:
			cancelled_count += 1

	recent = all_claims[:5]

	return {
		"total_claims": len(all_claims),
		"total_amount": total_amount,
		"draft_count": draft_count,
		"submitted_count": submitted_count,
		"cancelled_count": cancelled_count,
		"recent_claims": recent,
	}


@frappe.whitelist()
def get_claims(status="all", start=0, limit=20):
	user = frappe.session.user

	filters = {
		"voucher_type": "Journal Entry",
		"owner": user,
		"user_remark": ["like", "Expense Claim -%"],
	}

	if status == "draft":
		filters["docstatus"] = 0
	elif status == "submitted":
		filters["docstatus"] = 1
	elif status == "cancelled":
		filters["docstatus"] = 2

	claims = frappe.get_all(
		"Journal Entry",
		filters=filters,
		fields=["name", "posting_date", "total_debit", "docstatus", "user_remark", "creation"],
		order_by="creation desc",
		start=int(start),
		page_length=int(limit),
	)

	return claims


@frappe.whitelist()
def get_claim_detail(name):
	je = frappe.get_doc("Journal Entry", name)

	if je.owner != frappe.session.user:
		frappe.throw(_("You don't have permission to view this claim"))

	attachments = frappe.get_all(
		"File",
		filters={"attached_to_doctype": "Journal Entry", "attached_to_name": name},
		fields=["file_url", "file_name"],
	)

	# Extract project from the debit row (expense side)
	project = None
	project_name = None
	for row in je.accounts:
		if row.debit_in_account_currency > 0 and row.project:
			project = row.project
			project_name = frappe.db.get_value("Project", project, "project_name") or project
			break

	return {
		"name": je.name,
		"posting_date": je.posting_date,
		"total_debit": je.total_debit,
		"docstatus": je.docstatus,
		"user_remark": je.user_remark,
		"creation": je.creation,
		"company": je.company,
		"project": project,
		"project_name": project_name,
		"accounts": [
			{
				"account": row.account,
				"debit": row.debit_in_account_currency,
				"credit": row.credit_in_account_currency,
			}
			for row in je.accounts
		],
		"attachments": attachments,
	}
