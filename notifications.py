import requests
import time

# ---------------------- CONFIGURATION ----------------------
# List the token contract addresses you want to track.
# (These should be the contract addresses for the tokens you consider "fresh.")
TOKEN_CONTRACTS = [
    "UCYaUNhgB2344N8Qpg4t712V9RHahcpTCejwXKspump",  # replace with actual contract address
    "61V8vBaqAGMpgDQi4JcAwo1dmBGHsyhzodcPqnEVpump",# add as many as needed
    "AxriehR6Xw3adzHopnvMn7GcpRFcD41ddpiTWMg6pump",
]

# Set your thresholds (in percentage) for triggering notifications.
# (Note: Using price change percentage as provided by DEX Screener)
INCREASE_THRESHOLD = 50  # e.g., if price increases by 50% or more
DROP_THRESHOLD = -30 # e.g., if price drops by 30% or more

# Pushbullet API configuration.
PUSHBULLET_API_KEY = "o.crkvejU5t8FCJDQzdeuPGOGPi2lODpCO"  # replace with your Pushbullet API key

# How often (in seconds) to check the token data.
CHECK_INTERVAL = 60  # e.g., every 5 minutes
# -----------------------------------------------------------

def send_pushbullet_message(api_key, title, body):
    """
    Sends a push notification via Pushbullet.
    """
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {
        "Access-Token": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "type": "note",
        "title": title,
        "body": body
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print("Error sending Pushbullet message:", response.text)
    except Exception as e:
        print("Exception sending Pushbullet message:", e)

def get_token_data(contract_address):
    """
    Retrieves token data from DEX Screener for the given contract address.
    """
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching token data for {contract_address}:", response.text)
            return None
    except Exception as e:
        print(f"Exception fetching token data for {contract_address}:", e)
        return None

def monitor_tokens():
    """
    Main loop: checks each token's data and sends Pushbullet notifications if thresholds are met.
    """
    while True:
        for contract in TOKEN_CONTRACTS:
            data = get_token_data(contract)
            if not data:
                continue

            pairs = data.get("pairs", [])
            if not pairs:
                print(f"No trading pairs found for contract {contract}.")
                continue

            # For simplicity, let's just use the first pair
            pair_data = pairs[0]

            # Extract token info from 'baseToken'
            base_token_info = pair_data.get("baseToken", {})
            token_name = base_token_info.get("name", "Unknown Token")
            token_symbol = base_token_info.get("symbol", "")

            # Extract the 24-hour price change
            price_change_data = pair_data.get("priceChange", {})
            # You can change 'h24' to 'h1' or another timeframe if you prefer
            price_change_value = price_change_data.get("h1")

            if price_change_value is None:
                print(f"No h1 price change data for {token_name} ({contract}).")
                continue

            # Convert the price change to a float
            try:
                price_change = float(price_change_value)
            except Exception as e:
                print(f"Error parsing price change for {token_name}: {e}")
                continue

            # Compare against thresholds
            message = None
            if price_change >= INCREASE_THRESHOLD:
                message = (f"🚀 {token_name} ({token_symbol}) increased by "
                           f"{price_change:.2f}% in the last 1h!")
            elif price_change <= DROP_THRESHOLD:
                message = (f"⚠️ {token_name} ({token_symbol}) dropped by "
                           f"{price_change:.2f}% in the last 1h!")

            # If thresholds met, send notification
            if message:
                print("Sending notification:", message)
                send_pushbullet_message(
                    PUSHBULLET_API_KEY,
                    f"Crypto Alert: {token_name}",
                    message
                )

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("Starting token monitor using DEX Screener API...")
    monitor_tokens()
