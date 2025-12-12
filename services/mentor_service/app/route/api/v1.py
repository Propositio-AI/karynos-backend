from fastapi import APIRouter, HTTPException

from crud import mentors_crud, mentor_groups_crud, mentor_group_members_crud
from schemas import (
    NewMentorRequest, NewMentorResponse, UpdateMentorRequest, MentorResponse,
    NewMentorGroupRequest, NewMentorGroupResponse, MentorGroupResponse,
    UpdateMentorGroupRequest, AddMentorToGroupRequest, AddMentorToGroupResponse, 
    MentorInGroup, MentorRoleInfo, RemoveMentorFromGroupRequest, RemoveMentorResponse
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
        _, chief_result, error = mentors_crud.read(
            [["mentor_id", "==", request.chief_mentor_id]]
        )
        if not chief_result:
            raise HTTPException(status_code=400, detail="chief_mentor_id が存在しません")
        
    # organization_id の存在確認
    client = Client()
    org_url = f"http://organization-service:8000/api/v1/organization/{request.organization_id}"
    success, _, error = client.get(org_url)
    if not success:
        raise HTTPException(status_code=400, detail="organization_id が存在しません")
    
    # access_group が指定されている場合、存在確認
    if request.access_group:
        _, group_result, error = mentor_groups_crud.read(
            [["group_id", "==", request.access_group]]
        )
        if not group_result:
            raise HTTPException(status_code=400, detail="access_group が存在しません")
    
    _, result, error = mentors_crud.create(
        MentorTableSchema(**request.model_dump(), login_id=random_string())
    )
    print(error, flush=True)
    return NewMentorResponse.model_validate(result)



@router.get("/admin/{mentor_id}", response_model=MentorResponse)
async def get_mentor(mentor_id: str):
    """Mentor情報を取得"""
    _, result, error = mentors_crud.read(
        [
            ["mentor_id", "==", mentor_id]
        ]
    )
    print(error, flush=True)
    return MentorResponse.model_validate(result[0])


@router.put("/admin/{mentor_id}", response_model=MentorResponse)
async def update_mentor(mentor_id: str, request: UpdateMentorRequest):
    """Mentor情報を更新"""
    _, result, error = mentors_crud.update(
        [
            ["mentor_id", "==", mentor_id]
        ],
        request.model_dump(exclude_unset=True)
    )
    print(error, flush=True)
    return MentorResponse.model_validate(result[0])


@router.delete("/admin/{mentor_id}", response_model=MentorResponse)
async def delete_mentor(mentor_id: str):
    """Mentor情報を削除"""
    _, result, error = mentors_crud.delete(
        [
            ["mentor_id", "==", mentor_id]
        ]
    )
    print(error, flush=True)
    return MentorResponse.model_validate(result[0])

# ====================
# Mentor Groups
# ====================

@router.post("/groups/new", response_model=NewMentorGroupResponse)
async def create_group(request: NewMentorGroupRequest):
    """新しいMentorグループを作成"""
    # chief_mentor_id が指定されている場合、存在確認
    if request.chief_mentor_id:
        _, chief_result, error = mentors_crud.read(
            [["mentor_id", "==", request.chief_mentor_id]]
        )
        if not chief_result:
            raise HTTPException(status_code=400, detail="chief_mentor_id が存在しません")
    
    group_data = request.model_dump(exclude={"mentors"})
    group_instance = MentorGroupTableSchema(**group_data)
    _, group_result, error = mentor_groups_crud.create(group_instance)
    print(error, flush=True)
    group_id = group_result.group_id

    """メンバー登録"""
    added_mentors = []
    for mentor_info in request.mentors:
        member_data = {
            "group_id": group_id,
            "mentor_id": mentor_info.mentor_id,
            "role": mentor_info.role
        }
        _, member_result, error = mentor_group_members_crud.create(member_data)
        print(error, flush=True)
        added_mentors.append(member_result)
    return NewMentorGroupResponse.model_validate(group_result)


@router.get("/groups/{group_id}", response_model=MentorGroupResponse)
async def get_group(group_id: str):
    """Mentorグループの情報を取得"""
    _, group_result, error = mentor_groups_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    print(error, flush=True)
    group = group_result[0]

    _, members, error = mentor_group_members_crud.read(
        [
            ["group_id", "==", group_id]
        ]
    )
    print(error, flush=True)
    mentors = [MentorInGroup(name=member.name, mentor_id=member.mentor_id) for member in members]
    return MentorGroupResponse(
        name=group.name,
        description=group.description,
        mentors=mentors
    )


@router.put("/groups/{group_id}", response_model=MentorGroupResponse)
async def update_group(group_id: str, request: UpdateMentorGroupRequest):
    """Mentorグループの情報を更新"""
    _, result, error = mentor_groups_crud.update(
        [
            ["group_id", "==", group_id]
        ],
        request.model_dump(exclude_unset=True)
    )
    print(error, flush=True)
    return MentorGroupResponse.model_validate(result[0])


@router.delete("/groups/{group_id}", response_model=MentorGroupResponse)
async def delete_group(group_id: str):
    """Mentorグループを削除"""
    # まずグループのメンバーを全て削除
    _, _, error = mentor_group_members_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    print(error, flush=True)

    # グループを削除
    _, result, error = mentor_groups_crud.delete(
        [
            ["group_id", "==", group_id]
        ]
    )
    print(error, flush=True)
    return MentorGroupResponse.model_validate(result[0])

# ====================
# Mentor Group Members
# ====================

@router.post("/groups/{group_id}/add_mentor", response_model=AddMentorToGroupResponse)
async def add_mentor_to_group(group_id: str, request: AddMentorToGroupRequest):
    """メンターをグループに追加"""
    added_mentors = []
    for mentor_info in request.mentors:
        member_instance = MentorGroupMemberTableSchema(
            group_id=group_id,
            mentor_id=mentor_info.mentor_id,
            role=mentor_info.role
        )
        _, result, error = mentor_group_members_crud.create(member_instance)
        print(error, flush=True)
        added_mentors.append(MentorRoleInfo(mentor_id=result.mentor_id, role=result.role))
    return AddMentorToGroupResponse(mentors=added_mentors)


@router.delete("/groups/{group_id}/remove_mentor", response_model=RemoveMentorResponse)
async def remove_mentor_from_group(group_id: str, request: RemoveMentorFromGroupRequest):
    """Mentorをグループから削除"""
    removed_mentor_ids = []
    for mentor_id in request.mentor_ids:
        _, result, error = mentor_group_members_crud.delete(
            [
                ["group_id", "==", group_id],
                ["mentor_id", "==", mentor_id]
            ]
        )
        print(error, flush=True)
        if result:
            removed_mentor_ids.append(mentor_id)
    return RemoveMentorResponse(mentor_ids=removed_mentor_ids)
