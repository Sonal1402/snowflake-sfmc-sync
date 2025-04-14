import snowflake.connector
import requests
import json

# === CONFIGURATION ===
SNOWFLAKE_USER = 'sonal'
SNOWFLAKE_PASSWORD = 'M9S7zKZ6SsfZn48'
SNOWFLAKE_ACCOUNT = 'uxmqipy-ys97690'  # Replace with your Snowflake account name (e.g., ab12345.us-east-1)
SNOWFLAKE_DATABASE = 'test_sfmc_integration'
SNOWFLAKE_SCHEMA = 'DEMO'
SNOWFLAKE_WAREHOUSE = 'COMPUTE_WH'

SFMC_CLIENT_ID = 'yjb9g127h8qu9uw6wkyvywtu'
SFMC_CLIENT_SECRET = 'PAGtyh1X0iVNXocA3Ybi36fg'  # Make sure this is correct
SFMC_AUTH_BASE = 'https://mcg68snys52lv7t1xd970936rtp4.auth.marketingcloudapis.com'
SFMC_REST_BASE = 'https://mcg68snys52lv7t1xd970936rtp4.rest.marketingcloudapis.com'

DATA_EXTENSION_KEY = 'snowflake_contacts'  # You must set this!

# === Step 1: Connect to Snowflake and read data ===
def get_snowflake_data():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    cur = conn.cursor()
    cur.execute("SELECT email, first_name, last_name FROM contacts")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convert to list of dictionaries
    data = []
    for row in rows:
        data.append({
            "keys": {
                "email": row[0]
            },
            "values": {
                "first_name": row[1],
                "last_name": row[2]
            }
        })
    return data

# === Step 2: Get SFMC access token ===
def get_access_token():
    url = f"{SFMC_AUTH_BASE}/v2/token"
    headers = {"Content-Type": "application/json"}
    payload = {
        "grant_type": "client_credentials",
        "client_id": SFMC_CLIENT_ID,
        "client_secret": SFMC_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['access_token']

# === Step 3: Push data to SFMC Data Extension ===
def send_to_data_extension(access_token, data):
    url = f"{SFMC_REST_BASE}/hub/v1/dataevents/key:{DATA_EXTENSION_KEY}/rowset"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 202:
        print("✅ Data successfully pushed to SFMC.")
    else:
        print("❌ Failed to push data.")
        print(response.status_code, response.text)

# === Main Script ===
if __name__ == '__main__':
    print("🔄 Reading data from Snowflake...")
    contacts = get_snowflake_data()
    print(f"📦 {len(contacts)} records fetched.")

    print("🔐 Authenticating with SFMC...")
    token = get_access_token()

    print("🚀 Sending data to SFMC Data Extension...")
    send_to_data_extension(token, contacts)
