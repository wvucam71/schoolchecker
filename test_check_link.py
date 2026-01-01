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

def test_link_has_changed_triggers_email():
    """
    Tests that send_email is called when the final_url is different from EXPECTED_URL.
    Assumes the link has changed.
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
        mock_head.return_value.url = "http://new-signup-link.com/form"
        mock_head.return_value.raise_for_status.return_value = None

        api.check_link.check_website() # Call the function from the module

        # Assert that requests.get was called
        mock_get.assert_called_once_with(api.check_link.URL, timeout=10)

        # Assert that requests.head was called with the found link
        mock_head.assert_called_once_with("http://docs.google.com/forms/new-link", allow_redirects=True, timeout=10)

        # Assert that send_email was called with the new link
        mock_send_email.assert_called_once_with("http://new-signup-link.com/form")

def test_link_is_same_does_not_trigger_email():
    """
    Tests that send_email is NOT called when the final_url is the same as EXPECTED_URL.
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

        # Configure mock_head to return the EXPECTED_URL
        mock_head.return_value.url = api.check_link.EXPECTED_URL
        mock_head.return_value.raise_for_status.return_value = None

        api.check_link.check_website() # Call the function from the module

        # Assert that send_email was NOT called
        mock_send_email.assert_not_called()

