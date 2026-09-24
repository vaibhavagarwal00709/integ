from core.enums import TaskStatus, ResourceBaseType
from core.schema.resource_type import ResourceTypeSchema
from integrations.figma.base import FigmaBase


class FigmaConfigure(FigmaBase):
    def action(self) -> TaskStatus:
        app = self.task.app

        user_resource = ResourceTypeSchema(
            name="User",
            slug="user",
            base_type=ResourceBaseType.USER,
            sync_order=1
        )
        role_resource = ResourceTypeSchema(
            name="Role",
            slug="role",
            base_type=ResourceBaseType.GROUP,
            sync_order=0
        )
        role_membership_resource = ResourceTypeSchema(
            name="Role Membership",
            slug="role_membership",
            base_type=ResourceBaseType.GROUP_MEMBERSHIP,
            sync_order=-1
        )

        app.connection.resource_types = [
            user_resource, role_resource, role_membership_resource]
        self.tower_api.update_app(app.external_uuid, app)

        return TaskStatus.COMPLETED
