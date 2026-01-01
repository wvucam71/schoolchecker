import pytest
from unittest import mock
import os
import api.check_link # Import the module to patch its attributes

# Mock response for requests.get to simulate the website content
MOCK_WEBSITE_HTML = """
<html>
    <body>
        <nav>
            <a href="http://docs.google.com/forms/new-link">Sign Up Here</a>
        </nav>
        <p>Some other content</p>
    </body>
</html>
"""

# HTML content with no signup link
MOCK_WEBSITE_HTML_NO_LINK = """
<html>
    <body>
        <p>No sign up links here.</p>
    </body>
</html>
"""

def test_link_has_changed_triggers_email_with_new_args():
    """
    Tests that send_email is called with correct arguments when the final_url is different from EXPECTED_URL.
    """
    with mock.patch.object(api.check_link, 'URL', "http://mock-website.com"), \
         mock.patch.object(api.check_link, 'EXPECTED_URL', "http://old-signup-link.com/form"), \
         mock.patch.object(api.check_link, 'SENDER_EMAIL', "test@example.com"), \
         mock.patch.object(api.check_link, 'RECEIVER_EMAILS', ["recipient@example.com"]), \
         mock.patch.object(api.check_link, 'SMTP_USERNAME', "test@example.com"), \
         mock.patch.object(api.check_link, 'SMTP_PASSWORD', "password"), \
         mock.patch('requests.get') as mock_get, \
         mock.patch('requests.head') as mock_head, \
         mock.patch('api.check_link.send_email') as mock_send_email:

        # Configure mock_get to return our mock HTML
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = MOCK_WEBSITE_HTML
        mock_get.return_value.raise_for_status.return_value = None

        # Configure mock_head to return a new, different final URL
        new_final_url = "http://new-signup-link.com/form"
        mock_head.return_value.url = new_final_url
        mock_head.return_value.raise_for_status.return_value = None

        api.check_link.check_website() # Call the function from the module

        # Assert that requests.get was called
        mock_get.assert_called_once_with(api.check_link.URL, timeout=10)

        # Assert that requests.head was called with the found link
        mock_head.assert_called_once_with("http://docs.google.com/forms/new-link", allow_redirects=True, timeout=10)

        # Assert that send_email was called with the new arguments
        mock_send_email.assert_called_once_with(
            original_url="http://mock-website.com",
            found_link="http://docs.google.com/forms/new-link",
            final_url=new_final_url,
            link_changed=True
        )

def test_link_is_same_sends_email_with_new_args():
    """
    Tests that send_email is called with correct arguments when the final_url is the same as EXPECTED_URL.
    """
    with mock.patch.object(api.check_link, 'URL', "http://mock-website.com"), \
         mock.patch.object(api.check_link, 'EXPECTED_URL', "http://old-signup-link.com/form"), \
         mock.patch.object(api.check_link, 'SENDER_EMAIL', "test@example.com"), \
         mock.patch.object(api.check_link, 'RECEIVER_EMAILS', ["recipient@example.com"]), \
         mock.patch.object(api.check_link, 'SMTP_USERNAME', "test@example.com"), \
         mock.patch.object(api.check_link, 'SMTP_PASSWORD', "password"), \
         mock.patch('requests.get') as mock_get, \
         mock.patch('requests.head') as mock_head, \
         mock.patch('api.check_link.send_email') as mock_send_email:

        # Configure mock_get to return our mock HTML
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = MOCK_WEBSITE_HTML
        mock_get.return_value.raise_for_status.return_value = None

        # Configure mock_head to return the EXPECTED_URL (same as configured EXPECTED_URL)
        same_final_url = api.check_link.EXPECTED_URL
        mock_head.return_value.url = same_final_url
        mock_head.return_value.raise_for_status.return_value = None

        api.check_link.check_website() # Call the function from the module

        # Assert that send_email was called with the correct arguments
        mock_send_email.assert_called_once_with(
            original_url="http://mock-website.com",
            found_link="http://docs.google.com/forms/new-link",
            final_url=same_final_url,
            link_changed=False
        )

def test_no_signup_link_found_sends_email():
    """
    Tests that an email is sent when no sign-up link is found on the page.
    """
    with mock.patch.object(api.check_link, 'URL', "http://mock-website.com"), \
         mock.patch.object(api.check_link, 'EXPECTED_URL', "http://old-signup-link.com/form"), \
         mock.patch.object(api.check_link, 'SENDER_EMAIL', "test@example.com"), \
         mock.patch.object(api.check_link, 'RECEIVER_EMAILS', ["recipient@example.com"]), \
         mock.patch.object(api.check_link, 'SMTP_USERNAME', "test@example.com"), \
         mock.patch.object(api.check_link, 'SMTP_PASSWORD', "password"), \
         mock.patch('requests.get') as mock_get, \
         mock.patch('api.check_link.send_email') as mock_send_email:

        # Configure mock_get to return HTML with no sign-up link
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = MOCK_WEBSITE_HTML_NO_LINK
        mock_get.return_value.raise_for_status.return_value = None

        api.check_link.check_website()

        # Assert that send_email was called with found_link=None
        mock_send_email.assert_called_once_with(
            original_url="http://mock-website.com",
            found_link=None,
            final_url=None, # In this case final_url will be None as no link is found
            link_changed=False
        )

def test_url_env_var_not_set_sends_email():
    """
    Tests that an email is sent when the URL environment variable is not set.
    """
    with mock.patch.object(api.check_link, 'URL', None), \
         mock.patch.object(api.check_link, 'EXPECTED_URL', "http://old-signup-link.com/form"), \
         mock.patch.object(api.check_link, 'SENDER_EMAIL', "test@example.com"), \
         mock.patch.object(api.check_link, 'RECEIVER_EMAILS', ["recipient@example.com"]), \
         mock.patch.object(api.check_link, 'SMTP_USERNAME', "test@example.com"), \
         mock.patch.object(api.check_link, 'SMTP_PASSWORD', "password"), \
         mock.patch('api.check_link.send_email') as mock_send_email:

        api.check_link.check_website()

        # Assert that send_email was called with appropriate arguments
        mock_send_email.assert_called_once_with(
            original_url="N/A",
            found_link=None,
            final_url="N/A",
            link_changed=False
        )



