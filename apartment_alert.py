import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import json
import os
import googlemaps
from datetime import datetime

import os
from twilio.rest import Client

# Load Twilio credentials from environment variables
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEYI")
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("Google Maps API key not set.")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# File for seen listings
SEEN_LISTINGS_FILE = "seen_listings.json"

# Apartment search URLs
URLS = [
    "https://wahlinfastigheter.se/lediga-objekt/lagenheter/",
    "https://bostad.stockholm.se/bostad?s=58.64265&n=60.02370&w=16.07849&e=19.55017&hide-filter=true&sort=annonserad-fran-desc"
]

# Slussen Götgatan location
SLUSSEN_COORDINATES = (59.3180483, 18.0715148)

# Google Maps Client
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

# Function to load seen listings
def load_seen_listings():
    try:
        with open(SEEN_LISTINGS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Function to save seen listings
def save_seen_listings(seen_listings):
    with open(SEEN_LISTINGS_FILE, "w") as f:
        json.dump(seen_listings, f)

# Function to check public transport time
def is_within_travel_limit(address):
    now = datetime.now().replace(hour=8, minute=0)  # Monday at 8:00 AM
    directions = gmaps.directions(address, SLUSSEN_COORDINATES, mode="transit", departure_time=now)
    
    if directions:
        duration_sec = directions[0]['legs'][0]['duration']['value']
        return duration_sec / 60 <= 40  # Convert to minutes
    return False

# Scrape apartment listings
def scrape_listings():
    listings = []
    
    for url in URLS:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        for listing in soup.select(".list-item"):
            title = listing.select_one(".listing-title").text.strip()
            link = "https://bostad.stockholm.se" + listing.select_one("a")["href"]
            price_text = listing.select_one(".listing-price").text.strip()
            price = int("".join(filter(str.isdigit, price_text)))

            # Get apartment location
            address = listing.select_one(".listing-address").text.strip()

            # Filter by price and distance
            if price <= 8000 and is_within_travel_limit(address):
                listings.append((title, link, price))

    return listings

# Send SMS
def send_sms(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=RECIPIENT_PHONE_NUMBER
    )

# Main function
def main():
    seen_listings = load_seen_listings()
    new_listings = scrape_listings()

    unseen_listings = [listing for listing in new_listings if listing[1] not in seen_listings]

    if unseen_listings:
        for title, link, price in unseen_listings:
            message = f"New Apartment Listing: {title}\nPrice: {price} SEK\n{link}"
            send_sms(message)
            print(f"SMS sent for {title}")

        seen_listings.extend([listing[1] for listing in unseen_listings])
        save_seen_listings(seen_listings)

if __name__ == "__main__":
    main()
