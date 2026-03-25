import frappe

def execute():
    """Test the get_ticket_svr_logs API"""
    from helpdesk.api.svr import get_ticket_svr_logs
    
    ticket_id = '19'
    print(f"\nCalling get_ticket_svr_logs with ticket_id: {ticket_id}")
    
    try:
        result = get_ticket_svr_logs(ticket_id)
        print(f"\nSuccess! Returned {len(result)} SVR logs:")
        for log in result:
            print(f"  - {log.get('name')}: {log.get('svr_number')}")
            print(f"    Fields: {list(log.keys())}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
