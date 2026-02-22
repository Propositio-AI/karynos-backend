from fastapi import APIRouter
from crud import organization_crud
from schemas import (
    NewOrganizationRequest, NewOrganizationResponse,
    OrganizationNameResponse,
    OrganizationListResponse,
    OrganizationResponse,
    UpdateOrganizationRequest, UpdateOrganizationResponse,

    OrganizationType,
    OrganizationListItem
)

# /api/v1/organization

router = APIRouter()

@router.post("/", response_model=NewOrganizationResponse)
async def _(request: NewOrganizationRequest):
    response = organization_crud.create(request)
    if not response["success"]:
        raise Exception(response["message"])

    return NewOrganizationResponse.model_validate(response["data"])

@router.get("/", response_model=OrganizationListResponse)
async def _(organization_type: OrganizationType = None):
    response = organization_crud.read([
        ["organization_type", "==", organization_type]
    ])

    if not response["success"]:
        raise Exception(response["message"])

    return OrganizationListResponse(
        organizations = [OrganizationListItem.model_validate(o) for o in response["data"]]
    )

@router.get("/{organization_id}/name", response_model=OrganizationNameResponse)
async def _(organization_id:int):
    response = organization_crud.read([
        ["organization_id", "==", organization_id]
    ])

    if not response["success"] or not response["data"]:
        raise Exception(response["message"])

    return OrganizationNameResponse.model_validate(response["data"][0])

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def _(organization_id: int):
    response = organization_crud.read([
        ["organization_id", "==", organization_id]
    ])

    if not response["success"] or not response["data"]:
        raise Exception(response["message"])

    return OrganizationResponse.model_validate(response["data"][0])

@router.put("/{organization_id}", response_model=UpdateOrganizationResponse)
async def _(organization_id: int, request: UpdateOrganizationRequest):
    response = organization_crud.update(
        [
            ["organization_id", "==", organization_id]
        ],
        request.model_dump(exclude_none=True)
    )

    if not response["success"] or not response["data"]:
        raise Exception(response["message"])

    return UpdateOrganizationResponse.model_validate(response["data"][0])

@router.delete("/{organization_id}", response_model=OrganizationResponse)
async def _(organization_id: int):
    response = organization_crud.delete([
        ["organization_id", "==", organization_id]
    ])

    if not response["success"] or not response["data"]:
        raise Exception(response["message"])

    return OrganizationResponse.model_validate(response["data"][0])
