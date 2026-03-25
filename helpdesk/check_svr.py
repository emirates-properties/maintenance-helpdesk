import frappe

def execute():
    """Check SVR logs for ticket HD-TICKET-19"""
    ticket_id = 'HD-TICKET-19'
    
    # Check if ticket exists
    ticket = frappe.db.exists('HD Ticket', ticket_id)
    print(f"\nTicket {ticket_id} exists: {ticket}")
    
    if ticket:
        ticket_doc = frappe.get_doc('HD Ticket', ticket_id)
        print(f"Ticket svr_log_id field: {ticket_doc.svr_log_id}")
    
    # Check for SVR logs
    logs = frappe.get_all(
        'EPFM Maintanace Log',
        filters={'ticket_id': ticket_id},
        fields=['name', 'svr_number', 'ticket_id', 'date', 'status'],
        order_by='creation desc'
    )
    
    print(f"\nFound {len(logs)} SVR logs for {ticket_id}:")
    for log in logs:
        print(f"  - {log.name}: {log.svr_number} (Status: {log.status})")
    
    # Check all SVR logs to see if any reference this ticket
    all_logs = frappe.get_all(
        'EPFM Maintanace Log',
        fields=['name', 'svr_number', 'ticket_id'],
        limit=10
    )
    
    print(f"\nRecent SVR logs (any ticket):")
    for log in all_logs:
        print(f"  - {log.name}: {log.svr_number} -> Ticket: {log.ticket_id}")
