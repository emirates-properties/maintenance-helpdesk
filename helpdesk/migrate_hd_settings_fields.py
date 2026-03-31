"""
Manual migration script to add AI instruction fields to HD Settings
Run with: bench --site pms.localhost execute helpdesk.migrate_hd_settings_fields.migrate
"""

import frappe

def migrate():
	"""Add AI instruction fields to HD Settings doctype"""
	print("Starting manual migration of HD Settings...")
	
	try:
		# Import the doctype
		from frappe.modules import import_file
		
		# Clear cache
		frappe.clear_cache(doctype="HD Settings")
		
		# Reload the doctype from JSON
		doctype_path = frappe.get_app_path("helpdesk", "helpdesk", "doctype", "hd_settings", "hd_settings.json")
		import_file.import_file_by_path(doctype_path, data_import=False, force=True)
		
		print("✓ HD Settings doctype updated successfully!")
		print("✓ New AI instruction fields have been added:")
		print("  - ai_general_instructions")
		print("  - ai_tone_professional")
		print("  - ai_tone_friendly")
		print("  - ai_tone_concise")
		print("  - ai_tone_detailed")
		
		# Try to update the existing HD Settings document
		try:
			if frappe.db.exists("HD Settings", "HD Settings"):
				settings = frappe.get_doc("HD Settings", "HD Settings")
				settings.save()  # This will trigger set_ai_defaults()
				print("✓ HD Settings document updated with default values!")
		except Exception as e:
			print(f"Note: Could not auto-update HD Settings document: {e}")
			print("Please open HD Settings in the UI and save it to populate default values.")
		
		frappe.db.commit()
		print("\n✅ Migration completed successfully!")
		
	except Exception as e:
		print(f"❌ Error during migration: {e}")
		frappe.db.rollback()
		raise

if __name__ == "__main__":
	migrate()
