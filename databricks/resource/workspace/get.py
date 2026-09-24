from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from core.schema.app_group import AppGroupSchema, IdenAppGroupExtension
from core.schema.app_group_membership import AppGroupMembershipSchema, BaseAppUserSchema
from integrations.databricks.base import DatabricksBase


class DatabricksWorkspaceGet(DatabricksBase):

    def action(self) -> TaskStatus:
        client = self.get_account_client()

        workspace_schemas = [
            AppGroupSchema(
                app=self.task.app,
                local_id=str(workspace.workspace_id),
                description=workspace.workspace_name,
                name=workspace.workspace_name,
                status=ResourceStatus.ACTIVE,
                resource_type=self.task.resource_type,
            )
            for workspace in client.workspaces.list()
        ]

        self.tower_api.bulk_sync_resources(self.task.resource_type.base_type, self.task.app.external_uuid,
                                           workspace_schemas)
        return TaskStatus.COMPLETED
