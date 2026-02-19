frappe.ui.form.on('Journal Entry', {
	refresh(frm) {
		// Only act on expense claim JEs created by ClaimSuite
		if (!frm.doc.user_remark || !frm.doc.user_remark.startsWith('Expense Claim -')) return;

		// Show payment status indicator
		if (frm.doc.custom_payment_journal) {
			frm.dashboard.add_indicator(
				__('Employee Paid — {0}', [frm.doc.custom_payment_journal]),
				'green'
			);
		}

		// Show "Pay Employee" button only on submitted JEs that haven't been paid yet
		if (frm.doc.docstatus === 1 && !frm.doc.custom_payment_journal) {
			frm.add_custom_button(__('Pay Employee'), () => {
				// Auto-fetch the payable account (credit side of the expense JE) and amount
				let payable_account = '';
				let amount = frm.doc.total_debit;

				for (let row of (frm.doc.accounts || [])) {
					if (row.credit_in_account_currency > 0) {
						payable_account = row.account;
						break;
					}
				}

				let d = new frappe.ui.Dialog({
					title: __('Pay Employee'),
					fields: [
						{
							fieldtype: 'Link',
							fieldname: 'payable_account',
							label: __('Payable Account'),
							options: 'Account',
							default: payable_account,
							read_only: 1,
							description: __('Auto-fetched from expense claim'),
						},
						{
							fieldtype: 'Currency',
							fieldname: 'amount',
							label: __('Amount'),
							default: amount,
							read_only: 1,
						},
						{ fieldtype: 'Column Break' },
						{
							fieldtype: 'Link',
							fieldname: 'payment_account',
							label: __('Payment Account'),
							options: 'Account',
							reqd: 1,
							filters: {
								account_type: ['in', ['Bank', 'Cash']],
								company: frm.doc.company,
							},
							description: __('Bank or cash account used to pay the employee'),
						},
						{
							fieldtype: 'Date',
							fieldname: 'posting_date',
							label: __('Payment Date'),
							default: frappe.datetime.get_today(),
							reqd: 1,
						},
					],
					primary_action_label: __('Create Payment Journal'),
					primary_action(values) {
						frappe.call({
							method: 'claimsuite.api.create_payment_journal',
							args: {
								expense_journal: frm.doc.name,
								payable_account: values.payable_account,
								payment_account: values.payment_account,
								amount: values.amount,
								posting_date: values.posting_date,
								company: frm.doc.company,
							},
							freeze: true,
							freeze_message: __('Creating payment journal…'),
							callback(r) {
								if (r.message) {
									frappe.show_alert({
										message: __('Payment Journal {0} created', [
											`<a href="/app/journal-entry/${r.message}">${r.message}</a>`,
										]),
										indicator: 'green',
									});
									d.hide();
									frm.reload_doc();
								}
							},
						});
					},
				});

				d.show();
			}, __('Actions'));
		}
	},
});
