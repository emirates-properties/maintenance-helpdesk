import frappe

def execute():
    """Debug the ticket_id field"""
    
    # Get one SVR log to see how ticket_id is stored
    log = frappe.get_doc('EPFM Maintanace Log', 'ML-108')
    print(f"\nML-108 ticket_id field:")
    print(f"  Value: {repr(log.ticket_id)}")
    print(f"  Type: {type(log.ticket_id)}")
    
    # Try different query methods
    print(f"\n1. Query with string '19':")
    logs1 = frappe.get_all('EPFM Maintanace Log', filters={'ticket_id': '19'}, fields=['name'])
    print(f"   Found: {len(logs1)}")
    
    print(f"\n2. Query with int 19:")
    logs2 = frappe.get_all('EPFM Maintanace Log', filters={'ticket_id': 19}, fields=['name'])
    print(f"   Found: {len(logs2)}")
    
    print(f"\n3. Using db.sql:")
    logs3 = frappe.db.sql("""
        SELECT name, ticket_id 
        FROM `tabEPFM Maintanace Log` 
        WHERE ticket_id = '19'
    """, as_dict=True)
    print(f"   Found: {len(logs3)}")
    for log in logs3:
        print(f"   - {log.name}: ticket_id = {repr(log.ticket_id)}")
