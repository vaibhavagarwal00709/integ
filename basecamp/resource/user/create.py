import logging
from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.basecamp.base import BasecampBase


class BasecampUserCreate(BasecampBase):
    def action(self) -> TaskStatus:

        url = f"{self.get_url}"
        page = self._login()
        people_url = f"{url}account/enrollments/employees/new"
        page.navigate(people_url, lambda: page.locator(
            'input[type="submit"][name="commit"][value="Email invitation now…"]'))

        name = f"{self.task.app_user.first_name} {
            self.task.app_user.last_name}"
        email = self.task.app_user.email
        if name == "":
            name_parts = email.split("@")
            name = name_parts[0]

        input_locator = page.locator('input[name="people[][name]"]')
        input_locator.wait_for(state='visible', timeout=30000)
        page.slow_type(input_locator, name)

        email_locator = page.locator(
            'input[name="people[][email_address]"]')
        page.slow_type(email_locator, email)

        button_locator = page.locator(
            'input[type="submit"][name="commit"][value="Email invitation now…"]')
        page.human_click(button_locator)

        people_url = f"{url}account/people"
        page.navigate(people_url)

        figure_element = page.locator(f'.people-roster__person:has-text("{email}")').locator(
            'button[name="button"][type="submit"][aria-label="Options menu"]')
        page.human_click(figure_element)

        parent_span = page.locator(
            '.action-sheet__content[data-bridge--action-sheet-target="menuToHide"]')
        parent_span.wait_for(state='visible', timeout=30000)
        move_link = parent_span.locator(
            'a.action-sheet__action.action-sheet__action--move')
        move_link.wait_for(state='visible', timeout=30000)
        page.human_click(move_link)

        project_memberships = self.task.app_user.iden_extension.app_group_memberships.get(
            'project', [])

        project_memberships = self.task.app_user.iden_extension.app_group_memberships.get(
            'project', [])
        for project_membership in project_memberships:
            project_id = project_membership.app_group.local_id
            checkbox_selector = f'input[type="checkbox"][value="{project_id}"]'
            checkbox = page.locator(checkbox_selector)
            if checkbox.is_visible():
                checkbox.click()

        page.human_click(page.get_by_role("button", name="All on"))
        button = page.wait_for_selector(
            'input.btn.btn--primary.flush', timeout=10000)
        button.scroll_into_view_if_needed()
        page.human_click(button)

        self.log(f"User {name} has been created successfully", logging.INFO)
        self.task.app_user.status = ResourceStatus.INVITED
        self.tower_api.update_resource(self.task.app_user)
        return TaskStatus.COMPLETED
