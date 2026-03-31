"""AI-powered reply generation for helpdesk tickets using Google Generative AI."""

import frappe
from frappe import _
from google import genai
from google.genai import types

from helpdesk.utils import agent_only


@frappe.whitelist()
@agent_only
def generate_reply_suggestions(ticket_id: str, tone: str = "professional", user_input: str = ""):
	"""
	Generate AI-powered reply suggestions for a ticket.
	
	Args:
		ticket_id: ID of the HD Ticket
		tone: Tone of the reply - professional, friendly, concise, or detailed
		user_input: Optional additional context or instructions from the agent
	
	Returns:
		dict: Contains suggestions list and metadata
	"""
	# Validate inputs
	if not ticket_id:
		frappe.throw(_("Ticket ID is required"))
	
	valid_tones = ["professional", "friendly", "concise", "detailed"]
	if tone.lower() not in valid_tones:
		frappe.throw(_("Invalid tone. Must be one of: {0}").format(", ".join(valid_tones)))
	
	# Check if AI features are enabled
	settings = frappe.get_single("HD Settings")
	if not settings.enable_ai_features:
		frappe.throw(_("AI features are not enabled. Please enable them in HD Settings."))
	
	if not settings.google_ai_api_key:
		frappe.throw(_("Google AI API key is not configured. Please add it in HD Settings."))
	
	# Get ticket context
	try:
		ticket = frappe.get_doc("HD Ticket", ticket_id)
	except frappe.DoesNotExistError:
		frappe.throw(_("Ticket {0} not found").format(ticket_id))
	
	# Get the last customer communication
	last_customer_message = get_last_customer_communication(ticket_id)
	
	if not last_customer_message:
		frappe.throw(_("No customer communication found for this ticket"))
	
	# Generate AI suggestions
	try:
		# Debug logging
		frappe.logger().info(f"AI Reply Generation - Ticket: {ticket_id}, Tone: {tone}, User Input: '{user_input}'")
		
		suggestions = generate_ai_suggestions(
			settings,
			ticket.subject,
			ticket.description or "",
			last_customer_message,
			tone.lower(),
			user_input
		)
		
		return {
			"success": True,
			"suggestions": suggestions,
			"ticket_id": ticket_id,
			"tone": tone
		}
	except Exception as e:
		error_message = str(e)
		frappe.log_error(
			message=error_message,
			title=f"AI Reply Generation Error - Ticket {ticket_id}"
		)
		
		# Check for rate limit errors
		if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message or "quota" in error_message.lower():
			frappe.throw(
				_("AI quota exceeded. Please wait a few minutes and try again, or upgrade your Google AI API plan for higher limits.")
			)
		elif "404" in error_message or "NOT_FOUND" in error_message:
			frappe.throw(
				_("AI model not found. Please contact your administrator to check the configuration.")
			)
		else:
			frappe.throw(
				_("Failed to generate AI suggestions. Please try again or contact support if the issue persists.")
			)


def get_last_customer_communication(ticket_id: str) -> str:
	"""Get the last communication from the customer for a ticket."""
	from frappe.query_builder import Order
	
	Communication = frappe.qb.DocType("Communication")
	
	query = (
		frappe.qb.from_(Communication)
		.select(Communication.content)
		.where(Communication.reference_doctype == "HD Ticket")
		.where(Communication.reference_name == ticket_id)
		.where(Communication.sent_or_received == "Received")
		.where(Communication.communication_type == "Communication")
		.orderby(Communication.creation, order=Order.desc)
		.limit(1)
	)
	
	result = query.run(as_dict=True)
	
	if result:
		return result[0].content or ""
	
	# If no communication found, use ticket description as fallback
	ticket = frappe.get_doc("HD Ticket", ticket_id)
	return ticket.description or ""


