import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

# --- Configuration ---
URL = os.environ.get("URL")
EXPECTED_URL = os.environ.get("EXPECTED_URL")
SENDER_EMAIL = "your_email@gmail.com"
RECEIVER_EMAILS = ["receiver1@example.com", "receiver2@example.com"]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"  # Use an App Password for Gmail

def send_email(new_link):
    """Sends an email notification."""
    message = MIMEText(f"Kidematics Sign Up Open\n\nThe new sign-up link is: {new_link}")
    message["Subject"] = "Kidematics Sign Up Open"
    message["From"] = SENDER_EMAIL
    message["To"] = ", ".join(RECEIVER_EMAILS)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAILS, message.as_string())
    print("Email notification sent!")

def check_website():
    """Checks the website for a new sign-up link."""
    try:
        page = requests.get(URL, timeout=10)
        page.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching website: {e}")
        return

    soup = BeautifulSoup(page.content, "html.parser")

    # Try to find the link in a few ways
    signup_link = None
    # 1. Look for a link with "Sign Up Here" text
    sign_up_text = soup.find(text="Sign Up Here")
    if sign_up_text:
        parent_anchor = sign_up_text.find_parent("a")
        if parent_anchor and parent_anchor.has_attr("href"):
            signup_link = parent_anchor["href"]

    # 2. If not found, look for a google form link in the navigation
    if not signup_link:
        nav_link = soup.select_one('a[href*="docs.google.com/forms"]')
        if nav_link:
            signup_link = nav_link['href']

    # 3. If still not found, look for a "Sign Up" link in the main navigation
    if not signup_link:
        # This is a bit more brittle, might need adjustment if the site structure changes
        signup_nav = soup.find("a", text="Sign Up")
        if signup_nav and signup_nav.has_attr("href"):
            signup_link = signup_nav["href"]


    if signup_link:
        # Follow redirects
        try:
            response = requests.head(signup_link, allow_redirects=True, timeout=10)
            final_url = response.url
            print(f"Found sign-up link: {signup_link}")
            print(f"Redirects to: {final_url}")

            if final_url != EXPECTED_URL:
                print("Sign-up link has changed!")
                # send_email(final_url) # Uncomment to send emails
            else:
                print("Sign-up link is the same.")
        except requests.exceptions.RequestException as e:
            print(f"Error following redirect for {signup_link}: {e}")

    else:
        print("Sign-up link not found on the page.")

if __name__ == "__main__":
    check_website()