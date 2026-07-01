from fastapi import APIRouter

from app.services.dreamer.schemas import (
    DreamerGroupResponse,
    DreamerResponse,
    DreamerToGroupRequest,
    DreamerToGroupResponse,
    NewDreamerGroupRequest,
    NewDreamerGroupResponse,
    NewDreamerRequest,
    NewDreamerResponse,
    TestLoginRequest,
    TestLoginResponse,
    UpdateDreamerGroupRequest,
    UpdateDreamerRequest,
)
from app.services.dreamer.service import dreamer_service

router = APIRouter()


@router.post("/test-login", response_model=TestLoginResponse)
def test_login(request: TestLoginRequest):
    return dreamer_service.test_login(request)


@router.post("/admin/new", response_model=NewDreamerResponse)
def create_dreamer(request: NewDreamerRequest):
    return dreamer_service.create_dreamer(request)


@router.get("/admin/{dreamer_id}", response_model=DreamerResponse)
def get_dreamer(dreamer_id: str):
    return dreamer_service.get_dreamer(dreamer_id)


@router.put("/admin/{dreamer_id}", response_model=DreamerResponse)
def update_dreamer(dreamer_id: str, request: UpdateDreamerRequest):
    return dreamer_service.update_dreamer(dreamer_id, request)


@router.delete("/admin/{dreamer_id}", response_model=DreamerResponse)
def delete_dreamer(dreamer_id: str):
    return dreamer_service.delete_dreamer(dreamer_id)


@router.post("/groups/new", response_model=NewDreamerGroupResponse)
def create_group(request: NewDreamerGroupRequest):
    return dreamer_service.create_group(request)


@router.get("/groups/{group_id}", response_model=DreamerGroupResponse)
def get_group(group_id: str):
    return dreamer_service.get_group(group_id)


@router.put("/groups/{group_id}", response_model=DreamerGroupResponse)
def update_group(group_id: str, request: UpdateDreamerGroupRequest):
    return dreamer_service.update_group(group_id, request)


@router.delete("/groups/{group_id}", response_model=DreamerGroupResponse)
def delete_group(group_id: str):
    return dreamer_service.delete_group(group_id)


@router.put("/groups/{group_id}/add_dreamer", response_model=DreamerToGroupResponse)
def add_dreamer_to_group(group_id: str, request: DreamerToGroupRequest):
    return dreamer_service.add_dreamer_to_group(group_id, request)


@router.delete(
    "/groups/{group_id}/remove_dreamer", response_model=DreamerToGroupResponse
)
def remove_dreamer_from_group(group_id: str, request: DreamerToGroupRequest):
    return dreamer_service.remove_dreamer_from_group(group_id, request)
