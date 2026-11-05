import urllib.request
import json
from uuid import uuid4

def test_all_mobile_features():
    print("==================================================")
    print("TESTING ALL AGROLENS FLUTTER FEATURES ON BACKEND")
    print("==================================================")

    # 1. Weather Feature
    print("\n[FEATURE 1] Weather Forecast Service:")
    url = "http://127.0.0.1:8000/api/v1/weather?location=Bengaluru&days=3"
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    weather_data = json.loads(resp.read().decode())
    assert "temperature_c" in weather_data
    assert "forecast" in weather_data
    print(f"  [OK] Location: {weather_data['location']['name']}, Temp: {weather_data['temperature_c']}°C, Provider: {weather_data['provider']}")
    print(f"  [OK] Daily Forecast days returned: {len(weather_data['forecast'])}")

    # 2. Government Schemes Feature
    print("\n[FEATURE 2] Government Agricultural Schemes Service:")
    url = "http://127.0.0.1:8000/api/v1/schemes"
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    schemes_data = json.loads(resp.read().decode())
    print(f"  [OK] Schemes endpoint reachable, Total in DB: {schemes_data['total']}")

    # 3. Agriculture News Feature
    print("\n[FEATURE 3] PIB / Agriculture News Service:")
    url = "http://127.0.0.1:8000/api/v1/news"
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    news_data = json.loads(resp.read().decode())
    print(f"  [OK] News endpoint reachable, Total articles: {news_data['total']}")

    # 4. Mandi Market Prices Feature
    print("\n[FEATURE 4] Mandi Live Market Prices Service:")
    url = "http://127.0.0.1:8000/api/v1/market/prices?commodity=Tomato"
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    mandi_data = json.loads(resp.read().decode())
    print(f"  [OK] Mandi price endpoint reachable, Total records: {mandi_data['total']}")

    # 5. Mobile User Registration, Login & Session Authentication
    print("\n[FEATURE 5] Mobile Farmer Authentication & Session Management:")
    username = f"farmer_{str(uuid4())[:6]}"
    email = f"{username}@agrolens.in"
    password = "FarmerPass2026!"
    
    # Register
    reg_payload = json.dumps({"username": username, "email": email, "password": password}).encode("utf-8")
    req_reg = urllib.request.Request("http://127.0.0.1:8000/api/v1/auth/register", data=reg_payload, headers={"Content-Type": "application/json"})
    resp_reg = urllib.request.urlopen(req_reg)
    reg_res = json.loads(resp_reg.read().decode())
    token = reg_res["access_token"]
    print(f"  [OK] Registered account '{username}' successfully (Status {resp_reg.status}).")
    
    # Authenticated /me endpoint
    req_me = urllib.request.Request("http://127.0.0.1:8000/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    resp_me = urllib.request.urlopen(req_me)
    me_res = json.loads(resp_me.read().decode())
    assert me_res["username"] == username
    print(f"  [OK] Session authenticated via Bearer token: User ID = {me_res['user_id']}, Email = {me_res['email']}")

    # Logout
    req_logout = urllib.request.Request("http://127.0.0.1:8000/api/v1/auth/logout", data=b"{}", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    resp_logout = urllib.request.urlopen(req_logout)
    print(f"  [OK] Logged out successfully (Status {resp_logout.status}).")

    print("\n==================================================")
    print("ALL FLUTTER FEATURES WORKING PERFECTLY ON BACKEND!")
    print("==================================================")

if __name__ == "__main__":
    test_all_mobile_features()
