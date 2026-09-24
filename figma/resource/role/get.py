from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from core.schema.app_group import AppGroupSchema
from integrations.figma.base import FigmaBase


class FigmaRoleGet(FigmaBase):
    def action(self) -> TaskStatus:
        roles = [
            "Owner",
            "Admin",
            "Can edit",
            "Can view",
        ]
        role_schemas = [
            AppGroupSchema(
                status=ResourceStatus.ACTIVE,
                app=self.task.app,
                local_id=role,
                description=role,
                resource_type=self.task.resource_type,
            ) for role in roles
        ]
        self.tower_api.bulk_sync_resources(self.task.resource_type.base_type, self.task.app.external_uuid,
                                           role_schemas)
        return TaskStatus.COMPLETED
