import logging
from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.basecamp.base import BasecampBase


class BasecampUserUpdate(BasecampBase):
    def action(self) -> TaskStatus:
        page = self._login()
        user_id = self.task.app_user.local_id

        old_project_memberships = self.task.config.old_app_user.iden_extension.app_group_memberships.get(
            'project', [])
        current_project_memberships = self.task.app_user.iden_extension.app_group_memberships.get(
            'project', [])

        old_project_local_ids = [
            project_membership.app_group.local_id for project_membership in old_project_memberships]
        current_project_local_ids = [
            project_membership.app_group.local_id for project_membership in current_project_memberships]

        url = f"{self.get_url}"

        name = self.task.app_user.name
        email = self.taskapp_user.email
        if name == "":
            name_parts = email.split("@")
            name = name_parts[0]

        edit_url = f"{url}account/accesses/{user_id}/edit"
        page.navigate(edit_url)

        for project_membership in current_project_memberships:
            project_id = project_membership.app_group.local_id
            if project_id not in old_project_local_ids:
                checkbox_selector = f'input[type="checkbox"][value="{
                    project_id}"]'
                checkbox = page.locator(checkbox_selector)
                if checkbox.is_visible():
                    page.human_click(checkbox)

        for project_membership in old_project_memberships:
            project_id = project_membership.app_group.local_id
            if project_id not in current_project_local_ids:
                checkbox_selector = f'input[type="checkbox"][value="{
                    project_id}"]'
                checkbox = page.locator(checkbox_selector)
                if checkbox.is_visible():
                    page.human_click(checkbox)

        all_on_button = page.get_by_role("button", name="All on")
        all_on_button.wait_for(state='visible', timeout=30000)
        page.human_click(all_on_button)
        button = page.wait_for_selector(
            'input.btn.btn--primary.flush', timeout=10000)
        button.scroll_into_view_if_needed()
        page.human_click(button)

        return TaskStatus.COMPLETED
