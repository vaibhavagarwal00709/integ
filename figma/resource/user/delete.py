import json
import logging
from playwright.sync_api import expect

from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.figma.base import FigmaBase
from minion_utils.exceptions import PlaywrightTimeoutError


class FigmaUserDelete(FigmaBase):

    def action(self) -> TaskStatus:
        team_url = f"{self.get_team_url}."
        page = self._login(team_url)
        row_locator = self._search_admin_console(page)
        if not row_locator:
            self.log("Couldn't find user, assuming deleted", logging.WARNING)
            return TaskStatus.COMPLETED

        row_locator.hover()
        option_button = row_locator.locator(
            f"div[class*=members_table--menuColumn]")
        option_button.scroll_into_view_if_needed()
        page.human_click(option_button)
        page.human_click(page.get_by_text("Remove"))
        modal = page.locator("div[class*=header_modal--modal]")
        confirm_delete_button = modal.get_by_role("button", name="Remove")
        page.human_click(confirm_delete_button)
        confirm_delete_button.wait_for(state='detached', timeout=10000)

        self.log("Confirming deletion")
        row_locator = self._search_admin_console(page)
        if row_locator is None:
            self.log("Confirmed deletion")
            self.task.app_user.status = ResourceStatus.INACTIVE
            self.tower_api.update_resource(self.task.app_user)
            return TaskStatus.COMPLETED
        self.log("Couldn't confirm deletion", logging.ERROR)
        return TaskStatus.ERROR

    # def action(self) -> TaskStatus:
    #     team_url = f"{self.get_team_url}."
    #     page = self._login(team_url)
    #     tier = self.credential_manager.get_credential("tier")
    #     row_locator_func = self._search_user if tier == "Free" else self._search_admin_console
    #     options_button_class = "members_list_row--permissionsColumnModal" if tier == "Free" else "members_table--menuColumn"
    #     row_locator = row_locator_func(page)
    #     if not row_locator:
    #         self.log("Couldn't find user, assuming deleted", logging.WARNING)
    #         return TaskStatus.COMPLETED

    #     row_locator.hover()
    #     option_button = row_locator.locator(
    #         f"div[class*={options_button_class}]")
    #     option_button.scroll_into_view_if_needed()
    #     page.human_click(option_button)
    #     page.human_click(page.get_by_text("Remove"))

    #     if tier != "Free":
    #         modal = page.locator("div[class*=header_modal--modal]")
    #         confirm_delete_button = modal.get_by_role("button", name="Remove")
    #         page.human_click(confirm_delete_button)
    #         confirm_delete_button.wait_for(state='detached', timeout=10000)

    #     self.log("Confirming deletion")
    #     row_locator = row_locator_func(page)
    #     if row_locator is None:
    #         self.log("Confirmed deletion")
    #         self.task.app_user.status = ResourceStatus.INACTIVE
    #         self.tower_api.update_resource(self.task.app_user)
    #         return TaskStatus.COMPLETED
    #     self.log("Couldn't confirm deletion", logging.ERROR)
    #     return TaskStatus.ERROR
