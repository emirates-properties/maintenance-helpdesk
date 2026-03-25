import frappe

def execute():
    meta = frappe.get_meta('HD Ticket')
    print("FIELDS:")
    for f in meta.fields:
        print(f"{f.fieldname}: {f.fieldtype}")
