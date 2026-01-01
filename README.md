# Kidematics Sign Up Checker

This project contains a Python script that checks the Kidematics "Before and After School" page for a new sign-up link. If the link has changed, it sends an email notification.

The script is designed to be deployed as a serverless function on Vercel and run as a cron job.

## Setup and Deployment

1.  **Push to Git:** Push this project to a Git repository (e.g., on GitHub).

2.  **Import to Vercel:** Import your Git repository into Vercel.

3.  **Configure Environment Variables:** In your Vercel project settings, add the following environment variables:

    *   `URL`: The URL of the website to check.
    *   `EXPECTED_URL`: The URL that the sign-up link is expected to point to.
    *   `SENDER_EMAIL`: The email address you want to send the notification from (e.g., your Gmail address).
    *   `RECEIVER_EMAILS`: A comma-separated list of email addresses you want to send the notification to (e.g., `email1@example.com,email2@example.com`).
    *   `SMTP_USERNAME`: Your email provider’s SMTP username (often the same as your sender email address).
    *   `SMTP_PASSWORD`: Your email provider’s SMTP password. **Important:** If you are using Gmail, you’ll need to generate an “App Password” to use here. You can find instructions on how to do that in Google’s help documentation.

4.  **Deploy:** Vercel will automatically deploy your project. The cron job defined in `vercel.json` will run the `api/check_link.py` script every 6 hours.