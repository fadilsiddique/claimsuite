"""One-shot script to register the ClaimSuite generic-pass *class* with Google Wallet.

Run with:
    bench --site <site> execute claimsuite.tools.register_wallet_class.run

Idempotent: GETs first, INSERTs only on 404.
"""

from googleapiclient.errors import HttpError

from claimsuite.wallet import _class_id, _wallet_client


def _build_class_body():
	return {
		"id": _class_id(),
		"classTemplateInfo": {
			"cardTemplateOverride": {
				"cardRowTemplateInfos": [
					{
						"twoItems": {
							"startItem": {
								"firstValue": {
									"fields": [
										{"fieldPath": "object.textModulesData['amount']"}
									]
								}
							},
							"endItem": {
								"firstValue": {
									"fields": [
										{"fieldPath": "object.textModulesData['count']"}
									]
								}
							},
						}
					},
					{
						"oneItem": {
							"item": {
								"firstValue": {
									"fields": [
										{"fieldPath": "object.textModulesData['updated']"}
									]
								}
							}
						}
					},
				]
			}
		},
		"hexBackgroundColor": "#29A38B",
		"multipleDevicesAndHoldersAllowedStatus": "ONE_USER_ALL_DEVICES",
	}


def run():
	client = _wallet_client()
	cid = _class_id()
	try:
		client.genericclass().get(resourceId=cid).execute()
		print(f"Class already exists, skipping: {cid}")
	except HttpError as e:
		if e.resp.status == 404:
			client.genericclass().insert(body=_build_class_body()).execute()
			print(f"Created class: {cid}")
		else:
			raise
