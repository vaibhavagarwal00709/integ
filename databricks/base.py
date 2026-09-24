from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.service import iam
from databricks.sdk.errors import ResourceConflict, ResourceAlreadyExists
from logging import getLogger
from minion_utils.integration_utils.base_runner import BaseRunner

logger = getLogger(__name__)


class DatabricksBase(BaseRunner):

    def get_account_client(self):
        account_id = self.task.app.settings.get("account_id").value
        client_id = self.credential_manager.get_credential("client_id")
        client_secret = self.credential_manager.get_credential("client_secret")
        return AccountClient(
            host="https://accounts.cloud.databricks.com",
            account_id=account_id,
            client_id=client_id,
            client_secret=client_secret
        )

    def _add_to_workspace(self, client, workspace_id, user_id, role):
        role_dict = {
            "USER": iam.WorkspacePermission.USER,
            "ADMIN": iam.WorkspacePermission.ADMIN
        }
        client.workspace_assignment.update(
            workspace_id=workspace_id,
            principal_id=user_id,
            permissions=[role_dict[role]]
        )
        logger.info(f"Added user {user_id} to workspace {
                    workspace_id} with role {role}")

    def _remove_from_workspace(self, client, workspace_id, user_id):
        client.workspace_assignment.delete(
            workspace_id=workspace_id,
            principal_id=user_id,
        )
        logger.info(f"Removed user {user_id} from workspace {workspace_id}")
