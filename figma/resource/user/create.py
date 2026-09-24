import json
import logging
from playwright.sync_api import expect

from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.figma.base import FigmaBase
from minion_utils.exceptions import PlaywrightTimeoutError


class FigmaUserCreate(FigmaBase):

    def action(self) -> TaskStatus:
        team_url = f"{self.get_team_url}."
        page = self._login(team_url)
        role = self.task.app_user.iden_extension.app_group_memberships["role"].app_group.local_id
        team_admin_console_url = f"{
            self.get_team_url}/team-admin-console/members"
        page.navigate(team_admin_console_url,
                      lambda: page.get_by_role("button", name="Invite users"))

        dialog = page.get_by_role("dialog")
        email = self.task.app_user.email
        page.slow_type(dialog.get_by_test_id("autocomplete-input"), email)
        self.log("Entered email")

        if role and role != "No team role":
            invite_section = page.locator(
                "div[class*=permissions_modal--inviteBar]")
            role_select_button = invite_section.locator(
                "div[class*=role_row--select]").first
            page.human_click(role_select_button)
            page.human_click(invite_section.get_by_text(role.lower()).last)

        page.human_click(page.get_by_role("button", name="Invite", exact=True))
        self.log("Clicked Invite button")

        # confirm invite
        row_locator = self._search_admin_console(page)
        if row_locator:
            self.task.app_user.status = ResourceStatus.INVITED
            self.tower_api.update_resource(self.task.app_user)
            self.log("Confirmed creation")
            return TaskStatus.COMPLETED
        self.log("Couldn't confirm creation", logging.ERROR)
        return TaskStatus.ERROR

    # def action(self) -> TaskStatus:
    #     team_url = f"{self.get_team_url}."
    #     page = self._login(team_url)
    #     role = self.task.app_user.iden_extension.app_group_memberships["role"].app_group.local_id
    #     tier = self.credential_manager.get_credential("tier")
    #     if tier == "Free":
    #         page.navigate(team_url, lambda: page.get_by_role(
    #             "button", name="Share"))
    #         page.human_click(page.get_by_role("button", name="Share"))
    #     else:
    #         team_admin_console_url = f"{
    #             self.get_team_url}/team-admin-console/members"
    #         page.navigate(team_admin_console_url,
    #                       lambda: page.get_by_role("button", name="Invite users"))

    #     dialog = page.get_by_role("dialog")
    #     email = self.task.app_user.email
    #     page.slow_type(dialog.get_by_test_id("autocomplete-input"), email)
    #     self.log("Entered email")

    #     if role and role != "No team role":
    #         invite_section = page.locator(
    #             "div[class*=permissions_modal--inviteBar]")
    #         role_select_button = invite_section.locator(
    #             "div[class*=role_row--select]").first
    #         page.human_click(role_select_button)
    #         page.human_click(invite_section.get_by_text(role.lower()).last)

    #     page.human_click(page.get_by_role("button", name="Invite", exact=True))
    #     self.log("Clicked Invite button")

    #     # confirm invite
    #     row_locator_func = self._search_user if tier == "Free" else self._search_admin_console
    #     row_locator = row_locator_func(page)
    #     if row_locator:
    #         self.task.app_user.status = ResourceStatus.INVITED
    #         self.tower_api.update_resource(self.task.app_user)
    #         self.log("Confirmed creation")
    #         return TaskStatus.COMPLETED
    #     self.log("Couldn't confirm creation", logging.ERROR)
    #     return TaskStatus.ERROR
