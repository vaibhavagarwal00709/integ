import json
import logging
from playwright.sync_api import expect
from core.schema.app_user import AppUserSchema
from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from core.schema.app_user import AppUserSchema, IdenAppUserExtension
from core.schema.app_group_membership import AppGroupMembershipSchema, BaseAppGroupSchema
from integrations.figma.base import FigmaBase
from minion_utils.exceptions import PlaywrightTimeoutError
from playwright_utils import to_json


class FigmaUserGet(FigmaBase):
    def action(self) -> TaskStatus:
        team_url = f"{self.get_team_url}."
        page = self._login(team_url)

        api_url = f"https://www.figma.com/api/teams/{self.team_id}/members"
        with page.expect_response(api_url) as response_info:
            try:
                page.navigate(
                    f"{team_url}/members", lambda: page.locator('div[class*=team_settings_modal--modalBody]'))
            except PlaywrightTimeoutError:
                raise Exception("NETWORK: Couldn't load team members page")
            page.locator(
                'div[class*=team_settings_modal--modalBody]').wait_for(state="visible", timeout=5000)

        response_obj = to_json(response_info)

        role_mapping = {
            999: "Owner",
            900: "Admin",
            100: "Can view",
            300: "Can edit",
        }

        if not response_obj["error"]:
            user_schemas = [
                AppUserSchema(
                    email=self.task.app_user.email,
                    resource_type=self.task.resource_type,
                    app=self.task.app,
                    status=ResourceStatus.INVITED if user["team_role"]["pending"] else ResourceStatus.ACTIVE,
                    iden_extension=IdenAppUserExtension(
                        app_group_memberships={
                            "role": AppGroupMembershipSchema(
                                app_group=BaseAppGroupSchema(
                                    local_id=role_mapping[user["team_role"]["level"]])
                            )
                        }
                    )
                ) for user in response_obj["meta"] if user is not None
            ]
            self.tower_api.bulk_sync_resources(self.task.resource_type.base_type, self.task.app.external_uuid,
                                               user_schemas)
            return TaskStatus.COMPLETED

        return TaskStatus.ERROR

    # def action(self) -> TaskStatus:
    #     team_url = f"{self.get_team_url}."
    #     page = self._login(team_url)
    #     responses = []
    #     page.on('response', lambda response: responses.append(
    #         response.body()) if response.url.endswith("/state") else None)

    #     api_url = f"https://www.figma.com/api/teams/{self.team_id}/members"
    #     with page.expect_response(api_url) as response_info:
    #         try:
    #             page.navigate(
    #                 f"{team_url}/members", lambda: page.locator('div[class*=team_settings_modal--modalBody]'))
    #         except PlaywrightTimeoutError:
    #             raise Exception("NETWORK: Couldn't load team members page")
    #         page.locator(
    #             'div[class*=team_settings_modal--modalBody]').wait_for(state="visible", timeout=5000)

    #     # response_obj = to_json(response_info)
    #     response_obj = to_json(response_info)

    #     responses = [json.loads(response).get("meta", {})
    #                  for response in responses]
    #     team_responses = [
    #         response for response in responses if "teams" in response]
    #     required_team_info = None
    #     for team_response in team_responses:
    #         if not team_response["teams"]:
    #             continue
    #         teams: list = team_response["teams"]
    #         required_team_infos = [
    #             team for team in teams if team["id"] == self.team_id]
    #         if not required_team_infos:
    #             continue
    #         required_team_info = required_team_infos[0]
    #         break

    #     tier = None
    #     if required_team_info is not None:
    #         if required_team_info.get("starter_team", False):
    #             tier = "Free"
    #         elif required_team_info.get("pro_team", False):
    #             tier = "Professional"
    #         elif required_team_info.get("org_team", False):
    #             tier = "Organization"

    #     role_mapping = {
    #         999: "Owner",
    #         900: "Admin",
    #         100: "Can view",
    #         300: "Can edit",
    #     }

    #     if not response_obj["error"]:
    #         user_schemas = [
    #             AppUserSchema(
    #                 email=self.task.app_user.email,
    #                 resource_type=self.task.resource_type,
    #                 app=self.task.app,
    #                 status=ResourceStatus.INVITED if user["team_role"]["pending"] else ResourceStatus.ACTIVE,
    #                 iden_extension=IdenAppUserExtension(
    #                     app_group_memberships={
    #                         "role": AppGroupMembershipSchema(
    #                             app_group=BaseAppGroupSchema(
    #                                 local_id=role_mapping[user["team_role"]["level"]])
    #                         )
    #                     }
    #                 )
    #             ) for user in response_obj["meta"] if user is not None
    #         ]
    #         self.tower_api.bulk_sync_resources(self.task.resource_type.base_type, self.task.app.external_uuid,
    #                                            user_schemas)
    #         return TaskStatus.COMPLETED

    #     return TaskStatus.ERROR

    def action(self) -> TaskStatus:
        team_url = f"{self.get_team_url}."
        page = self._login(team_url)

        api_url = f"https://www.figma.com/api/teams/{self.team_id}/members"
        with page.expect_response(api_url) as response_info:
            try:
                page.navigate(
                    f"{team_url}/members", lambda: page.locator('div[class*=team_settings_modal--modalBody]'))
            except PlaywrightTimeoutError:
                raise Exception("NETWORK: Couldn't load team members page")
            page.locator(
                'div[class*=team_settings_modal--modalBody]').wait_for(state="visible", timeout=5000)

        response_obj = to_json(response_info)

        role_mapping = {
            999: "Owner",
            900: "Admin",
            100: "Can view",
            300: "Can edit",
        }

        if not response_obj["error"]:
            user_schemas = [
                AppUserSchema(
                    email=self.task.app_user.email,
                    resource_type=self.task.resource_type,
                    app=self.task.app,
                    status=ResourceStatus.INVITED if user["team_role"]["pending"] else ResourceStatus.ACTIVE,
                    iden_extension=IdenAppUserExtension(
                        app_group_memberships={
                            "role": AppGroupMembershipSchema(
                                app_group=BaseAppGroupSchema(
                                    local_id=role_mapping[user["team_role"]["level"]])
                            )
                        }
                    )
                ) for user in response_obj["meta"] if user is not None
            ]
            self.tower_api.bulk_sync_resources(self.task.resource_type.base_type, self.task.app.external_uuid,
                                               user_schemas)
            return TaskStatus.COMPLETED

        return TaskStatus.ERROR
