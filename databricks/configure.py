from core.enums import TaskStatus, ResourceBaseType
from core.schema.resource_type import ResourceTypeSchema
from integrations.databricks.base import DatabricksBase


class DatabricksConfigure(DatabricksBase):
    def action(self) -> TaskStatus:
        user_resource = ResourceTypeSchema(
            name="User", slug="user", base_type=ResourceBaseType.USER, sync_order=1
        )
        workspace_resource = ResourceTypeSchema(
            name="Workspace",
            slug="workspace",
            base_type=ResourceBaseType.GROUP,
            sync_order=0
        )
        workspace_membership_resource = ResourceTypeSchema(
            name="Workspace membership",
            slug="workspace_membership",
            base_type=ResourceBaseType.GROUP_MEMBERSHIP,
            sync_order=-1
        )
        self.task.app.connection.resource_types = [
            user_resource,
            workspace_resource,
            workspace_membership_resource,
        ]
        self.tower_api.update_app(self.task.app.external_uuid, self.task.app)
        return TaskStatus.COMPLETED
