from fastapi import APIRouter
from schemas import (NewDreamerRequest, NewDreamerResponse, UpdateDreamerRequest,
                     DreamerResponse, NewDreamerGroupRequest, NewDreamerGroupResponse, 
                     DreamerGroupResponse, UpdateDreamerGroupRequest, DreamerToGroupRequest, 
                     DreamerToGroupResponse)

# /api/v1/dreamer
router = APIRouter(prefix="/v1", tags=["dreamer"])

# ================
# Admin
# ================

@router.post("/admin/new", response_model=NewDreamerResponse)
async def create_dreamer(dreamer: NewDreamerRequest):
    """新しいアカウントの作成"""
    pass

@router.get("/admin/{dreamer_id}", response_model=DreamerResponse)
async def get_dreamer(dreamer_id: str):
    """dreamer情報の取得"""
    pass

@router.put("/admin/{dreamer_id}", response_model=DreamerResponse)
async def update_dreamer(dreamer_id: str, dreamer: UpdateDreamerRequest):
    """dreamer情報の更新"""
    pass

@router.delete("/admin/{dreamer_id}", response_model=DreamerResponse)
async def delete_dreamer(dreamer_id: str):
    """deramer情報の削除"""
    pass

# ================
# Group
# ================

@router.post("/groups/new", response_model=NewDreamerGroupResponse)
async def create_group(group: NewDreamerGroupRequest):
    """新しいグループの作成"""
    pass

@router.get("/groups/{group_id}", response_model=DreamerGroupResponse)
async def get_group(group_id: str):
    """グループ情報の取得"""
    pass

@router.put("/groups/{group_id}", response_model=DreamerGroupResponse)
async def update_group(group_id: str, group: UpdateDreamerGroupRequest):
    """グループ情報の更新"""
    pass

@router.delete("/groups/{group_id}", response_model=DreamerGroupResponse)
async def delete_group(group_id: str):
    """グループを削除"""
    pass

#================
# Group Member
#================

@router.post("/groups/{group_id}/add_dreamer", response_model=DreamerToGroupResponse)
async def add_dreamer_to_group(group_id: str, request: DreamerToGroupRequest):
    """グループにdreamerを追加"""
    pass

@router.post("/groups/{group_id}/remove_dreamer", response_model=DreamerToGroupResponse)
async def remove_dreamer_from_group(group_id: str, request: DreamerToGroupRequest):
    """グループからdreamerを削除"""
    pass
