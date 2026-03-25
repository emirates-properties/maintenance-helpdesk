# Helpdesk Customizations

## Overview
This is a customized version of **Frappe Helpdesk** built for **PMS (Property Management System)**. It extends the standard helpdesk with SVR (Service Visit Report) integration and ticket history tracking tied to EPFM maintenance logs.

---

## Changes Made

### 1. SVR (Service Visit Report) Integration

**Backend** — `helpdesk/api/svr.py`
- `create_svr_log` — Creates a new EPFM Maintenance Log and links it to the ticket
- `get_svr_log` — Fetches a single SVR log by document name
- `update_svr_log` — Updates fields on an existing SVR log
- `get_ticket_svr_logs` — Returns all SVR logs linked to a ticket
- `get_previous_ticket_history` — Returns all previous tickets raised by the same customer email (excluding the current ticket)

**Frontend Components** — `desk/src/components/ticket-agent/`
- `CreateSVRModal.vue` — Modal to create a new SVR log from the ticket. Supports paste-to-parse (auto-fill from formatted SVR text) and manual entry
- `AssignSVRModal.vue` — Modal to link an existing SVR log to the ticket by SVR number
- `TicketSVRDetails.vue` — Tab panel showing all SVR logs linked to the current ticket with full details
- `TicketPreviousHistory.vue` — Tab panel showing all previous tickets from the same customer email

**Ticket Header** — `TicketHeader.vue`
- Added "Quick SVR Log" button — opens `CreateSVRModal`
- Added "Assign SVR" button — opens `AssignSVRModal`

---

### 2. Activity Panel Tabs

**`TicketActivityPanel.vue`** — Two new tabs added alongside the default Activity / Emails / Comments tabs:

| Tab | Component | Description |
|-----|-----------|-------------|
| SVR Details | `TicketSVRDetails.vue` | Shows linked EPFM maintenance logs |
| Ticket History | `TicketPreviousHistory.vue` | Shows previous tickets by the same customer |

---

### 3. Ticket Fields Used

The following custom fields were added to **HD Ticket**:
- `svr_log_id` — Link to EPFM Maintanace Log
- `property` — Link to PM Property
- `contract_no` — Contract number
- `unit` — Link to PM Unit
- `tenant_id` — Tenant identifier

---

## EPFM Maintenance Log (SVR) Fields

| Field | Type | Description |
|-------|------|-------------|
| `svr_number` | Data | The SVR reference number |
| `ticket_id` | Link (HD Ticket) | Linked helpdesk ticket |
| `date` | Date | Date of the visit |
| `property` | Link (PM Property) | Property |
| `unit` | Link (PM Unit) | Unit number |
| `zone` | Link | Zone |
| `tenant_name` | Data | Tenant name |
| `contract_number` | Data | Contract number |
| `service_category` | Link | Type of service |
| `status` | Select | OPEN / ASSIGNED / INPROGRESS / COMPLETED / RESOLVED / HOLD / etc. |
| `priority` | Select | Low / Medium / High / Urgent |
| `assigned_to` | Link (User) | Assigned technician |
| `work_done_by` | Select | EPFM or third party |
| `remarks` | Text Editor | Notes / remarks |
| `supervisor_inspection_required` | Check | Flag for supervisor inspection |
| `tags` | Table MultiSelect | Searchable tags |

---

## Environment Variables

In `desk/.env` (create if not present):

```
VITE_EPFM_URL=http://your-epfm-domain.com
```

Used to build the "View Full SVR" link in `TicketSVRDetails`. If empty, uses the same domain.

---

## Future Improvements (To-Do)

- [ ] Add edit/update SVR log directly from the SVR Details tab
- [ ] Add status filter/search in Ticket History tab
- [ ] Show SVR count badge on the SVR Details tab label
- [ ] Pagination for Ticket History (currently limited to 50)
- [ ] Email notification when SVR is assigned or status changes
- [ ] Mobile view support for SVR Details and Ticket History tabs
