import os

import frappe

no_cache = 1


def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	context.csrf_token = csrf_token

	index_path = os.path.join(
		os.path.dirname(__file__), "..", "public", "frontend", "index.html"
	)

	with open(index_path) as f:
		content = f.read()

	# Inject actual CSRF token
	content = content.replace("'{{ csrf_token }}'", f"'{csrf_token}'")

	context.frontend_html = content
	context.no_breadcrumbs = True
	context.no_header = True
