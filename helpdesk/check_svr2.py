import frappe

def execute():
    """Check ticket naming and fix SVR logs"""
    
    # Check what the actual ticket name format is
    tickets = frappe.get_all('HD Ticket', fields=['name', 'subject'], limit=5, order_by='creation desc')
    print("\nRecent tickets:")
    for ticket in tickets:
        print(f"  Name: {ticket.name}, Subject: {ticket.subject}")
    
    # Check the specific ticket from the URL
    # The URL shows tickets/19#svr so the ticket might be named just "19"
    ticket_19 = frappe.db.exists('HD Ticket', '19')
    print(f"\nTicket '19' exists: {ticket_19}")
    
    if ticket_19:
        ticket_doc = frappe.get_doc('HD Ticket', '19')
        print(f"Ticket 19 details:")
        print(f"  Name: {ticket_doc.name}")
        print(f"  Subject: {ticket_doc.subject}")
        print(f"  SVR Log ID: {ticket_doc.svr_log_id}")
        
        # Now check SVR logs for this ticket
        logs = frappe.get_all(
            'EPFM Maintanace Log',
            filters={'ticket_id': '19'},
            fields=['name', 'svr_number', 'ticket_id', 'date', 'status'],
            order_by='creation desc'
        )
        
        print(f"\nFound {len(logs)} SVR logs for ticket 19:")
        for log in logs:
            print(f"  - {log.name}: {log.svr_number} (Status: {log.status})")
