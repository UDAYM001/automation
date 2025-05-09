from playwright.sync_api import sync_playwright
from imapclient import IMAPClient
import pyzmail
import re
import time

# Fetch OTP from IONOS Webmail using IMAP
def get_latest_otp_ionos(email, password, retries=5, wait_sec=5):
    server = 'imap.ionos.com'  # IONOS IMAP server

    with IMAPClient(host=server, ssl=True) as client:
        client.login(email, password)
        client.select_folder('INBOX')

        for attempt in range(retries):
            print(f"📬 Checking for OTP email (Attempt {attempt + 1}/{retries})...")
            messages = client.search(['UNSEEN'])

            for uid in reversed(messages):  # newest first
                raw_message = client.fetch([uid], ['BODY[]', 'FLAGS'])
                message = pyzmail.PyzMessage.factory(raw_message[uid][b'BODY[]'])

                subject = message.get_subject()
                from_email = message.get_addresses('from')[0][1]

                if message.text_part:
                    body = message.text_part.get_payload().decode(message.text_part.charset)
                elif message.html_part:
                    body = message.html_part.get_payload().decode(message.html_part.charset)
                else:
                    continue

                otp_match = re.search(r'\b\d{6}\b', body)
                if otp_match:
                    print(f"✅ OTP found: {otp_match.group(0)}")
                    return otp_match.group(0)

            time.sleep(wait_sec)

    print("❌ OTP not found in email.")
    return None


def run_login():
    user_id = "mca@hiisight.com"
    password = "March@2025"

    email_address = "code@hiisight.com"
    email_password = "Ravi@1443101"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            accept_downloads=True,  # ✅ Enable download permission
            viewport={'width': 1920, 'height': 1080},
            screen={'width': 1920, 'height': 1080}
        )

        page = context.new_page()

        # Step-by-step login
        page.goto("https://www.providerportal.com/")
        page.wait_for_selector('#asPrimary_ctl00_txtLoginId')
        page.fill('#asPrimary_ctl00_txtLoginId', user_id)
        page.click('#asPrimary_ctl00_btnLookup')
        page.wait_for_selector('input.button.button-primary[type="submit"][value="Next"]', timeout=15000)
        page.click('input.button.button-primary[type="submit"][value="Next"]')
        page.wait_for_selector('#input60', timeout=15000)
        page.fill('#input60', password)
        page.click('input.button.button-primary[type="submit"][value="Login"]')
        page.wait_for_selector('input.button.button-primary[type="submit"][value="Send Email"]', timeout=15000)
        page.click('input.button.button-primary[type="submit"][value="Send Email"]')

        # Get OTP
        print("📧 Waiting for OTP email...")
        page.wait_for_timeout(10000)
        otp = get_latest_otp_ionos(email_address, email_password)
        if not otp:
            print("❌ Could not retrieve OTP. Exiting.")
            return

        # Enter OTP
        page.wait_for_selector('#input103', timeout=15000)
        page.fill('#input103', otp)
        page.click('input.button.button-primary[type="submit"][value="Verify Code"]')

        # Wait for dashboard to load
        print("✅ OTP Verified. Waiting for dashboard to load...")
        page.wait_for_timeout(5000)

        # ⬇️ Multiple downloads
        print("✅ Login complete. Starting repeated downloads...")
        download_count = 25  # 🔁 Number of times to download

        for i in range(download_count):
            try:
                print(f"📥 Starting download {i + 1}/{download_count}...")
                with page.expect_download() as download_info:
                    page.click("button#download")  # ⬅️ Replace with actual button selector

                download = download_info.value
                saved_path = download.path()
                print(f"✅ Download {i + 1} completed: {saved_path}")

                time.sleep(90000)  # Optional wait between downloads
            except Exception as e:
                print(f"❌ Download {i + 1} failed: {e}")

        print("✅ All downloads complete. Browser will stay open for 8 hours...")
        time.sleep(28800)

        context.close()
        browser.close()

if __name__ == "__main__":
    run_login()
