from core.enums import ResourceBaseType, TaskStatus
from core.schema.attribute_type import BaseResourceAttributeSchema
from core.schema.resource_type import ResourceTypeSchema
from integrations.basecamp.base import BasecampBase


class BasecampConfigure(BasecampBase):
    def action(self):
        app = self.task.app
        user_resource = ResourceTypeSchema(
            name="User",
            slug="user",
            base_type=ResourceBaseType.USER,
            sync_order=0
        )
        group_resource = ResourceTypeSchema(
            name="Project",
            slug="project",
            base_type=ResourceBaseType.GROUP,
            sync_order=1
        )
        group_membership_resource = ResourceTypeSchema(
            name="Project Membership",
            slug="project_membership",
            base_type=ResourceBaseType.GROUP_MEMBERSHIP,
            sync_order=-1,
        )
        app.connection.resource_types = [
            user_resource, group_resource, group_membership_resource]
        success = self.tower_api.update_app(app.external_uuid, app)
        return TaskStatus.COMPLETED if success else TaskStatus.ERROR
