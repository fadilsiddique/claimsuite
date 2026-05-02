import frappe
from frappe import _
from frappe.utils import add_months, get_first_day, get_last_day, getdate, today


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
def get_modes_of_payment():
	settings = frappe.get_single("Claim Settings")
	company = frappe.db.get_value("Account", settings.default_payment_account, "company")

	modes = frappe.get_all(
		"Mode of Payment",
		filters={"enabled": 1},
		fields=["name"],
		order_by="name asc",
	)

	result = []
	for mode in modes:
		account = frappe.db.get_value(
			"Mode of Payment Account",
			{"parent": mode.name, "company": company},
			"default_account",
		)
		if account:
			result.append({"label": mode.name, "value": mode.name, "account": account})

	return result


@frappe.whitelist()
def create_expense_claim(claim_type, amount, expense_date, description="", file_url="", project="", payment_method="employee", mode_of_payment=""):
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

	company = frappe.db.get_value("Account", expense_account, "company")

	# Determine credit account based on payment method
	if payment_method == "company":
		if not mode_of_payment:
			frappe.throw(_("Please select a Mode of Payment"))
		credit_account = frappe.db.get_value(
			"Mode of Payment Account",
			{"parent": mode_of_payment, "company": company},
			"default_account",
		)
		if not credit_account:
			frappe.throw(
				_("No account configured for Mode of Payment '{0}' in company '{1}'").format(
					mode_of_payment, company
				)
			)
	else:
		if not settings.default_payment_account:
			frappe.throw(_("Default payment account not configured in Claim Settings"))
		credit_account = settings.default_payment_account

	remark = f"Expense Claim - {claim_type} - {description} - {expense_date}"

	debit_row = {
		"account": expense_account,
		"debit_in_account_currency": amount,
		"credit_in_account_currency": 0,
	}
	credit_row = {
		"account": credit_account,
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
def update_expense_claim(name, claim_type, amount, expense_date, description="", file_url="", project="", payment_method="employee", mode_of_payment=""):
	je = frappe.get_doc("Journal Entry", name)

	if je.owner != frappe.session.user:
		frappe.throw(_("You don't have permission to edit this claim"))
	if je.docstatus != 0:
		frappe.throw(_("Only draft claims can be edited"))

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

	company = frappe.db.get_value("Account", expense_account, "company")

	if payment_method == "company":
		if not mode_of_payment:
			frappe.throw(_("Please select a Mode of Payment"))
		credit_account = frappe.db.get_value(
			"Mode of Payment Account",
			{"parent": mode_of_payment, "company": company},
			"default_account",
		)
		if not credit_account:
			frappe.throw(
				_("No account configured for Mode of Payment '{0}' in company '{1}'").format(
					mode_of_payment, company
				)
			)
	else:
		if not settings.default_payment_account:
			frappe.throw(_("Default payment account not configured in Claim Settings"))
		credit_account = settings.default_payment_account

	je.posting_date = expense_date
	je.company = company
	je.user_remark = f"Expense Claim - {claim_type} - {description} - {expense_date}"

	debit_row = {
		"account": expense_account,
		"debit_in_account_currency": amount,
		"credit_in_account_currency": 0,
	}
	credit_row = {
		"account": credit_account,
		"debit_in_account_currency": 0,
		"credit_in_account_currency": amount,
	}
	if project:
		debit_row["project"] = project
		credit_row["project"] = project

	je.set("accounts", [debit_row, credit_row])
	je.save()

	if file_url:
		existing = frappe.db.exists(
			"File",
			{
				"file_url": file_url,
				"attached_to_doctype": "Journal Entry",
				"attached_to_name": je.name,
			},
		)
		if not existing:
			frappe.get_doc({
				"doctype": "File",
				"file_url": file_url,
				"attached_to_doctype": "Journal Entry",
				"attached_to_name": je.name,
			}).save(ignore_permissions=True)

	return {"name": je.name, "amount": amount, "claim_type": claim_type}


@frappe.whitelist()
def create_payment_journal(expense_journal, payable_account, payment_account, amount, posting_date, company):
	"""Create a payment JE to reimburse the employee and link it back to the expense JE."""
	amount = float(amount)

	je = frappe.get_doc({
		"doctype": "Journal Entry",
		"voucher_type": "Journal Entry",
		"posting_date": posting_date,
		"company": company,
		"user_remark": f"Employee reimbursement for {expense_journal}",
		"accounts": [
			{
				"account": payable_account,
				"debit_in_account_currency": amount,
				"credit_in_account_currency": 0,
			},
			{
				"account": payment_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": amount,
			},
		],
	})
	je.insert()
	je.submit()

	# Link the payment JE back to the original expense JE
	frappe.db.set_value("Journal Entry", expense_journal, {
		"custom_payment_journal": je.name,
		"custom_payment_to_employee": "Paid",
	})

	return je.name


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

	# Pending reimbursement: employee-paid claims (credit row = default_payment_account)
	# that haven't been marked as paid back to the employee yet.
	settings = frappe.get_single("Claim Settings")
	pending_amount = 0
	pending_count = 0
	if settings.default_payment_account:
		pending_rows = _fetch_claim_rows(user, None, None)
		for r in pending_rows:
			if (
				r.get("credit_account") == settings.default_payment_account
				and (r.get("custom_payment_to_employee") or "") != "Paid"
			):
				pending_amount += float(r.get("total_debit") or 0)
				pending_count += 1

	return {
		"total_claims": len(all_claims),
		"total_amount": total_amount,
		"draft_count": draft_count,
		"submitted_count": submitted_count,
		"cancelled_count": cancelled_count,
		"pending_amount": pending_amount,
		"pending_count": pending_count,
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
		fields=["name", "posting_date", "total_debit", "docstatus", "user_remark", "creation",
				"custom_payment_to_employee", "custom_payment_journal"],
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

	# Extract credit account so the edit form can infer payment method / mode
	credit_account = None
	for row in je.accounts:
		if row.credit_in_account_currency > 0:
			credit_account = row.account
			break

	settings = frappe.get_single("Claim Settings")
	payment_method = "company"
	mode_of_payment = ""
	if credit_account and credit_account == settings.default_payment_account:
		payment_method = "employee"
	elif credit_account:
		mode_of_payment = frappe.db.get_value(
			"Mode of Payment Account",
			{"default_account": credit_account, "company": je.company},
			"parent",
		) or ""

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
		"payment_status": je.custom_payment_to_employee or "",
		"payment_journal": je.custom_payment_journal or "",
		"payment_method": payment_method,
		"mode_of_payment": mode_of_payment,
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


def _period_window(period):
	t = getdate(today())

	if period == "month":
		start = get_first_day(t)
		end = get_last_day(t)
		prev_anchor = add_months(t, -1)
		prev_start = get_first_day(prev_anchor)
		prev_end = get_last_day(prev_anchor)
	elif period == "quarter":
		q_start_month = ((t.month - 1) // 3) * 3 + 1
		start = getdate(f"{t.year}-{q_start_month:02d}-01")
		end = get_last_day(add_months(start, 2))
		prev_start = add_months(start, -3)
		prev_end = get_last_day(add_months(prev_start, 2))
	elif period == "year":
		start = getdate(f"{t.year}-01-01")
		end = getdate(f"{t.year}-12-31")
		prev_start = getdate(f"{t.year - 1}-01-01")
		prev_end = getdate(f"{t.year - 1}-12-31")
	else:
		# "all" — no date filter, no prior comparison
		return None, None, None, None

	return start, end, prev_start, prev_end


def _aggregate_claims(rows, default_payment_account):
	by_type = {}
	paid_by_me = {
		"amount": 0.0, "count": 0,
		"pending_amount": 0.0, "pending_count": 0,
		"reimbursed_amount": 0.0, "reimbursed_count": 0,
	}
	paid_by_company = {"amount": 0.0, "count": 0}
	total_amount = 0.0
	claim_count = 0

	for r in rows:
		amount = float(r.get("total_debit") or 0)
		total_amount += amount
		claim_count += 1

		try:
			claim_type = (r.get("user_remark") or "").split(" - ")[1].strip() or "Other"
		except IndexError:
			claim_type = "Other"

		bucket = by_type.setdefault(claim_type, {"amount": 0.0, "count": 0})
		bucket["amount"] += amount
		bucket["count"] += 1

		if default_payment_account and r.get("credit_account") == default_payment_account:
			paid_by_me["amount"] += amount
			paid_by_me["count"] += 1
			if (r.get("custom_payment_to_employee") or "") == "Paid":
				paid_by_me["reimbursed_amount"] += amount
				paid_by_me["reimbursed_count"] += 1
			else:
				paid_by_me["pending_amount"] += amount
				paid_by_me["pending_count"] += 1
		else:
			paid_by_company["amount"] += amount
			paid_by_company["count"] += 1

	by_type_list = sorted(
		[{"claim_type": k, **v} for k, v in by_type.items()],
		key=lambda x: x["amount"],
		reverse=True,
	)

	return {
		"total_amount": total_amount,
		"claim_count": claim_count,
		"by_type": by_type_list,
		"paid_by_me": paid_by_me,
		"paid_by_company": paid_by_company,
	}


def _fetch_claim_rows(user, start, end):
	params = {"user": user}
	date_clause = ""
	if start and end:
		date_clause = "AND je.posting_date BETWEEN %(start)s AND %(end)s"
		params["start"] = start
		params["end"] = end

	return frappe.db.sql(
		f"""
		SELECT je.name, je.total_debit, je.user_remark,
		       je.custom_payment_to_employee, jea.account AS credit_account
		FROM `tabJournal Entry` je
		INNER JOIN `tabJournal Entry Account` jea ON jea.parent = je.name
		WHERE je.voucher_type = 'Journal Entry'
		  AND je.owner = %(user)s
		  AND je.user_remark LIKE 'Expense Claim -%%'
		  AND jea.credit_in_account_currency > 0
		  {date_clause}
		""",
		params,
		as_dict=True,
	)


@frappe.whitelist()
def get_insights(period="month"):
	user = frappe.session.user
	settings = frappe.get_single("Claim Settings")
	default_payment_account = settings.default_payment_account

	start, end, prev_start, prev_end = _period_window(period)

	rows = _fetch_claim_rows(user, start, end)
	agg = _aggregate_claims(rows, default_payment_account)

	prev_total_amount = None
	if prev_start and prev_end:
		prev_rows = _fetch_claim_rows(user, prev_start, prev_end)
		prev_total_amount = sum(float(r.get("total_debit") or 0) for r in prev_rows)

	return {
		"period": period,
		"start_date": start,
		"end_date": end,
		"prev_total_amount": prev_total_amount,
		**agg,
	}
