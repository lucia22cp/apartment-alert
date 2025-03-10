from twilio.rest import Client
import os

# Load Twilio credentials from environment variables
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")

if not TWILIO_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER or not RECIPIENT_PHONE_NUMBER:
    raise ValueError("Twilio credentials not set properly.")

# Create Twilio client
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Send a test message
message = client.messages.create(
    body="🚀 Twilio Test Message: Your script is working!",
    from_=TWILIO_PHONE_NUMBER,
    to=RECIPIENT_PHONE_NUMBER
)

print(f"✅ Test SMS sent! Message SID: {message.sid}")
