import frappe
import json

def execute():
    """Test the API with detailed logging"""
    from helpdesk.api.svr import get_ticket_svr_logs
    
    # Simulate the API call
    frappe.set_user("Administrator")
    
    ticket_id = '19'
    print(f"\nTesting get_ticket_svr_logs with ticket_id: {ticket_id}")
    print(f"Type: {type(ticket_id)}")
    
    # Call the function
    try:
        result = get_ticket_svr_logs(ticket_id)
        print(f"\nResult type: {type(result)}")
        print(f"Result length: {len(result) if result else 0}")
        print(f"\nResult: {json.dumps(result, indent=2, default=str)}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Also test directly with frappe.get_all
    print(f"\n\nDirect frappe.get_all test:")
    logs = frappe.get_all(
        'EPFM Maintanace Log',
        filters={'ticket_id': ticket_id},
        fields=['name', 'svr_number', 'date'],
        order_by='creation desc'
    )
    print(f"Found {len(logs)} logs")
