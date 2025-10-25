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
    _, newOrganization, error = organization_crud.create(request)

    return NewOrganizationResponse.model_validate(newOrganization)

@router.get("/", response_model=OrganizationListResponse)
async def _(organization_type: OrganizationType = None):
    _, organizations, error = organization_crud.read([
        ["organization_type", "==", organization_type]
    ])

    return OrganizationListResponse(
        organizations = [OrganizationListItem.model_validate(o) for o in organizations]
    )

@router.get("/{organization_id}/name", response_model=OrganizationNameResponse)
async def _(organization_id:int):
    _, organizations, error = organization_crud.read([
        ["organization_id", "==", organization_id]
    ])

    return OrganizationNameResponse.model_validate(organizations[0])

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def _(organization_id: int):
    _, organizations, error = organization_crud.read([
        ["organization_id", "==", organization_id]
    ])

    return OrganizationResponse.model_validate(organizations[0])

@router.put("/{organization_id}", response_model=UpdateOrganizationResponse)
async def _(organization_id: int, request: UpdateOrganizationRequest):
    _, updateOrganization, error = organization_crud.update(
        [
            ["organization_id", "==", organization_id]
        ],
        request.model_dump(exclude_none=True)
    )

    return UpdateOrganizationResponse.model_validate(updateOrganization[0])

@router.delete("/{organization_id}", response_model=OrganizationResponse)
async def _(organization_id: int):
    _, organizations, error = organization_crud.delete([
        ["organization_id", "==", organization_id]
    ])

    return OrganizationResponse.model_validate(organizations[0])
