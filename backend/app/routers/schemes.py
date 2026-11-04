import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from backend.app.config import get_setting
from backend.app.schemas.scheme import (
    SchemeInput,
    SchemeListResponse,
    SchemeRecord,
)
from backend.app.schemas.scheme_agent import SchemeDiscoveryResponse
from backend.app.services import scheme_agent as scheme_agent_service
from backend.app.services import schemes as scheme_service


router = APIRouter(prefix="/api/schemes", tags=["Agriculture Schemes"])


def require_schemes_admin(
    x_schemes_admin_token: str | None = Header(default=None),
) -> None:
    expected_token = get_setting("AGROLENS_SCHEMES_ADMIN_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scheme management is not configured.",
        )
    if (
        x_schemes_admin_token is None
        or not secrets.compare_digest(x_schemes_admin_token, expected_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid schemes admin token is required.",
        )


@router.get(
    "",
    response_model=SchemeListResponse,
    summary="List agriculture schemes",
)
def list_schemes(
    government_level: str | None = Query(
        default=None, pattern="^(central|state)$"
    ),
    state: str | None = Query(default=None, min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    records, total = scheme_service.list_schemes(
        government_level=government_level,
        state=state,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(records),
        "total": total,
        "limit": limit,
        "offset": offset,
        "schemes": records,
    }


@router.post(
    "/agent/discover",
    response_model=SchemeDiscoveryResponse,
    summary="Refresh checks of allowlisted official scheme sources",
)
def discover_scheme_sources(
    refresh: bool = Query(default=False),
    _: None = Depends(require_schemes_admin),
):
    return scheme_agent_service.discover_sources(force_refresh=refresh)


@router.get(
    "/agent/discover",
    response_model=SchemeDiscoveryResponse,
    summary="Read cached official scheme source discovery",
)
def get_scheme_source_discovery():
    return scheme_agent_service.discover_sources()


@router.get(
    "/{scheme_id}",
    response_model=SchemeRecord,
    summary="Retrieve an agriculture scheme",
)
def get_scheme(scheme_id: str):
    scheme = scheme_service.get_scheme(scheme_id)
    if scheme is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agriculture scheme not found.",
        )
    return scheme


@router.post(
    "",
    response_model=SchemeRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Add a verified agriculture scheme",
)
def create_scheme(
    scheme: SchemeInput,
    _: None = Depends(require_schemes_admin),
):
    return scheme_service.create_scheme(scheme)


@router.put(
    "/{scheme_id}",
    response_model=SchemeRecord,
    summary="Update a verified agriculture scheme",
)
def update_scheme(
    scheme_id: str,
    scheme: SchemeInput,
    _: None = Depends(require_schemes_admin),
):
    updated = scheme_service.update_scheme(scheme_id, scheme)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agriculture scheme not found.",
        )
    return updated
