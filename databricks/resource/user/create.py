import logging
from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.service import iam
from databricks.sdk.errors import ResourceConflict, ResourceAlreadyExists
from databricks.sdk.errors import NotFound
from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.databricks.base import DatabricksBase


class DatabricksUserCreate(DatabricksBase):

    def action(self) -> TaskStatus:
        client = self.get_account_client()
        email = self.task.app_user.email
        display_name = self.task.app_user.first_name + " " + self.task.app_user.last_name

        try:
            user_obj = client.users.create(
                user_name=email,
                display_name=display_name,
            )
            user_id = user_obj.id
            self.log(f"Created user {user_id}")
        except ResourceConflict:
            self.log(f"User with {email} already exists", logging.WARNING)
            user_obj = [u for u in list(
                client.users.list()) if u.user_name == email][0]
            user_id = user_obj.id

        workspaces = self.task.app_user.iden_extension.app_group_memberships["workspace"]
        for ws in workspaces:
            workspace_id = ws.app_group.local_id
            print(ws.attributes)
            self._add_to_workspace(client, workspace_id,
                                   user_id, ws.attributes[0].value)

        self.task.app_user.status = ResourceStatus.ACTIVE
        self.tower_api.update_resource(self.task.app_user)
        return TaskStatus.COMPLETED
