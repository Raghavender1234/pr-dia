# In backend/app/utils/email_utils.py

import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from flask import current_app

def send_email(to_email, subject, html_content):
    """
    Sends an email using the Brevo API.
    """
    # 1. Get credentials from your .env file
    api_key = os.getenv('BREVO_API_KEY')
    from_email_address = os.getenv('MAIL_SENDER_ADDRESS')

    if not api_key or not from_email_address:
        current_app.logger.error("Brevo API Key or From Email is not configured.")
        return False

    # 2. Configure the Brevo API client
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # 3. Define the sender and recipient
    sender = sib_api_v3_sdk.SendSmtpEmailSender(email=from_email_address, name=os.getenv('APP_NAME', 'OpenLMS'))
    to = [sib_api_v3_sdk.SendSmtpEmailTo(email=to_email)]

    # 4. Create the email object with all the details
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject=subject,
        html_content=html_content
    )

    # 5. Send the email and handle any errors
    try:
        api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        current_app.logger.error(f"Brevo API Exception when sending email: {e}\n")
        return False