import requests
import base64
from datetime import datetime
from requests.auth import HTTPBasicAuth

def get_access_token():
    # 1. Put your real keys back in here!
    consumer_key = 'n6nkzqwhhrKcICKTsua1O7hFdnNZC76yGfn3P3T6bRxgVIyQ'
    consumer_secret = 'paorugAtzqGynK6QFlQshJSykb7BxHZHszINa1cDyFLx4Vttb38UTEsAZ0Y8dkdS'
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    try:
        response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        return response.json()['access_token']
    except Exception as e:
        print("Error getting token:", e)
        return None

def trigger_stk_push(phone_number, amount):
    access_token = get_access_token()
    if not access_token:
        print("Could not get access token, stopping.")
        return

    # 2. Safaricom Sandbox Test Variables
    business_shortcode = '174379'
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    
    # 3. Generate the current time (YearMonthDayHourMinuteSecond)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # 4. Create the encrypted password
    password_string = business_shortcode + passkey + timestamp
    password = base64.b64encode(password_string.encode('utf-8')).decode('utf-8')
    
    # 5. Set up the STK Push Request
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 6. The actual data being sent to the buyer's phone
    payload = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://kt8b8msj-8000.uks1.devtunnels.ms/callback/", # A dummy URL for testing
        "AccountReference": "Shoe Store Order",
        "TransactionDesc": "Paying for Shoes"
    }
    
    # 7. Fire the request!
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response_data = response.json()
        print("Safaricom says:", response_data)
        return response_data  # <-- We must hand the data back to views.py!
    except Exception as e:
        print("Oops, the push failed:", e)
        return None           # <-- Hand back None if it crashes

# --- RUN IT HERE ---
# Replace with YOUR actual Safaricom phone number (Must start with 254, no plus sign!)
