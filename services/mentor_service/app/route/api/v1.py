from fastapi import APIRouter

from crud import mentors_crud, mentor_groups_crud, mentor_group_members_crud
from schemas import (
    NewMentorRequest, NewMentorResponse, UpdateMentorRequest, MentorResponse,
    NewMentorGroupRequest, NewMentorGroupResponse, MentorGroupResponse,
    UpdateMentorGroupRequest, MentorToGroupRequest, MentorToGroupResponse, 
    MentorInGroup,MentorRoleInfo
)
from models.MentorsTable import MentorTableSchema
from models.MentorGroupsTable import MentorGroupTableSchema
from shared.utils.security import random_string

# /api/v1/mentor
router = APIRouter()

# ====================
# Mentor Admin
# ====================

@router.post("/admin/new", response_model=NewMentorResponse)
async def create_mentor(request: NewMentorRequest):
    """新しいMentorアカウントを作成"""
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
            "role": mentor_info.mentor_id
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

@router.post("/groups/{group_id}/add_mentor", response_model=MentorToGroupResponse)
async def add_mentor_to_group(group_id: str, request: MentorToGroupRequest):
    """Mentorをグループに追加"""
    added_mentors = []
    for mentor_info in request.mentors:
        data = {
            "group_id": group_id,
            "mentor_id": mentor_info.mentor_id,
            "role": mentor_info.role
            }
        _, result, error = mentor_group_members_crud.create(data)
        print(error, flush=True)
        added_mentors.append(MentorRoleInfo(mentor_id=result.mentor_id, role=result.role))
    return MentorToGroupResponse(mentors=added_mentors)


@router.post("/groups/{group_id}/remove_mentor", response_model=MentorToGroupResponse)
async def remove_mentor_from_group(group_id: str, request: MentorToGroupRequest):
    """Mentorをグループから削除"""
    removed_mentors=[]
    for mentor_id in request.mentors:
        _, result, error = mentor_group_members_crud.delete(
            [
                ["group_id", "==", group_id],
                ["mentor_id", "==", mentor_id]
            ]
        )
    print(error, flush=True)
    if result:
        removed_mentors.append(MentorRoleInfo(mentor_id=mentor_id, role="member"))
    return MentorToGroupResponse(mentors=result)
