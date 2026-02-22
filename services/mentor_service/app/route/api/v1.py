from fastapi import APIRouter, HTTPException

from crud import mentors_crud, mentor_groups_crud, mentor_group_members_crud
from schemas import (
    NewMentorRequest, NewMentorResponse, UpdateMentorRequest, MentorResponse,
    NewMentorGroupRequest, NewMentorGroupResponse, MentorGroupResponse,
    UpdateMentorGroupRequest, AddMentorToGroupRequest, AddMentorToGroupResponse, MentorGroupInfo,
    MentorInGroup, MentorRoleInfo, RemoveMentorFromGroupRequest, RemoveMentorFromGroupResponse
)
from models.MentorsTable import MentorTableSchema
from models.MentorGroupsTable import MentorGroupTableSchema
from models.MentorGroupMembersTable import MentorGroupMemberTableSchema
from shared.utils.security import random_string
from shared.lib.API import Client

# /api/v1/mentor
router = APIRouter()

# ====================
# Mentor Admin
# ====================

@router.post("/admin/new", response_model=NewMentorResponse)
async def create_mentor(request: NewMentorRequest):
    """新しいMentorアカウントを作成"""
    
    # chief_mentor_id が指定されている場合、存在確認
    if request.chief_mentor_id:
        chief_response = mentors_crud.read(
            [["mentor_id", "==", request.chief_mentor_id]]
        )
        if not chief_response["success"] or not chief_response["data"]:
            raise HTTPException(status_code=400, detail="chief_mentor_id が存在しません")
        
    # organization_id の存在確認
    client = Client()
    org_url = f"http://organization-service:8000/api/v1/organization/{request.organization_id}"
    org_response = client.get(org_url)
    if not org_response["success"]:
        raise HTTPException(status_code=400, detail="organization_id が存在しません")
    
    # access_group が指定されている場合、存在確認
    if request.access_group:
        group_response = mentor_groups_crud.read(
            [["group_id", "==", request.access_group]]
        )
        if not group_response["success"] or not group_response["data"]:
            raise HTTPException(status_code=400, detail="access_group が存在しません")
    
    mentor_response = mentors_crud.create(
        MentorTableSchema(**request.model_dump(), login_id=random_string())
    )
    if not mentor_response["success"]:
        raise HTTPException(status_code=500, detail=mentor_response["message"])
    result = mentor_response["data"]
    
    # access_group が指定されている場合、そのグループにメンバーとして追加
    if request.access_group:
        member_instance = MentorGroupMemberTableSchema(
            group_id=request.access_group,
            mentor_id=result.mentor_id,
            role=request.access_group_role or "member"
        )
        member_response = mentor_group_members_crud.create(member_instance)
        if not member_response["success"]:
            raise HTTPException(status_code=500, detail=member_response["message"])
    
    return NewMentorResponse.model_validate(result)


@router.get("/admin/{mentor_id}", response_model=MentorResponse)
async def get_mentor(mentor_id: str):
    """Mentor情報を取得"""
    mentor_response = mentors_crud.read(
        [
            ["mentor_id", "==", mentor_id]
        ]
    )
    if not mentor_response["success"] or not mentor_response["data"]:
        raise HTTPException(status_code=404, detail="mentor が見つかりません")

    mentor = mentor_response["data"][0]
    
    # mentorが所属するグループを取得
    members_response = mentor_group_members_crud.read(
        [
            ["mentor_id", "==", mentor_id]
        ]
    )
    if not members_response["success"]:
        raise HTTPException(status_code=500, detail=members_response["message"])
    members = members_response["data"]
    
    # グループ情報を取得
    groups = []
    if members:
        for member in members:
            group_response = mentor_groups_crud.read(
                [
                    ["group_id", "==", member.group_id]
                ]
            )
            if group_response["success"] and group_response["data"]:
                group = group_response["data"][0]
                groups.append(MentorGroupInfo(name=group.name, group_id=group.group_id))
    
    return MentorResponse(
        login_id=mentor.login_id,
        chief_mentor_id=mentor.chief_mentor_id,
        organization_id=mentor.organization_id,
        name_family=mentor.name_family,
        name_given=mentor.name_given,
        access_group=mentor.access_group,
        group=groups
    )


@router.put("/admin/{mentor_id}", response_model=MentorResponse)
async def update_mentor(mentor_id: str, request: UpdateMentorRequest):
    """Mentor情報を更新"""
    update_response = mentors_crud.update(
        [
            ["mentor_id", "==", mentor_id]
        ],
        request.model_dump(exclude_unset=True)
    )
    if not update_response["success"] or not update_response["data"]:
        raise HTTPException(status_code=500, detail=update_response["message"])
    return MentorResponse.model_validate(update_response["data"][0])


@router.delete("/admin/{mentor_id}", response_model=MentorResponse)
async def delete_mentor(mentor_id: str):
    """Mentor情報を削除"""
    # 所属している全グループから削除
    delete_members_response = mentor_group_members_crud.delete(
        [
            ["mentor_id", "==", mentor_id]
        ]
    )
    if not delete_members_response["success"]:
        raise HTTPException(status_code=500, detail=delete_members_response["message"])
    
    # mentorを削除
    delete_mentor_response = mentors_crud.delete(
        [
            ["mentor_id", "==", mentor_id]
        ]
    )
    if not delete_mentor_response["success"] or not delete_mentor_response["data"]:
        raise HTTPException(status_code=404, detail="mentor が見つかりません")
    return MentorResponse.model_validate(delete_mentor_response["data"][0])

# ====================
# Mentor Groups
# ====================

