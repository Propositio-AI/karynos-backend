from fastapi import APIRouter

from crud import dreamer_crud, dreamer_group_crud, dreamer_group_members_crud
from schemas import (NewDreamerRequest, NewDreamerResponse, UpdateDreamerRequest,
                     DreamerResponse, NewDreamerGroupRequest, NewDreamerGroupResponse, 
                     DreamerGroupResponse, UpdateDreamerGroupRequest, DreamerToGroupRequest, 
                     DreamerToGroupResponse,DreamerInGroup)
from shared.utils.security import random_string
from models.DreamerTable import DreamerTableSchema
from models.DreamerGroupTable import DreamerGroupTableSchema
from models.DreamerGroupMembersTable import DreamerGroupMembersTableSchema


# /api/v1/dreamer
router = APIRouter()

# ================
# Dreamer Admin
# ================

@router.post("/admin/new", response_model=NewDreamerResponse)
async def create_dreamer(request: NewDreamerRequest):
    """新しいアカウントの作成"""
    _, result, error = dreamer_crud.create(DreamerTableSchema(**request.model_dump(), login_id = random_string()))
    print(error, flush=True)
    return NewDreamerResponse.model_validate(result)

@router.get("/admin/{dreamer_id}", response_model=DreamerResponse)
async def get_dreamer(dreamer_id: str):
    """dreamer情報の取得"""
    _, result, error =dreamer_crud.read(
        [
            ["dreamer_id", "==", dreamer_id]
        ] 
    )
    print(error, flush=True)
    return DreamerResponse.model_validate(result[0])

@router.put("/admin/{dreamer_id}", response_model=DreamerResponse)
async def update_dreamer(dreamer_id: str, request: UpdateDreamerRequest):
    """dreamer情報の更新"""
    _, result, error=dreamer_crud.update(
        [
            ["dreamer_id", "==", dreamer_id]
        ], 
    request.model_dump(exclude_unset=True)
    )
    print(error, flush=True)
    return DreamerResponse.model_validate(result[0])

@router.delete("/admin/{dreamer_id}", response_model=DreamerResponse)
async def delete_dreamer(dreamer_id: str):
    """dreamer情報の削除"""
    _, result, error=dreamer_crud.delete(
        [
            ["dreamer_id", "==", dreamer_id]
        ]
    )
    print(error, flush=True)
    return DreamerResponse.model_validate(result[0])

# ================
# Dreamer Groups
# ================

@router.post("/groups/new", response_model=NewDreamerGroupResponse)
async def create_group(request: NewDreamerGroupRequest):
    """新しいグループの作成"""
    group_data = request.model_dump(exclude={"dreamers"})
    group_instance = DreamerGroupTableSchema(**group_data)
    _, group_result, error = dreamer_group_crud.create(group_instance)
    print(error, flush=True)
    group_id = group_result.group_id

    # メンバー登録
    added_dreamers = []
    for dreamer_id in request.dreamers:
        member_instance = DreamerGroupMembersTableSchema(
            group_id=group_id,
            dreamer_id=dreamer_id
        )
        _, member_result, error = dreamer_group_members_crud.create(member_instance)
        print(error, flush=True)
        added_dreamers.append(member_result)

    return NewDreamerGroupResponse.model_validate(group_result)



@router.get("/groups/{group_id}", response_model=DreamerGroupResponse)
async def get_group(group_id: str):
    """グループ情報の取得"""
    _, group_result, error=dreamer_group_crud.read(
        [
            ["group_id","==",group_id]
        ]
    )
    print(error, flush=True)

    group=group_result[0]
    _, members, error=dreamer_group_members_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    dreamers=[DreamerInGroup(name=member.name, dreamer_id=member.dreamer_id)for member in members]
    print(error, flush=True)
    return DreamerGroupResponse(
        name=group.name,
        description=group.description,
        dreamers=dreamers
    )

@router.put("/groups/{group_id}", response_model=DreamerGroupResponse)
async def update_group(group_id: str, request: UpdateDreamerGroupRequest):
    """グループ情報の更新"""
    _, result, error=dreamer_group_crud.update(
        [
            ["group_id", "==", group_id]
        ],
        request.model_dump(exclude_unset=True)
    )
    print(error, flush=True)
    return DreamerGroupResponse.model_validate(result[0])

@router.delete("/groups/{group_id}", response_model=DreamerGroupResponse)
async def delete_group(group_id: str):
    """グループを削除"""
    _, result, error=dreamer_group_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    print(error, flush=True)
    return DreamerGroupResponse.model_validate(result[0])

#================
# Dreamer Group Members
#================

@router.put("/groups/{group_id}/add_dreamer", response_model=DreamerToGroupResponse)
async def add_dreamer_to_group(group_id: str, request: DreamerToGroupRequest):
    """グループにdreamerを追加"""
    added_dreamers = []

    for dreamer_id in request.dreamers:
        member_instance = DreamerGroupMembersTableSchema(
            group_id=group_id,
            dreamer_id=dreamer_id
        )
        _, member_result, error = dreamer_group_members_crud.create(member_instance)
        print(error, flush=True)
        added_dreamers.append(member_result)

    dreamer_ids = [member.dreamer_id for member in added_dreamers]
    return DreamerToGroupResponse.model_validate({"dreamers": dreamer_ids})


@router.delete("/groups/{group_id}/remove_dreamer", response_model=DreamerToGroupResponse)
async def remove_dreamer_from_group(group_id: str, request: DreamerToGroupRequest):
    """グループからdreamerを削除"""
    deleted_ids = []

    for dreamer_id in request.dreamers:
        _, result, error = dreamer_group_members_crud.delete(
            [
                ["group_id", "==", group_id],
                ["dreamer_id", "==", dreamer_id]
            ]
        )
        print(error, flush=True)
        if result:
            deleted_ids.append(dreamer_id)
    return DreamerToGroupResponse.model_validate({"dreamers": deleted_ids})