import logging

from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from core.schema.app_user import AppUserSchema
from integrations.cloudflare.base import CloudflareBase


class CloudflareUserUpdate(CloudflareBase):
    def action(self) -> TaskStatus:
        member_id = self.task.app_user.local_id
        url = f"{self.BASE_URL}/{self.account_id}/members/{member_id}"
        roles = [
            element.app_group.local_id
            for element in self.task.app_user.iden_extension.app_group_memberships["role"]
        ]
        data = {"roles": [{"id": role} for role in roles]}
        response = self._send_request(url=url, method="PUT", data=data)
        if response.status_code != 200:
            self.log("Failed", logging.WARNING)
            return TaskStatus.ERROR
        self.tower_api.update_resource(self.task.app_user)
        return TaskStatus.COMPLETED
