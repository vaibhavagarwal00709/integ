import logging
from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from integrations.cloudflare.base import CloudflareBase


class CloudflareUserDelete(CloudflareBase):
    def action(self) -> TaskStatus:
        member_id = self.task.app_user.local_id
        if member_id:
            url = f"{self.BASE_URL}/{self.account_id}/members/{member_id}"
            response = self._send_request(url=url, method="DELETE")
            if response.status_code == 200:
                self.log("User Deleted")
                self.task.app_user.status = ResourceStatus.INACTIVE
                self.tower_api.update_resource(self.task.app_user)
                return TaskStatus.COMPLETED
            elif response.status_code == 404:
                self.log("Member not found for account", logging.WARNING)
                self.task.app_user.status = ResourceStatus.INACTIVE
                self.tower_api.update_resource(self.task.app_user)
                return TaskStatus.COMPLETED
            else:
                self.log(f"Failed to delete user", logging.ERROR)
                return TaskStatus.ERROR
        else:
            return TaskStatus.ERROR
