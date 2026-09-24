import logging

from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from core.schema.app_user import AppUserSchema, IdenAppUserExtension
from core.schema.app_group_membership import AppGroupMembershipSchema, BaseAppGroupSchema
from integrations.cloudflare.base import CloudflareBase


class CloudflareUserGet(CloudflareBase):
    def action(self) -> TaskStatus:
        url = f"{self.BASE_URL}/{self.account_id}/members"
        users = self.make_paginated_request(url=url)

        self.log(users)

        def get_status(user):
            if user['status'] == 'pending':
                return ResourceStatus.INVITED
            return ResourceStatus.ACTIVE

        user_schemas = [
            AppUserSchema(
                email=user["user"]["email"],
                local_id=user["id"],
                status=get_status(user),
                resource_type=self.task.resource_type,
                app=self.task.app,
                iden_extension=IdenAppUserExtension(
                    app_group_memberships={
                        "role": [
                            AppGroupMembershipSchema(
                                # local_id=role["id"]
                                app_group=BaseAppGroupSchema(
                                    local_id=role["id"])
                            ) for role in user["roles"]
                        ]
                    }
                )
            ) for user in users
        ]

        self.tower_api.bulk_sync_resources(
            self.task.resource_type.base_type, self.task.app.external_uuid, user_schemas)
        return TaskStatus.COMPLETED
