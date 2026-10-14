from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import time

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# ---------------- LOGIN ----------------

creds = None

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = build("gmail", "v1", credentials=creds)

# ---------------- FILTRO ----------------

QUERY = "before:2025/01/01"
# Ejemplos:
# QUERY = "category:promotions"
# QUERY = "from:facebookmail.com"
# QUERY = "older:2y"

eliminados = 0

print("Buscando correos...\n")

while True:

    respuesta = service.users().messages().list(
        userId="me",
        q=QUERY,
        maxResults=500
    ).execute()

    mensajes = respuesta.get("messages", [])

    if not mensajes:
        break

    for mensaje in mensajes:
        try:
            service.users().messages().trash(
                userId="me",
                id=mensaje["id"]
            ).execute()

            eliminados += 1

            if eliminados % 100 == 0:
                print(f"{eliminados} correos enviados a la papelera...")

        except Exception as e:
            print(f"Error con {mensaje['id']}: {e}")

        # Evita exceder el límite de solicitudes
        time.sleep(0.02)

print("\n--------------------------------")
print(f"Proceso terminado.")
print(f"Total eliminados: {eliminados}")