@router.post("/groups/new", response_model=NewMentorGroupResponse)
async def create_group(request: NewMentorGroupRequest):
    """新しいMentorグループを作成"""
    # chief_mentor_id が指定されている場合、存在確認
    if request.chief_mentor_id:
        chief_response = mentors_crud.read(
            [["mentor_id", "==", request.chief_mentor_id]]
        )
        if not chief_response["success"] or not chief_response["data"]:
            raise HTTPException(status_code=400, detail="chief_mentor_id が存在しません")

    # メンバーに指定された mentor_id を事前に全件確認（存在しなければ 400）
    for mentor_info in request.mentors:
        mentor_response = mentors_crud.read(
            [["mentor_id", "==", mentor_info.mentor_id]]
        )
        if not mentor_response["success"] or not mentor_response["data"]:
            raise HTTPException(status_code=400, detail="mentor_id が存在しません")
    
    group_data = request.model_dump(exclude={"mentors"})
    group_instance = MentorGroupTableSchema(**group_data)
    group_response = mentor_groups_crud.create(group_instance)
    if not group_response["success"]:
        raise HTTPException(status_code=500, detail=group_response["message"])
    group_result = group_response["data"]
    group_id = group_result.group_id

    """メンバー登録"""
    added_mentors = []
    for mentor_info in request.mentors:
        member_instance = MentorGroupMemberTableSchema(
            group_id=group_id,
            mentor_id=mentor_info.mentor_id,
            role=mentor_info.role
        )
        member_response = mentor_group_members_crud.create(member_instance)
        if not member_response["success"]:
            raise HTTPException(status_code=500, detail=member_response["message"])
        added_mentors.append(member_response["data"])
    return NewMentorGroupResponse.model_validate(group_result)


@router.get("/groups/{group_id}", response_model=MentorGroupResponse)
async def get_group(group_id: str):
    """Mentorグループの情報を取得"""
    group_response = mentor_groups_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    if not group_response["success"] or not group_response["data"]:
        raise HTTPException(status_code=404, detail="group が見つかりません")
    
    group = group_response["data"][0]

    members_response = mentor_group_members_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    if not members_response["success"]:
        raise HTTPException(status_code=500, detail=members_response["message"])
    members = members_response["data"]
    
    # 各メンバーのmentor情報を取得
    mentors = []
    if members:
        for member in members:
            mentor_response = mentors_crud.read(
                [
                    ["mentor_id", "==", member.mentor_id]
                ]
            )
            if mentor_response["success"] and mentor_response["data"]:
                mentor = mentor_response["data"][0]
                full_name = f"{mentor.name_family} {mentor.name_given}"
                mentors.append(MentorInGroup(name=full_name, mentor_id=mentor.mentor_id))
    
    return MentorGroupResponse(
        chief_mentor_id=group.chief_mentor_id,
        name=group.name,
        description=group.description,
        mentors=mentors
    )


@router.put("/groups/{group_id}", response_model=MentorGroupResponse)
async def update_group(group_id: str, request: UpdateMentorGroupRequest):
    """Mentorグループの情報を更新"""
    update_response = mentor_groups_crud.update(
        [
            ["group_id", "==", group_id]
        ],
        request.model_dump(exclude_unset=True)
    )
    if not update_response["success"] or not update_response["data"]:
        raise HTTPException(status_code=500, detail=update_response["message"])
    return MentorGroupResponse.model_validate(update_response["data"][0])


@router.delete("/groups/{group_id}", response_model=MentorGroupResponse)
async def delete_group(group_id: str):
    """Mentorグループを削除"""
    # まずグループのメンバーを全て削除
    delete_members_response = mentor_group_members_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    if not delete_members_response["success"]:
        raise HTTPException(status_code=500, detail=delete_members_response["message"])

    # グループを削除
    delete_group_response = mentor_groups_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    if not delete_group_response["success"] or not delete_group_response["data"]:
        raise HTTPException(status_code=500, detail=delete_group_response["message"])
    return MentorGroupResponse.model_validate(delete_group_response["data"][0])

# ====================
# Mentor Group Members
# ====================

@router.post("/groups/{group_id}/add_mentor", response_model=AddMentorToGroupResponse)
async def add_mentor_to_group(group_id: str, request: AddMentorToGroupRequest):
    """メンターをグループに追加"""
    # 追加対象メンターの存在確認（外部キー違反防止）
    for mentor_info in request.mentors:
        mentor_response = mentors_crud.read(
            [["mentor_id", "==", mentor_info.mentor_id]]
        )
        if not mentor_response["success"] or not mentor_response["data"]:
            raise HTTPException(status_code=400, detail="mentor_id が存在しません")

    added_mentors = []
    for mentor_info in request.mentors:
        member_instance = MentorGroupMemberTableSchema(
            group_id=group_id,
            mentor_id=mentor_info.mentor_id,
            role=mentor_info.role
        )
        member_response = mentor_group_members_crud.create(member_instance)
        if not member_response["success"]:
            raise HTTPException(status_code=500, detail=member_response["message"])
        member = member_response["data"]
        added_mentors.append(MentorRoleInfo(mentor_id=member.mentor_id, role=member.role))
    return AddMentorToGroupResponse(mentors=added_mentors)


@router.delete("/groups/{group_id}/remove_mentor", response_model=RemoveMentorFromGroupResponse)
async def remove_mentor_from_group(group_id: str, request: RemoveMentorFromGroupRequest):
    """Mentorをグループから削除"""
    removed_mentor_ids = []
    for mentor_id in request.mentor_ids:
        delete_response = mentor_group_members_crud.delete(
            [
                ["group_id", "==", group_id],
                ["mentor_id", "==", mentor_id]
            ]
        )
        if delete_response["success"] and delete_response["data"]:
            removed_mentor_ids.append(mentor_id)
    return RemoveMentorFromGroupResponse(mentor_ids=removed_mentor_ids)
