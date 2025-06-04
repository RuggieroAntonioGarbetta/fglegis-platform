import os
import requests


def invia_email_api_brevo(to_email, subject, content):
    headers = {
        "accept": "application/json",
        "api-key": os.environ.get("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": "FG LEGIS",
            "email": "noreply@fglegis.com"
        },
        "to": [{
            "email": to_email
        }],
        "subject": subject,
        "htmlContent": f"<p>{content}</p>"
    }

    response = requests.post("https://api.brevo.com/v3/smtp/email",
                             json=payload,
                             headers=headers)

    # Logging disabilitato temporaneamente per evitare errori di import
    # try:
    #     from .models import LogEmail
    #     LogEmail.objects.create(
    #         destinatario=to_email,
    #         oggetto=subject,
    #         contenuto=content,
    #         codice_risposta=response.status_code,
    #         risposta=str(response.json())
    #     )
    # except Exception as e:
    #     print(f"[EmailLogError] {e}")

    return response.status_code, response.json()
