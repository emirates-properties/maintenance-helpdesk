// Copyright (c) 2023, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("HD Ticket", {
  onload(frm) {
    if (frm.is_new()) return;
    frm.call("mark_seen");
  },
  
  property(frm) {
    // Clear unit when property changes
    if (frm.doc.unit) {
      frm.set_value('unit', '');
    }
    
    // Set filter for unit field based on selected property
    frm.set_query('unit', function() {
      if (frm.doc.property) {
        return {
          filters: {
            'property': frm.doc.property
          }
        };
      }
    });
  },
  
  setup(frm) {
    // Set query for unit field to filter by property
    frm.set_query('unit', function() {
      if (frm.doc.property) {
        return {
          filters: {
            'property': frm.doc.property
          }
        };
      }
    });
  }
});
