from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from core.schema.app_group import AppGroupSchema, IdenAppGroupExtension
from core.schema.app_group_membership import AppGroupMembershipSchema, BaseAppUserSchema
from core.schema.app_group import AppGroupSchema, IdenAppGroupExtension
from core.schema.app_group_membership import AppGroupMembershipSchema, BaseAppGroupSchema, BaseAppUserSchema
from integrations.basecamp.base import BasecampBase
import logging


class BasecampProjectGet(BasecampBase):

    def action(self) -> TaskStatus:
        page = self._login()
        url = f"{self.get_url}"
        filter_url = f"{url}projects/directory?view=active"
        goto_url = f"{url}projects/directory?view=active"

        soup = self.get_soup(filter_url, goto_url)

        projects = []

        project_articles = soup.find_all(
            'article', class_='project-list__project')

        for article in project_articles:
            project_id = article.get('id', '').replace(
                'bucket_', '').replace('_line', '')
            project_name = article.find(
                'span', attrs={'data-project-filter-target': 'highlightable'}).text.strip()

            projects.append({
                'id': project_id,
                'name': project_name
            })

        project_schemas = []

        for project in projects:
            filter_url = f"{url}projects/{project["id"]}/people/users/edit"
            goto_url = f"{url}projects/{project["id"]}/people/users/edit"
            soup = self.get_soup(filter_url, goto_url)

            person_figures = soup.find_all(
                'figure', class_='people-roster__person')

            project_members = []

            for figure in person_figures:
                person_id = figure.get('data-person-id', '')

                project_members.append({
                    'id': person_id,
                })

            project_schemas.append(
                AppGroupSchema(
                    app=self.task.app,
                    local_id=str(project["id"]),
                    description="",
                    name=project["name"],
                    status=ResourceStatus.ACTIVE,
                    resource_type=self.task.resource_type,
                    iden_extension=IdenAppGroupExtension(
                        members=[
                            AppGroupMembershipSchema(
                                local_id=str(project["id"]) +
                                ":"+str(member["id"]),
                                app_group=BaseAppGroupSchema(
                                    local_id=str(project["id"]),
                                    name=project["name"]
                                ),
                                member_app_user=BaseAppUserSchema(
                                    local_id=str(member["id"])
                                )
                            ) for member in project_members
                        ]
                    )
                )
            )

        self.tower_api.bulk_sync_resources(self.task,
                                           project_schemas)
        return TaskStatus.COMPLETED
