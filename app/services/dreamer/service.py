from fastapi import HTTPException

from app.gateways import dreamer_gateway
from app.services.dreamer.schemas import (
    DreamerGroupResponse,
    DreamerGroupSummary,
    DreamerInGroup,
    DreamerResponse,
    DreamerToGroupRequest,
    DreamerToGroupResponse,
    NewDreamerGroupRequest,
    NewDreamerGroupResponse,
    NewDreamerRequest,
    NewDreamerResponse,
    UpdateDreamerGroupRequest,
    UpdateDreamerRequest,
)
from app.utils.security import random_string


class DreamerService:
    def create_dreamer(self, request: NewDreamerRequest):
        create_response = dreamer_gateway.create_dreamer(
            {
                "organization_id": request.organization_id,
                "name_family": request.name_family,
                "name_given": request.name_given,
                "login_id": random_string(),
            }
        )
        self._ensure_success(create_response)
        return NewDreamerResponse.model_validate(create_response["data"])

    def get_dreamer(self, dreamer_id: str):
        dreamer_response = dreamer_gateway.get_dreamer(dreamer_id)
        if not dreamer_response["success"] or not dreamer_response["data"]:
            raise HTTPException(status_code=404, detail="dreamer が見つかりません")

        dreamer = dreamer_response["data"][0]
        members_response = dreamer_gateway.list_members_by_dreamer(dreamer_id)
        self._ensure_success(members_response)

        groups = []
        for member in members_response["data"]:
            group_response = dreamer_gateway.get_group(member.group_id)
            if group_response["success"] and group_response["data"]:
                group = group_response["data"][0]
                groups.append(
                    DreamerGroupSummary(name=group.name, group_id=group.group_id)
                )

        return DreamerResponse(
            login_id=dreamer.login_id,
            organization_id=dreamer.organization_id,
            name_family=dreamer.name_family,
            name_given=dreamer.name_given,
            groups=groups,
        )

    def update_dreamer(self, dreamer_id: str, request: UpdateDreamerRequest):
        response = dreamer_gateway.update_dreamer(
            dreamer_id, request.model_dump(exclude_unset=True)
        )
        if not response["success"]:
            raise HTTPException(status_code=500, detail=self._message(response))
        if not response["data"]:
            raise HTTPException(status_code=404, detail="dreamer が見つかりません")
        return DreamerResponse.model_validate(response["data"][0])

    def delete_dreamer(self, dreamer_id: str):
        delete_members_response = dreamer_gateway.delete_members_by_dreamer(dreamer_id)
        self._ensure_success(delete_members_response)

        delete_response = dreamer_gateway.delete_dreamer(dreamer_id)
        if not delete_response["success"] or not delete_response["data"]:
            raise HTTPException(status_code=404, detail="dreamer が見つかりません")
        return DreamerResponse.model_validate(delete_response["data"][0])

    def create_group(self, request: NewDreamerGroupRequest):
        for dreamer_id in request.dreamers:
            dreamer_response = dreamer_gateway.get_dreamer(str(dreamer_id))
            if not dreamer_response["success"] or not dreamer_response["data"]:
                raise HTTPException(status_code=400, detail="dreamer_id が存在しません")

        group_response = dreamer_gateway.create_group(
            {
                "name": request.name,
                "description": request.description,
            }
        )
        self._ensure_success(group_response)
        group_result = group_response["data"]

        for dreamer_id in request.dreamers:
            member_response = dreamer_gateway.create_group_member(
                {
                    "group_id": str(group_result.group_id),
                    "dreamer_id": str(dreamer_id),
                }
            )
            self._ensure_success(member_response)

        return NewDreamerGroupResponse.model_validate(group_result)

    def get_group(self, group_id: str):
        group_response = dreamer_gateway.get_group(group_id)
        if not group_response["success"] or not group_response["data"]:
            raise HTTPException(status_code=404, detail="group が見つかりません")

        group = group_response["data"][0]
        members_response = dreamer_gateway.list_members_by_group(group_id)
        self._ensure_success(members_response)

        dreamers = []
        for member in members_response["data"]:
            dreamer_response = dreamer_gateway.get_dreamer(member.dreamer_id)
            if dreamer_response["success"] and dreamer_response["data"]:
                dreamer = dreamer_response["data"][0]
                dreamers.append(
                    DreamerInGroup(
                        name=f"{dreamer.name_family} {dreamer.name_given}",
                        dreamer_id=dreamer.dreamer_id,
                    )
                )

        return DreamerGroupResponse(
            name=group.name, description=group.description, dreamers=dreamers
        )

    def update_group(self, group_id: str, request: UpdateDreamerGroupRequest):
        response = dreamer_gateway.update_group(
            group_id, request.model_dump(exclude_unset=True)
        )
        if not response["success"]:
            raise HTTPException(status_code=500, detail=self._message(response))
        if not response["data"]:
            raise HTTPException(status_code=404, detail="group が見つかりません")
        return DreamerGroupResponse.model_validate(response["data"][0])

    def delete_group(self, group_id: str):
        delete_members_response = dreamer_gateway.delete_members_by_group(group_id)
        self._ensure_success(delete_members_response)

        delete_response = dreamer_gateway.delete_group(group_id)
        if not delete_response["success"]:
            raise HTTPException(status_code=500, detail=self._message(delete_response))
        if not delete_response["data"]:
            raise HTTPException(status_code=404, detail="group が見つかりません")
        return DreamerGroupResponse.model_validate(delete_response["data"][0])

    def add_dreamer_to_group(self, group_id: str, request: DreamerToGroupRequest):
        added_dreamers = []
        for dreamer_id in request.dreamers:
            member_response = dreamer_gateway.create_group_member(
                {
                    "group_id": str(group_id),
                    "dreamer_id": str(dreamer_id),
                }
            )
            self._ensure_success(member_response)
            added_dreamers.append(member_response["data"])

        return DreamerToGroupResponse.model_validate(
            {"dreamers": [member.dreamer_id for member in added_dreamers]}
        )

    def remove_dreamer_from_group(self, group_id: str, request: DreamerToGroupRequest):
        deleted_ids = []
        for dreamer_id in request.dreamers:
            delete_response = dreamer_gateway.delete_group_member(
                group_id, str(dreamer_id)
            )
            if delete_response["success"] and delete_response["data"]:
                deleted_ids.append(dreamer_id)
        return DreamerToGroupResponse.model_validate({"dreamers": deleted_ids})

    def _ensure_success(self, response: dict):
        if response["success"]:
            return
        raise HTTPException(status_code=500, detail=self._message(response))

    def _message(self, response: dict):
        message = response.get("message", "gateway error")
        if isinstance(message, list):
            return ", ".join(message)
        return message


dreamer_service = DreamerService()
