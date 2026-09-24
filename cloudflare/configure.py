from core.enums import TaskStatus, ResourceBaseType
from core.schema.resource_type import ResourceTypeSchema
from integrations.cloudflare.base import CloudflareBase


class CloudflareConfigure(CloudflareBase):
    def action(self) -> TaskStatus:
        user_resource = ResourceTypeSchema(
            name="User", slug="user", base_type=ResourceBaseType.USER, sync_order=1
        )
        role_resource = ResourceTypeSchema(
            name="Role", slug="role", base_type=ResourceBaseType.GROUP, sync_order=0
        )
        role_membership_resource = ResourceTypeSchema(
            name="Role Membership",
            slug="role_membership",
            base_type=ResourceBaseType.GROUP_MEMBERSHIP,
            sync_order=-1,
        )
        self.task.app.connection.resource_types = [
            user_resource,
            role_resource,
            role_membership_resource,
        ]
        self.tower_api.update_app(self.task.app.external_uuid, self.task.app)
        return TaskStatus.COMPLETED
