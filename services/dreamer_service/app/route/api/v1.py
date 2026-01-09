from fastapi import APIRouter, HTTPException

from crud import dreamer_crud, dreamer_group_crud, dreamer_group_members_crud
from schemas import (NewDreamerRequest, NewDreamerResponse, UpdateDreamerRequest,
                     DreamerResponse, NewDreamerGroupRequest, NewDreamerGroupResponse, 
                     DreamerGroupResponse, UpdateDreamerGroupRequest, DreamerToGroupRequest, 
                     DreamerToGroupResponse,DreamerInGroup,DreamerGroupSummary)
from shared.utils.security import random_string
from shared.lib.API import Client
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
    # organizationが存在するか事前チェック（存在しないIDでの登録を防止）
    client = Client()
    org_url = f"http://organization-service:8000/api/v1/organization/{request.organization_id}"
    success, _, error = client.get(org_url)
    if not success:
        raise HTTPException(status_code=400, detail="organization_id が存在しません")

    _, result, error = dreamer_crud.create(DreamerTableSchema(**request.model_dump(), login_id = random_string()))
    print(error, flush=True)
    return NewDreamerResponse.model_validate(result)


@router.get("/admin/{login_id}", response_model=DreamerResponse)
async def get_dreamer(login_id: str):
    """dreamer情報の取得"""
    _, result, error = dreamer_crud.read(
        [
            ["login_id", "==", login_id]
        ] 
    )
    dreamer = result[0]
    
    # dreamerが所属するグループを取得
    _, members, error = dreamer_group_members_crud.read(
        [
            ["dreamer_id", "==", dreamer.dreamer_id]
        ]
    )
    print(error, flush=True)
    
    # グループ情報を取得
    groups = []
    if members:
        for member in members:
            _, group_result, error = dreamer_group_crud.read(
                [
                    ["group_id", "==", member.group_id]
                ]
            )
            if group_result:
                group = group_result[0]
                groups.append(DreamerGroupSummary(name=group.name, group_id=group.group_id))
    
    return DreamerResponse(
        dreamer_id=dreamer.dreamer_id,
        login_id=dreamer.login_id,
        organization_id=dreamer.organization_id,
        name_family=dreamer.name_family,
        name_given=dreamer.name_given,
        groups=groups
    )


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
    # 所属している全グループから削除
    _, _, error = dreamer_group_members_crud.delete(
        [
            ["dreamer_id", "==", dreamer_id]
        ]
    )
    print(error, flush=True)
    
    # dreamerを削除
    _, result, error=dreamer_crud.delete(
        [
            ["dreamer_id", "==", dreamer_id]
        ]
    )
    print(error, flush=True)
    if not result:
        raise HTTPException(status_code=404, detail="dreamer が見つかりません")
    return DreamerResponse.model_validate(result[0])

# ================
# Dreamer Groups
# ================

@router.post("/groups/new", response_model=NewDreamerGroupResponse)
async def create_group(request: NewDreamerGroupRequest):
    """新しいグループの作成"""
    # メンバーに指定された dreamer_id を事前に全件確認（存在しなければ 400）
    for dreamer_id in request.dreamers:
        _, dreamer_result, error = dreamer_crud.read(
            [["dreamer_id", "==", dreamer_id]]
        )
        if not dreamer_result:
            raise HTTPException(status_code=400, detail="dreamer_id が存在しません")

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
    _, group_result, error = dreamer_group_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    print(error, flush=True)

    group = group_result[0]
    _, members, error = dreamer_group_members_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    print(error, flush=True)
    
    # 各メンバーのdreamer情報を取得
    dreamers = []
    if members:
        for member in members:
            _, dreamer_result, error = dreamer_crud.read(
                [
                    ["dreamer_id", "==", member.dreamer_id]
                ]
            )
            if dreamer_result:
                dreamer = dreamer_result[0]
                full_name = f"{dreamer.name_family} {dreamer.name_given}"
                dreamers.append(DreamerInGroup(name=full_name, dreamer_id=dreamer.dreamer_id))
        
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
    # グループのメンバーを全て削除
    _, _, error = dreamer_group_members_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    print(error, flush=True)
    
    # グループを削除
    _, result, error = dreamer_group_crud.delete(
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
    # グループの存在確認
    _, group_result, error = dreamer_group_crud.read(
        [["group_id", "==", group_id]]
    )
    if not group_result:
        raise HTTPException(status_code=404, detail="group が見つかりません")

    # 追加対象 dreamer_id を事前に全件確認（外部キー違反防止）
    for dreamer_id in request.dreamers:
        _, dreamer_result, error = dreamer_crud.read(
            [["dreamer_id", "==", dreamer_id]]
        )
        if not dreamer_result:
            raise HTTPException(status_code=400, detail="dreamer_id が存在しません")

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