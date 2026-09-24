from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.service import iam
from core.enums import TaskStatus
from core.enums.resource_status import ResourceStatus
from core.schema.app_user import AppUserSchema, IdenAppUserExtension
from core.schema.app_group_membership import AppGroupMembershipSchema, BaseAppGroupSchema
from core.schema.attribute_type import BaseResourceAttributeValueSchema, BaseResourceAttributeSchema
from integrations.databricks.base import DatabricksBase


class DatabricksUserGet(DatabricksBase):
    def action(self) -> TaskStatus:
        client = self.get_account_client()
        user_schemas = []
        for user in client.users.list():
            curr_name = user.display_name
            if curr_name is None:
                self.log(f"User {user.id} has a NULL display_name.")
                first_name = ""
                last_name = ""
            else:
                curr_name_parts = curr_name.split(" ")
                if len(curr_name_parts) < 2:
                    self.log(
                        f"User {user.id} has an incomplete display_name: {curr_name}")
                    first_name = curr_name_parts[0] if curr_name_parts else "Unknown"
                    last_name = "" if len(
                        curr_name_parts) < 2 else curr_name_parts[1]
                else:
                    first_name = curr_name_parts[0]
                    last_name = curr_name_parts[1]

            user_schemas.append(
                AppUserSchema(
                    email=user.user_name,
                    local_id=user.id,
                    first_name=first_name,
                    last_name=last_name,
                    licensed=True,  # is_bot
                    status=ResourceStatus.ACTIVE,
                    resource_type=self.task.resource_type,
                    app=self.task.app,
                    iden_extension=IdenAppUserExtension(
                        app_group_memberships={
                            "workspace": []
                        }
                    )
                )


            )

        for principal in client.service_principals.list():
            user_schemas.append(
                AppUserSchema(
                    local_id=principal.id,
                    licensed=False,
                    status=ResourceStatus.ACTIVE,
                    resource_type=self.task.resource_type,
                    app=self.task.app,
                    iden_extension=IdenAppUserExtension(
                        app_group_memberships={
                            "workspace": []
                        }
                    )
                )


            )

        for workspace in client.workspaces.list():
            workspace_id = workspace.workspace_id
            workspace_name = workspace.workspace_name
            workspace_assignments = client.workspace_assignment.list(
                workspace_id)
            for ws_assignment in workspace_assignments:
                permissions = ws_assignment.permissions
                if any(permission == iam.WorkspacePermission.ADMIN for permission in permissions):
                    role = 'ADMIN'
                elif any(permission == iam.WorkspacePermission.USER for permission in permissions):
                    role = 'USER'
                else:
                    role = 'UNKNOWN'

                principal_id = str(ws_assignment.principal.principal_id)
                for user in user_schemas:
                    if user.local_id == principal_id:
                        user.iden_extension.app_group_memberships["workspace"].append(
                            AppGroupMembershipSchema(
                                app_group=BaseAppGroupSchema(
                                    local_id=str(workspace_id),
                                    name=workspace_name
                                ),
                                attributes=[BaseResourceAttributeValueSchema(
                                    resource_attribute=BaseResourceAttributeSchema(
                                        slug="role",
                                        type="string"
                                    ),
                                    value=role
                                )
                                ]
                            )

                        )

        # print(user_schemas)

        self.tower_api.bulk_sync_resources(
            self.task.resource_type.base_type, self.task.app.external_uuid, user_schemas)
        return TaskStatus.COMPLETED
