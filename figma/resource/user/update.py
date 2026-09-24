import json
import logging
from playwright.sync_api import expect

from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.figma.base import FigmaBase
from minion_utils.exceptions import PlaywrightTimeoutError


class FigmaUserUpdate(FigmaBase):

    def action(self) -> TaskStatus:
        team_url = f"{self.get_team_url}."
        page = self._login(team_url)
        role = self.task.app_user.iden_extension.app_group_memberships["role"].app_group.local_id
        row_locator = self._search_admin_console(page)
        row_locator.hover()
        option_button = row_locator.locator(
            f"div[class*=members_table--dropdownColumn]")
        option_button.scroll_into_view_if_needed()
        page.human_click(option_button)
        self.log("Clicked options button")
        menu = page.get_by_role("menu")
        page.human_click(menu.get_by_text(role))
        self.log(f"Clicked '{role}' role")

        # confirm role change
        self.log("Confirming role change")
        row_locator = self._search_admin_console(page)
        option_button = row_locator.locator(
            f"div[class*=members_table--dropdownColumn]")
        option_button.scroll_into_view_if_needed()
        if option_button.inner_text() == role:
            self.tower_api.update_resource(self.task.app_user)
            return TaskStatus.COMPLETED
        return TaskStatus.ERROR

    # def action(self) -> TaskStatus:
    #     team_url = f"{self.get_team_url}."
    #     page = self._login(team_url)
    #     tier = self.credential_manager.get_credential("tier")
    #     role = self.task.app_user.iden_extension.app_group_memberships["role"].app_group.local_id
    #     row_locator_func = self._search_user if tier == "Free" else self._search_admin_console
    #     options_button_class = "members_list_row--permissionsColumnModal" if tier == "Free" else "members_table--dropdownColumn"
    #     row_locator = row_locator_func(page)
    #     row_locator.hover()
    #     option_button = row_locator.locator(
    #         f"div[class*={options_button_class}]")
    #     option_button.scroll_into_view_if_needed()
    #     page.human_click(option_button)
    #     self.log("Clicked options button")
    #     menu = page.get_by_role("menu")
    #     page.human_click(menu.get_by_text(role))
    #     self.log(f"Clicked '{role}' role")

    #     # confirm role change
    #     self.log("Confirming role change")
    #     option_button = row_locator.locator(
    #         f"div[class*={options_button_class}]")
    #     option_button.scroll_into_view_if_needed()
    #     if option_button.inner_text() == role:
    #         self.tower_api.update_resource(self.task.app_user)
    #         return TaskStatus.COMPLETED
    #     return TaskStatus.ERROR
