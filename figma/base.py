import logging
from playwright.sync_api import TimeoutError
from minion_utils.integration_utils.base_runner import LoggedInBaseRunner
from playwright_utils import get_login_timeout
from minion_utils.exceptions import PlaywrightTimeoutError, LoginFailedException

logger = logging.getLogger(__name__)


class FigmaBase(LoggedInBaseRunner):

    def __init__(self, task):
        super().__init__(task)

    @property
    def get_team_url(self):
        team_id = self.task.app.settings.get("team_id").value
        return f"https://www.figma.com/files/team/{team_id}"

    def is_logged_in(self, manual=False):
        try:
            page = self.browser_handler.get_existing_page()
            self.log("Passed page")
            team_url = f"{self.get_team_url}."
            page.navigate(team_url)
            page.get_by_test_id("ProfileButton").hover(
                timeout=get_login_timeout(manual))
        except Exception as e:
            logger.error(e)
            return False
        else:
            logger.info("Logged in!")
            return True

    def _login(self, url):
        page = self.browser_handler.get_existing_page()
        page.navigate(url)
        logged_in = self.is_logged_in()
        if not logged_in:
            raise LoginFailedException("Could not log in to Figma!")
        else:
            self.log("Already logged in!")
            return page

    # def _logout(self):
    #     url = f"{self.get_team_url}."
    #     page = self.browser_handler.get_smart_page()
    #     page.navigate(url)
    #     logged_in = self.is_logged_in(page)
    #     if logged_in:
    #         page.human_click(page.get_by_test_id("ProfileButton"))
    #         page.human_click(page.get_by_text("Log out"))
    #         try:
    #             page.get_by_role("button", name="Log in").hover(timeout=5000)
    #         except PlaywrightTimeoutError:
    #             logger.error("Failed to log out!")
    #             return False
    #         else:
    #             logger.info("Logged out!")
    #             return True

    #     else:
    #         logger.info("Already logged out!")
    #         return True

    def _search_user(self, page):
        email = self.task.app_user.email
        email_locator = page.get_by_text(email, exact=True)
        try:
            page.navigate(
                f"{self.get_team_url}.", lambda: page.get_by_role("button", name="Open team dropdown"))
        except PlaywrightTimeoutError:
            raise Exception(f"NETWORK: Could not navigate")
        page.human_click(page.get_by_role("button", name="Open team dropdown"))
        settings_locator = page.locator(
            "div[class*=multilevel_dropdown--displayContents]")
        page.human_click(settings_locator.get_by_text("View Settings"))
        page.locator(
            'div[class*=team_settings_modal--modalBody]').wait_for(state="visible", timeout=5000)
        modal = page.locator(
            'div[class*=team_settings_modal--modalBody]').first
        page.human_click(page.get_by_role("button", name="Members"))
        row_locator = modal.locator(
            'div[class*=members_list--memberRowForModal]').filter(has=email_locator)
        try:
            row_locator.wait_for(state="attached", timeout=5000)
        except PlaywrightTimeoutError:
            return None
        else:
            return row_locator

    def _open_team_admin_console(self, page):
        team_admin_console_url = f"{
            self.get_team_url}/team-admin-console/members"
        page.navigate(team_admin_console_url,
                      lambda: page.get_by_role("button", name="Members"))

    def _search_admin_console(self, page):
        email = self.task.app_user.email
        email_locator = page.get_by_text(email, exact=True)
        try:
            self._open_team_admin_console()
        except PlaywrightTimeoutError:
            raise Exception(
                f"NETWORK: Could not navigate to team admin console")

        row_locator = page.get_by_role("row").filter(has=email_locator)
        try:
            row_locator.wait_for(state="attached", timeout=5000)
        except PlaywrightTimeoutError:
            return None
        else:
            return row_locator
