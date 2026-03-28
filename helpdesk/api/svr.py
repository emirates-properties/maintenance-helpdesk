import frappe
from frappe import _


@frappe.whitelist()
def create_svr_log(data):
    """
    Create a new EPFM Maintenance Log (SVR) entry
    
    Args:
        data: Dictionary containing SVR log data
        
    Returns:
        Created document name
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            import json
            data = json.loads(data)
        
        # Log the incoming data for debugging
        frappe.logger().debug(f"Creating SVR log with data: {data}")
        
        # Ensure required fields
        if not data.get('date'):
            frappe.throw(_("Date is required"))
        
        if not data.get('svr_number'):
            frappe.throw(_("SVR Number is required"))
            
        if not data.get('property'):
            frappe.throw(_("Property is required"))
        
        # Clean up data - extract values from objects if needed
        def clean_value(val):
            if val is None or val == '':
                return None
            if isinstance(val, dict) and 'value' in val:
                return val['value']
            return val
        
        # Create new EPFM Maintanace Log document
        doc = frappe.get_doc({
            'doctype': 'EPFM Maintanace Log',
            'date': clean_value(data.get('date')),
            'svr_number': clean_value(data.get('svr_number')),
            'ticket_id': clean_value(data.get('ticket_id')),
            'property': clean_value(data.get('property')),
            'unit': clean_value(data.get('unit')),
            'tenant_name': clean_value(data.get('tenant_name')),
            'contract_number': clean_value(data.get('contract_number')),
            'zone': clean_value(data.get('zone')),
            'service_category': clean_value(data.get('service_category')),
            'assigned_to': clean_value(data.get('assigned_to')),
            'priority': clean_value(data.get('priority')),
            'remarks': clean_value(data.get('remarks')),
            'supervisor_inspection_required': int(data.get('supervisor_inspection_required', 0)),
            'status': clean_value(data.get('status', 'OPEN')),
            'work_done_by': clean_value(data.get('work_done_by', 'EPFM'))
        })
        
        # Handle tags if provided
        if data.get('tags') and isinstance(data.get('tags'), list):
            for tag in data.get('tags'):
                doc.append('tags', {
                    'tag': tag
                })
        
        # Insert the document
        doc.insert()
        
        # Link SVR log back to the ticket if ticket_id is provided
        ticket_id = clean_value(data.get('ticket_id'))
        if ticket_id:
            try:
                # Update the HD Ticket with the SVR log link
                if frappe.db.exists('HD Ticket', ticket_id):
                    frappe.db.set_value('HD Ticket', ticket_id, 'svr_log_id', doc.name)
                    frappe.logger().info(f"Linked SVR log {doc.name} to ticket {ticket_id}")
            except Exception as link_error:
                frappe.logger().warning(f"Could not link SVR to ticket: {str(link_error)}")
                # Don't fail the whole operation if linking fails
        
        # Commit the transaction
        frappe.db.commit()
        
        frappe.logger().info(f"Successfully created SVR log: {doc.name}")
        
        return {
            'success': True,
            'name': doc.name,
            'message': _('SVR Log created successfully')
        }
        
    except Exception as e:
        frappe.logger().error(f"Error creating SVR log: {str(e)}")
        frappe.log_error(f"Error creating SVR log: {str(e)}")
        frappe.throw(_("Failed to create SVR log: {0}").format(str(e)))


@frappe.whitelist()
def get_svr_log(name):
    """
    Get EPFM Maintenance Log details
    
    Args:
        name: Document name
        
    Returns:
        Document data
    """
    try:
        doc = frappe.get_doc('EPFM Maintanace Log', name)
        return doc.as_dict()
    except Exception as e:
        frappe.throw(_("Failed to fetch SVR log: {0}").format(str(e)))


@frappe.whitelist()
def update_svr_log(name, data):
    """
    Update EPFM Maintenance Log
    
    Args:
        name: Document name
        data: Dictionary containing fields to update
        
    Returns:
        Updated document name
    """
    try:
        if isinstance(data, str):
            import json
            data = json.loads(data)
        
        doc = frappe.get_doc('EPFM Maintanace Log', name)
        
        # Update fields
        for key, value in data.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.save()
        frappe.db.commit()
        
        return {
            'success': True,
            'name': doc.name,
            'message': _('SVR Log updated successfully')
        }
        
    except Exception as e:
        frappe.log_error(f"Error updating SVR log: {str(e)}")
        frappe.throw(_("Failed to update SVR log: {0}").format(str(e)))


@frappe.whitelist()
def get_ticket_svr_logs(ticket_id):
    """
    Get all EPFM Maintenance Logs for a specific ticket
    
    Args:
        ticket_id: HD Ticket ID
        
    Returns:
        List of SVR logs associated with the ticket
    """
    try:
        if not ticket_id:
            return []
        
        # Query all SVR logs linked to this ticket
        svr_logs = frappe.get_all(
            'EPFM Maintanace Log',
            filters={'ticket_id': ticket_id},
            fields=[
                'name', 'svr_number', 'date', 'status', 'priority',
                'zone', 'property', 'unit', 'contract_number', 'tenant_name',
                'service_category', 'assigned_to', 'work_done_by', 'remarks',
                'supervisor_inspection_required', 'creation', 'modified', 'modified_by'
            ],
            order_by='creation desc'
        )
        
        # Fetch tags for each SVR log
        for log in svr_logs:
            tags = frappe.get_all(
                'EPFM Maintenance Log Tag',
                filters={'parent': log.name},
                fields=['tag'],
                pluck='tag'
            )
            log['tags'] = tags
        
        return svr_logs
        
    except Exception as e:
        frappe.logger().error(f"Error fetching SVR logs for ticket {ticket_id}: {str(e)}")
        frappe.log_error(f"Error fetching SVR logs for ticket: {str(e)}")
        return []


@frappe.whitelist()
def get_previous_ticket_history(email, current_ticket_id=None):
    """
    Get all tickets raised by a specific email address, excluding the current ticket.

    Args:
        email: The email address (raised_by field)
        current_ticket_id: The current ticket to exclude

    Returns:
        List of tickets with key details
    """
    if not email:
        return []

    try:
        filters = {"raised_by": email}
        if current_ticket_id:
            filters["name"] = ("!=", current_ticket_id)

        tickets = frappe.get_all(
            "HD Ticket",
            filters=filters,
            fields=[
                "name",
                "subject",
                "status",
                "status_category",
                "priority",
                "ticket_type",
                "agent_group",
                "contact",
                "property",
                "unit",
                "creation",
                "resolution_date",
                "svr_log_id",
                "is_merged",
            ],
            order_by="creation desc",
            limit=50,
        )

        return tickets

    except Exception as e:
        frappe.log_error(f"Error fetching previous ticket history for {email}: {str(e)}")
        return []
