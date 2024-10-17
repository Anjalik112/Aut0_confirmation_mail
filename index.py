from flask import Flask, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os

# Initialize Flask app
app = Flask(__name__)

# Email sender details (use environment variables for sensitive data)
sender_email = os.getenv("SENDER_EMAIL", "ignitestudentassociation@gmail.com")
sender_password = os.getenv("SENDER_PASSWORD", "dyxk yajp vcdv fkwd")

# Define email body templates and corresponding links for different events
event_details = {
    "Test-Event": {
        "body": "Congratulations {recipient_name} 🥳,\n\n Here is your confirmation email for successful registration in {event} at EventZen3.0! We are happy to say that the competitions you've taken part in are successfully registered. You can visit our Website for more details and guidelines on competitions. The clock is ticking, hurry up!\nYou can submit your work here: {join_link} \nMake sure to submit before the deadline!\nJoin the Whatsapp group link: {whatsapp_link} \n\nSee you soon!\n\nWe look forward to seeing your spark!\n\nSmokey regards,\nTeam Ignite 🔥",
        "join_link": "https://tinyurl.com/ignitephotographySubmission",
        "whatsapp_link": "https://chat.whatsapp.com/KcJngydTYXGLgDxlAhYzon",
    },
    "Aptitude-test": {
        "body": "Congratulations {recipient_name} 🥳,\n\n Here is your confirmation email for successful registration in {event} at EventZen3.0! We are happy to say that the competitions you've taken part in are successfully registered. You can visit our Website for more details and guidelines on competitions. The clock is ticking, hurry up!\nYou can submit your work here: {join_link} \nMake sure to submit before the deadline!\nJoin the Whatsapp group link: {whatsapp_link} \n\nSee you soon!\n\nWe look forward to seeing your spark!\n\nSmokey regards,\nTeam Ignite 🔥",
        "join_link": "https://exam.net",
        "whatsapp_link": "https://chat.whatsapp.com/CbILR7JRn3FBOGxiInOB69",
    },
    "Prompt-Competition": {
        "body": "Congratulations {recipient_name} 🥳,\n\n Here is your confirmation email for successful registration in {event} at EventZen3.0! We are happy to say that the competitions you've taken part in are successfully registered. You can visit our Website for more details and guidelines on competitions. The clock is ticking, hurry up!\nYou can submit your work here: {join_link} \nMake sure to submit before the deadline!\nJoin the Whatsapp group link: {whatsapp_link} \n\nSee you soon!\n\nWe look forward to seeing your spark!\n\nSmokey regards,\nTeam Ignite 🔥",
        "join_link": "https://tinyurl.com/ignitePromptSubmission",
        "whatsapp_link": "https://chat.whatsapp.com/KcJngydTYXGLgDxlAhYzon",
    },
    # Other event details go here...
}

# Map cf_form_id to event names
event_mapping = {
    "50520622": "Test-Event",
    "50507317": "Aptitude-test",
    "50507297": "Prompt-Competition",
    "50506013": "Photography-Competition",
    "50507273": "Poster-Competition",
    "50519628": "BGMI-Gaming",
    "50519775": "FreeFire-Gaming",
    "50519775": "Combo-Offer",
    # Add other mappings here as needed
}

# Function to send confirmation email
def send_confirmation_email(recipient_email, recipient_name, event):
    logging.info(f"Attempting to send email to {recipient_email} for event {event}")

    # Check if event exists in event_details
    event_info = event_details.get(event)
    
    if not event_info:
        logging.error(f"Event {event} not found in event details.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"EVENTZEN 3.0 - Confirmation of Registration for {event}"

    # Prepare the email body with the correct link and recipient name
    try:
        body_template = event_info.get('body')
        join_link = event_info.get('join_link', "")
        whatsapp_link = event_info.get('whatsapp_link', "")

        # Replace placeholders in the body with actual values
        body = body_template.format(
            recipient_name=recipient_name, 
            event=event, 
            join_link=join_link, 
            whatsapp_link=whatsapp_link
        )

        msg.attach(MIMEText(body, 'plain'))

        # Send email without SMTP debug output
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        logging.info(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}: {str(e)}")

# Webhook endpoint to receive payment success events
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        logging.error("Invalid data received in webhook")
        return jsonify({"status": "failed", "message": "Invalid data"}), 400

    logging.info(f"Received Webhook: {data}")

    # Check if this is a PAYMENT_SUCCESS_WEBHOOK event
    if data.get('type') == 'PAYMENT_SUCCESS_WEBHOOK':
        payment_details = data.get('data', {})
        customer_details = payment_details.get('customer_details', {})
        
        recipient_email = customer_details.get('customer_email')
        recipient_name = customer_details.get('customer_name')
        
        # Map cf_form_id to the event name
        event_id = payment_details.get('order', {}).get('order_tags', {}).get('cf_form_id')
        event = event_mapping.get(event_id)  # Use mapping

        # Validate that all required details are available
        if recipient_email and recipient_name and event:
            send_confirmation_email(recipient_email, recipient_name, event)
            return jsonify({"status": "success"}), 200
        else:
            logging.error("Missing recipient or event details")
            return jsonify({"status": "failed", "message": "Missing recipient or event details"}), 400

    return jsonify({"status": "ignored"}), 200

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    # Run the Flask server
    app.run(host='0.0.0.0', port=5000)
