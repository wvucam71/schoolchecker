import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

# --- Configuration ---
URL = os.environ.get("URL")
EXPECTED_URL_STR = os.environ.get("EXPECTED_URL")
EXPECTED_URLS = [url.strip() for url in EXPECTED_URL_STR.split(',')] if EXPECTED_URL_STR else []

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
RECEIVER_EMAILS = os.environ.get("RECEIVER_EMAILS", "").split(",")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD") # Use an App Password for Gmail

def send_email(original_url, found_link, final_url, link_changed):
    """Sends an email notification with details about the link check."""
    subject = ""
    body = ""

    if found_link is None:
        subject = f"Kidematics Sign Up: No Link Found on {original_url}"
        body = f"The scheduled check for Kidematics sign-up links on {original_url} did not find any sign-up link."
    elif link_changed:
        subject = f"Kidematics Sign Up OPEN: Link HAS Changed!"
        body = f"Kidematics Sign Up Open!\n\nThe original URL checked was: {original_url}\n" \
               f"The new sign-up link found is: {final_url}"
    else:
        subject = f"Kidematics Sign Up: Link Has NOT Changed"
        body = f"The scheduled check for Kidematics sign-up links on {original_url} found that " \
               f"the link has NOT changed.\n\n" \
               f"The current sign-up link is: {final_url}"

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = ", ".join(RECEIVER_EMAILS)

    print(f"Attempting to send email. Subject: {subject}")
    # print(f"Email Body:\n{body}") # For debugging

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAILS, message.as_string())
        print("Email notification sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_website():
    """Checks the website for a new sign-up link and sends email notification."""
    global URL # Ensure URL is accessed from module scope
    global EXPECTED_URLS # Ensure EXPECTED_URLS is accessed from module scope


    if not URL:
        print("Error: URL environment variable is not set.")
        send_email(original_url="N/A", found_link=None, final_url="N/A", link_changed=False)
        return

    page_content = None
    try:
        page = requests.get(URL, timeout=10)
        page.raise_for_status()  # Raise an exception for bad status codes
        page_content = page.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching website {URL}: {e}")
        send_email(original_url=URL, found_link=None, final_url="N/A", link_changed=False)
        return

    soup = BeautifulSoup(page_content, "html.parser")

    signup_link = None
    # Try to find the link in a few ways
    # 1. Look for a link with "Sign Up Here" string
    sign_up_text = soup.find(string="Sign Up Here")
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
        signup_nav = soup.find("a", string="Sign Up")
        if signup_nav and signup_nav.has_attr("href"):
            signup_link = signup_nav["href"]

    final_url = None
    link_has_changed = False

    if signup_link:
        # Follow redirects
        try:
            response = requests.head(signup_link, allow_redirects=True, timeout=10)
            final_url = response.url
            print(f"Found sign-up link: {signup_link}")
            print(f"Redirects to: {final_url}")

            if EXPECTED_URLS and final_url not in EXPECTED_URLS:
                print("Sign-up link has changed!")
                link_has_changed = True
            elif EXPECTED_URLS:
                print("Sign-up link is the same.")
            else:
                print("EXPECTED_URLS not set, cannot determine if link has changed.")

        except requests.exceptions.RequestException as e:
            print(f"Error following redirect for {signup_link}: {e}")
            send_email(original_url=URL, found_link=signup_link, final_url="N/A", link_changed=False)
            return
    else:
        print("Sign-up link not found on the page.")

    send_email(original_url=URL, found_link=signup_link, final_url=final_url, link_changed=link_has_changed)

def handler(request, response):
    check_website()
    response.status(200).send("Checked website.")