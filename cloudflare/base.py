import json
import requests
import logging
from minion_utils.integration_utils.base_runner import BaseRunner


class CloudflareBase(BaseRunner):
    BASE_URL = "https://api.cloudflare.com/client/v4/accounts"

    @property
    def account_id(self):
        return self.task.app.settings.get("account_id").value

    def _send_request(self, url, method="GET", data=None):
        access_token = self.credential_manager.get_credential("access_token")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.request(
            method=method, url=url, headers=headers, json=data)
        return response

    def make_request(self, url, method="GET", data=None):
        response = self._send_request(url, method, data)
        if response.status_code != 200:
            self.log(
                f"Request failed with status code {
                    response.status_code}", logging.ERROR
            )
            return None

        return response

    def make_paginated_request(self, url):
        initial_response = self._send_request(url=url, method="GET")
        if not initial_response or initial_response.status_code != 200:
            self.log(
                f"Request failed with status code {
                    initial_response.status_code} | {initial_response.text}",
                logging.ERROR,
            )
            return None

        results = initial_response.json()["result"]
        total_pages = initial_response.json()["result_info"]["total_pages"]
        self.log(f"Found {total_pages} pages")

        if total_pages == 1:
            return results

        for page in range(2, total_pages + 1):
            self.log(f"Fetching page {page} of {total_pages}")
            page_url = url + f"?page={page}"
            response = self._send_request(url=page_url, method="GET")
            if response.status_code != 200:
                self.log(
                    f"Request failed with status code {response.status_code}",
                    logging.ERROR,
                )
                return None
            results += response.json()["result"]

        return results