def generate_ai_suggestions(
	settings,
	subject: str,
	description: str,
	last_message: str,
	tone: str,
	user_input: str = ""
) -> list[dict]:
	"""
	Generate reply suggestions using Google Generative AI.
	
	Args:
		settings: HD Settings document object
		subject: Ticket subject
		description: Ticket description
		last_message: Last customer message
		tone: Desired tone of response
		user_input: Optional additional context from the agent
	
	Returns:
		list: List of suggestion dictionaries with text and tone
	"""
	# Initialize Google AI client
	api_key = settings.get_password("google_ai_api_key")
	client = genai.Client(api_key=api_key)
	
	# Load tone-specific instructions from settings
	tone_instructions = {
		"professional": settings.ai_tone_professional or "Write in a professional, formal tone. Be courteous and maintain business etiquette. Keep it concise (2-3 short paragraphs).",
		"friendly": settings.ai_tone_friendly or "Write in a warm, friendly tone. Be approachable and personable while remaining helpful. Keep it brief (2-3 short paragraphs).",
		"concise": settings.ai_tone_concise or "Write a very brief response. Maximum 3-4 sentences. Get straight to the point.",
		"detailed": settings.ai_tone_detailed or "Write a thorough response with clear explanations. Use 3-4 paragraphs with actionable steps."
	}
	
	# Load general instructions from settings
	general_instructions = settings.ai_general_instructions or """- Address the customer's main concern directly
- Be empathetic and solution-oriented
- Keep it SHORT and professional (max 150 words per reply)
- Do NOT include URLs, links, or long tracking IDs
- Do NOT include email signatures, greetings like "Dear Customer", or closings like "Best regards"
- Start directly with the response content
- Each reply should offer a slightly different approach"""
	
	# Construct the prompt
	prompt = f"""You are a professional customer support agent. Generate 3 concise email reply suggestions for this support ticket.

Ticket Subject: {subject}

Last Customer Message:
{last_message}

Instructions:
- {tone_instructions.get(tone, tone_instructions["professional"])}
{general_instructions}
"""
	
	# Add user input if provided
	if user_input and user_input.strip():
		prompt += f"\n\nAgent's Additional Context:\n{user_input.strip()}\n"
		frappe.logger().info(f"AI Reply - User input added to prompt: '{user_input.strip()}'")
	else:
		frappe.logger().info("AI Reply - No user input provided")
	
	prompt += "\nGenerate exactly 3 distinct reply options, numbered 1-3."
	
	# Debug: Log the full prompt
	frappe.logger().info(f"AI Reply - Full Prompt:\n{prompt}")
	
	# Generate responses using Google AI
	response = client.models.generate_content(
		model="gemini-2.5-flash",
		contents=prompt,
		config=types.GenerateContentConfig(
			temperature=0.8,  # Higher temperature for more variation
			top_p=0.95,
			top_k=40,
			max_output_tokens=2048,
		)
	)
	
	# Parse and format the response
	suggestions = parse_ai_response(response.text, tone)
	
	return suggestions


def parse_ai_response(response_text: str, tone: str) -> list[dict]:
	"""
	Parse the AI response and format it into structured suggestions.
	
	Args:
		response_text: Raw text from AI
		tone: The tone used for generation
	
	Returns:
		list: List of formatted suggestions
	"""
	suggestions = []
	
	# Split response into separate suggestions
	# The AI typically separates responses with numbering or clear breaks
	parts = response_text.split("\n\n")
	
	# Filter and clean up the parts
	cleaned_parts = []
	current_suggestion = []
	
	for part in parts:
		stripped = part.strip()
		if not stripped:
			continue
		
		# Check if this is a new numbered item (1., 2., 3. or **1.**, etc.)
		if (stripped[0].isdigit() and len(stripped) > 1 and stripped[1] in ".):") or \
		   ("**1" in stripped[:5] or "**2" in stripped[:5] or "**3" in stripped[:5]):
			if current_suggestion:
				cleaned_parts.append("\n\n".join(current_suggestion))
				current_suggestion = []
			# Remove the numbering
			cleaned = stripped.split(".", 1)[-1].strip()
			cleaned = cleaned.replace("**", "").strip()
			current_suggestion.append(cleaned)
		else:
			current_suggestion.append(stripped)
	
	# Add the last suggestion
	if current_suggestion:
		cleaned_parts.append("\n\n".join(current_suggestion))
	
	# Format as suggestion objects
	for i, text in enumerate(cleaned_parts[:3], 1):  # Limit to 3 suggestions
		if text:
			suggestions.append({
				"id": i,
				"text": text,
				"tone": tone.capitalize()
			})
	
	# Ensure we have at least one suggestion
	if not suggestions and response_text:
		suggestions.append({
			"id": 1,
			"text": response_text.strip(),
			"tone": tone.capitalize()
		})
	
	return suggestions
