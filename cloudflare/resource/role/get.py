import logging

from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from core.schema.app_group import AppGroupSchema
from integrations.cloudflare.base import CloudflareBase


class CloudflareRoleGet(CloudflareBase):
    def action(self) -> TaskStatus:
        url = f"{self.BASE_URL}/{self.account_id}/roles"
        roles = self.make_paginated_request(url=url)

        self.log(roles)

        role_schemas = [
            AppGroupSchema(
                app=self.task.app,
                local_id=role["id"],
                name=role["name"],
                description=role["description"],
                status=ResourceStatus.ACTIVE,
                resource_type=self.task.resource_type,
            )
            for role in roles
        ]

        self.tower_api.bulk_sync_resources(
            self.task.resource_type.base_type, self.task.app.external_uuid, role_schemas
        )
        return TaskStatus.COMPLETED
