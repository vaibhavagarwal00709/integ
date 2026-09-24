import logging
from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.basecamp.base import BasecampBase


class BasecampUserDelete(BasecampBase):
    def action(self) -> TaskStatus:

        url = f"{self.get_url}"
        page = self._login()
        people_url = f"{url}account/people"
        page.navigate(people_url)

        name = self.task.app_user.name
        email = self.taskapp_user.email
        if name == "":
            name_parts = email.split("@")
            name = name_parts[0]

        figure_element = page.locator(f'.people-roster__person:has-text("{email}")').locator(
            'button[name="button"][type="submit"][aria-label="Options menu"]')
        page.human_click(figure_element)

        parent_span = page.locator(
            '.action-sheet__content[data-bridge--action-sheet-target="menuToHide"]')
        parent_span.wait_for(state='visible', timeout=30000)
        edit_info_link = parent_span.locator(
            'a.action-sheet__action.action-sheet__action--edit')
        edit_info_link.wait_for(state='visible', timeout=30000)
        page.human_click(edit_info_link)

        delete_link = page.locator('a.decorated.decorated--delete')
        delete_link.wait_for(state='visible', timeout=30000)
        page.human_click(delete_link)

        page.on("dialog", lambda dialog: dialog.accept()
                if dialog.type == "confirm" else dialog.dismiss())

        remove_button = page.locator(
            f'input[type="submit"][name="commit"][value="Remove {name} completely"]')
        remove_button.wait_for(state='visible', timeout=10000)
        remove_button.scroll_into_view_if_needed()
        page.human_click(remove_button)

        self.log(f"User {name} has been deleted successfully", logging.INFO)
        self.task.app_user.status = ResourceStatus.INACTIVE
        self.tower_api.update_resource(self.task.app_user)
        return TaskStatus.COMPLETED
