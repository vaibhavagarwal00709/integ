import logging
from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.service import iam
from databricks.sdk.errors import ResourceConflict, ResourceAlreadyExists
from databricks.sdk.errors import NotFound
from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.databricks.base import DatabricksBase


class DatabricksUserDelete(DatabricksBase):
    def action(self) -> TaskStatus:
        client = self.get_account_client()
        user_id = self.task.app_user.local_id
        is_bot = not self.task.app_user.licensed
        try:
            if is_bot:
                client.service_principals.delete(id=user_id)
                self.log(f"Deleted bot {user_id}")
                self.task.app_user.status = ResourceStatus.INACTIVE
                self.tower_api.update_resource(self.task.app_user)
                return TaskStatus.COMPLETED
            else:
                client.users.delete(id=user_id)
                self.log(f"Deleted user {user_id}")
                self.task.app_user.status = ResourceStatus.INACTIVE
                self.tower_api.update_resource(self.task.app_user)
                return TaskStatus.COMPLETED
        except NotFound:
            self.log(f"User {user_id} not found", logging.WARNING)
            self.task.app_user.status = ResourceStatus.INACTIVE
            self.tower_api.update_resource(self.task.app_user)
            return TaskStatus.COMPLETED
