
import requests
import json
import time
from playwright.sync_api import sync_playwright
import requests as telegram_requests

# === Konfigurasi VirtuSIM ===
VIRTUSIM_API_KEY = "e2c10e6b0cbdd79df774ff5d9798cfe4"
SERVICE_ID = "26"
OPERATOR = "any"

# === Telegram Config ===
TELEGRAM_BOT_TOKEN = "5896875051:AAGbybqq0hEJpXxSVV2KgTjqSLXnD-A_WJk"
TELEGRAM_CHAT_ID = "5250069585"

def send_to_telegram(account_data):
    message = f"""
🎉 TikTok Account Created!

📱 Phone: {account_data["phone"]}
🔑 OTP: {account_data["otp"]}
👤 Username: {account_data["username"]}
🔒 Password: {account_data["password"]}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    telegram_requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    })

def get_virtual_number():
    url = "https://virtusim.com/api/json.php"
    params = {
        "api_key": VIRTUSIM_API_KEY,
        "action": "order",
        "service": SERVICE_ID,
        "operator": OPERATOR
    }
    response = requests.get(url, params=params).json()
    if response.get("status"):
        return response["data"]["id"], response["data"]["number"]
    else:
        raise Exception(f"Gagal order nomor: {response}")

def wait_for_sms(order_id, timeout=120):
    url = "https://virtusim.com/api/json.php"
    for i in range(timeout):
        params = {
            "api_key": VIRTUSIM_API_KEY,
            "action": "getcode",
            "id": order_id
        }
        response = requests.get(url, params=params).json()
        if response.get("status") and response["data"].get("code"):
            return response["data"]["code"]
        time.sleep(5)
    raise Exception("Timeout: Tidak menerima OTP")

def save_account(data):
    with open("accounts.json", "a") as f:
        json.dump(data, f)
        f.write("\n")

def register_tiktok(phone_number, otp_code):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.tiktok.com/signup/phone-or-email", timeout=60000)
        time.sleep(5)

        try:
            page.get_by_text("Use phone or email", exact=True).click(timeout=10000)
        except:
            print("❗ Tidak menemukan tombol 'Use phone or email'")

        try:
            page.get_by_text("Phone", exact=True).click(timeout=10000)
        except:
            print("❗ Tab Phone tidak ditemukan")

        page.locator('input[name="phone"]').fill(phone_number)
        page.get_by_role("button", name="Send code").click()
        page.wait_for_timeout(10000)

        otp_input = page.locator('input[name="code"]')
        otp_input.fill(otp_code)

        password = "Tiktok@1234"
        username = f"bot{int(time.time())}"
        page.locator('input[name="password"]').fill(password)
        page.locator('input[name="username"]').fill(username)
        page.wait_for_timeout(1000)

        try:
            page.get_by_role("button", name="Sign up").click(timeout=10000)
        except:
            print("❗ Tombol Sign up tidak ditemukan.")

        print("✅ Akun berhasil dicoba dibuat.")
        account_obj = {
            "phone": phone_number,
            "otp": otp_code,
            "username": username,
            "password": password
        }
        save_account(account_obj)
        send_to_telegram(account_obj)
        browser.close()

if __name__ == "__main__":
    try:
        order_id, phone = get_virtual_number()
        print(f"[+] Nomor diperoleh: {phone}")
        otp = wait_for_sms(order_id)
        print(f"[+] OTP diterima: {otp}")
        register_tiktok(phone, otp)
    except Exception as e:
        print(f"[!] Error: {e}")
