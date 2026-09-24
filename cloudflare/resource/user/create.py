import logging

from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.cloudflare.base import CloudflareBase


class CloudflareUserCreate(CloudflareBase):
    def action(self) -> TaskStatus:
        email = self.task.app_user.email
        roles = [
            element.app_group.local_id
            for element in self.task.app_user.iden_extension.app_group_memberships["role"]
        ]
        url = f"{self.BASE_URL}/{self.account_id}/members"
        data = {"email": email, "roles": roles}
        response = self._send_request(
            url=url, method="POST", data=data)
        if response.status_code == 200:
            self.log("Invite sent")
            self.task.app_user.status = ResourceStatus.INVITED
            self.tower_api.update_resource(self.task.app_user)
            return TaskStatus.COMPLETED

        if response.status_code == 400:
            self.log(
                "User already a member or has already been invited.", logging.WARNING
            )
            self.task.app_user.status = ResourceStatus.INVITED
            self.tower_api.update_resource(self.task.app_user)
            return TaskStatus.COMPLETED

        else:
            self.log("Could not invite user", logging.ERROR)
            return TaskStatus.ERROR
