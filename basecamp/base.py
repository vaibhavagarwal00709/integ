import json
import requests
import logging
from logging import getLogger
from minion_utils.integration_utils.base_runner import LoggedInBaseRunner
from minion_utils.integration_utils.base_runner import BaseRunner
from minion_utils.exceptions import LoginFailedException
import os
from bs4 import BeautifulSoup

from minion_utils.exceptions import PlaywrightTimeoutError, LoginFailedException

# class BasecampBase(OAuthRunner):

logger = logging.getLogger(__name__)

# company : 3689436


class BasecampBase(LoggedInBaseRunner):
    @property
    def get_company(self):
        # company_id = self.task.app.settings.get("company_id").value
        company_id = "3689436"
        return company_id

    @property
    def get_url(self):
        # account_id = self.task.app.settings.get("account_id").value
        account_id = "5822427"
        return f"https://3.basecamp.com/{account_id}/"

    def _login(self):
        url = f"{self.get_url}"
        page = self.browser_handler.get_existing_page()
        page.navigate(url)

        try:
            page.locator(
                f'img.avatar[data-current-person-avatar="true"][src="{url}my/avatar"]').hover()
            logged_in = True
        except PlaywrightTimeoutError:
            logged_in = False

        if not logged_in:
            raise LoginFailedException("Basecamp login failed")

        return page

    def is_logged_in(self):
        try:
            self._login()
        except Exception as e:
            self.log(e, logging.ERROR)
            self.log("Not logged in!")
            return False
        else:
            self.log("Already logged in!")
            return True

    def get_soup(self, filter_url, goto_url):
        responses = []
        url = f"{self.get_url}"
        page = self._login()

        def handle_response(response):
            if response.url == filter_url:
                try:
                    responses.append(response)
                except Exception as e:
                    print(f"Error capturing response: {e}")

        page.on("response", handle_response)
        page.navigate(goto_url)
        page.wait_for_load_state("networkidle")

        html_content = responses[0].text()
        soup = BeautifulSoup(html_content, 'html.parser')

        return soup
