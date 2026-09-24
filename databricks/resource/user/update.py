import logging
from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.service import iam
from databricks.sdk.errors import ResourceConflict, ResourceAlreadyExists
from databricks.sdk.errors import NotFound
from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.databricks.base import DatabricksBase


class DatabricksUserUpdate(DatabricksBase):

    def action(self) -> TaskStatus:
        # workspaces_added = params["workspaces_added"]
        # workspaces_removed = params["workspaces_removed"]

        client = self.get_account_client()
        user_id = self.task.app_user.local_id
        workspaces = self.task.app_user.iden_extension.app_group_memberships["workspace"]
        workspaces_existing = {
            ws.workspace_id for ws in client.workspaces.list()}

        workspaces_added = [
            item for item in workspaces if item.app_group.local_id not in workspaces_existing]
        workspaces_removed = [
            ws for ws in workspaces_existing if ws not in {item.app_group.local_id for item in workspaces}]

        for ws in workspaces_added:
            workspace_id = ws.app_group.local_id
            self._add_to_workspace(client, workspace_id,
                                   user_id, ws.attributes.value)

        for workspace_id in workspaces_removed:
            self._remove_from_workspace(client, workspace_id, user_id)

        self.tower_api.update_resource(self.task.app_user)
        return TaskStatus.COMPLETED
