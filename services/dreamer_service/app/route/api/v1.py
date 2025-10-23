from fastapi import APIRouter
from app.crud import dreamer_crud, dreamer_group_crud, dreamer_group_members_crud
from schemas import (NewDreamerRequest, NewDreamerResponse, UpdateDreamerRequest,
                     DreamerResponse, NewDreamerGroupRequest, NewDreamerGroupResponse, 
                     DreamerGroupResponse, UpdateDreamerGroupRequest, DreamerToGroupRequest, 
                     DreamerToGroupResponse)

# /api/v1/dreamer
router = APIRouter()

# ================
# Dreamer Admin
# ================

@router.post("/admin/new", response_model=NewDreamerResponse)
async def create_dreamer(request: NewDreamerRequest):
    """新しいアカウントの作成"""
    _, result, _=dreamer_crud.create(request)
    return result

@router.get("/admin/{dreamer_id}", response_model=DreamerResponse)
async def get_dreamer(dreamer_id: str):
    """dreamer情報の取得"""
    _, result, _=dreamer_crud.read(
        [
            ["dreamer_id", "==", dreamer_id]
        ] 
    )
    return result[0] if result else None

@router.put("/admin/{dreamer_id}", response_model=DreamerResponse)
async def update_dreamer(dreamer_id: str, request: UpdateDreamerRequest):
    """dreamer情報の更新"""
    _, result, _=dreamer_crud.update(
        [
            ["dreamer_id", "==", dreamer_id]
        ], 
    request.model_dump(exclude_unset=True)
    )
    return result

@router.delete("/admin/{dreamer_id}", response_model=DreamerResponse)
async def delete_dreamer(dreamer_id: str):
    """dreamer情報の削除"""
    _, result, _=dreamer_crud.delete(
        [
            ["dreamer_id", "==", dreamer_id]
        ]
    )
    return result[0] if result else None

# ================
# Dreamer Groups
# ================

@router.post("/groups/new", response_model=NewDreamerGroupResponse)
async def create_group(request: NewDreamerGroupRequest):
    """新しいグループの作成"""
    _, result, _=dreamer_group_crud.create(request)
    return result

@router.get("/groups/{group_id}", response_model=DreamerGroupResponse)
async def get_group(group_id: str):
    """グループ情報の取得"""
    _, result, _=dreamer_group_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    return result[0] if result else None

@router.put("/groups/{group_id}", response_model=DreamerGroupResponse)
async def update_group(group_id: str, request: UpdateDreamerGroupRequest):
    """グループ情報の更新"""
    _, result, _=dreamer_group_crud.update(
        [
            ["group_id", "==", group_id]
        ],
        request.model_dump(exclude_unset=True)
    )
    return result

@router.delete("/groups/{group_id}", response_model=DreamerGroupResponse)
async def delete_group(group_id: str):
    """グループを削除"""
    _, result, _=dreamer_group_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    return result[0] if result else None

#================
# Dreamer Group Members
#================

@router.post("/groups/{group_id}/add_dreamer", response_model=DreamerToGroupResponse)
async def add_dreamer_to_group(group_id: str, request: DreamerToGroupRequest):
    """グループにdreamerを追加"""
    added_dreamers=[]
    for dreamer_id in request.dreamers:
        data={"group_id": group_id, "dreamer_id": dreamer_id}
        _, result, _=dreamer_group_members_crud.create(data)
        added_dreamers.append(result)
    return {"dreamers": added_dreamers}

@router.post("/groups/{group_id}/remove_dreamer", response_model=DreamerToGroupResponse)
async def remove_dreamer_from_group(group_id: str, request: DreamerToGroupRequest):
    """グループからdreamerを削除"""
    _, result, _=dreamer_group_members_crud.delete(
        [
            ["group_id", "==", group_id],
            ["dreamer_id", "in", request.dreamers]
        ]
    )
    return {"dreamers": result}
