import logging

from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from core.schema.app_user import AppUserSchema
from integrations.basecamp.base import BasecampBase


class BasecampUserGet(BasecampBase):
    def action(self) -> TaskStatus:
        responses = []
        url = f"{self.get_url}"
        page = self._login()
        filter_url = f"{
            url}account/companies/{self.get_company}/people?personable_scope=users"
        goto_url = f"{url}account/people"

        people = []
        soup = self.get_soup(filter_url, goto_url)
        for person in soup.find_all('figure', class_='people-roster__person'):
            person_id = person.get('data-person-id', '')
            name_element = person.find('h4', class_='flush')
            if name_element:
                name = name_element.contents[0].strip()
            else:
                name = ''
            email_div = person.find(
                'div', class_='people-roster__person-metadata')
            email_text = email_div.get_text(strip=True) if email_div else ''
            email = email_text.split('•')[0].strip(
            ) if '•' in email_text else email_text

            invited = False
            invited_span = person.find('span', class_='txt--highlight')
            if invited_span and 'Invited on' in invited_span.get_text(strip=True):
                invited = True

            people.append({
                'id': person_id,
                'name': name,
                'email': email,
                'invited': invited,
            })

        user_schemas = []

        for user in people:

            curr_name = user.get("name", "")
            curr_name_parts = curr_name.split(" ")

            if len(curr_name_parts) < 2:
                self.log(
                    f"User {user['id']} has an incomplete display_name: {curr_name}")
                first_name = curr_name_parts[0] if curr_name_parts else "Unknown"
                last_name = "" if len(
                    curr_name_parts) < 2 else curr_name_parts[1]
            else:
                first_name = curr_name_parts[0]
                last_name = curr_name_parts[1]

            user_schemas.append(
                AppUserSchema(
                    email=user["email"],
                    local_id=str(user["id"]),
                    first_name=first_name,
                    last_name=last_name,
                    status=ResourceStatus.INVITED if user["invited"] else ResourceStatus.ACTIVE,
                    resource_type=self.task.resource_type,
                    app=self.task.app,
                )
            )

        self.tower_api.bulk_sync_resources(
            self.task,
            user_schemas
        )

        return TaskStatus.COMPLETED
