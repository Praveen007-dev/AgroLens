import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from backend.app.config import get_setting
from backend.app.schemas.news import NewsInput, NewsListResponse, NewsRecord
from backend.app.schemas.news_agent import NewsCollectionResponse
from backend.app.services import news as news_service
from backend.app.services import news_agent as news_agent_service


router = APIRouter(prefix="/api/news", tags=["Agriculture News"])


def require_news_admin(
    x_news_admin_token: str | None = Header(default=None),
) -> None:
    expected_token = get_setting("AGROLENS_NEWS_ADMIN_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="News management is not configured.",
        )
    if (
        x_news_admin_token is None
        or not secrets.compare_digest(x_news_admin_token, expected_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid news admin token is required.",
        )


@router.get(
    "",
    response_model=NewsListResponse,
    summary="List agriculture news articles",
)
def list_news(
    category: str | None = Query(default=None, min_length=1, max_length=100),
    region: str | None = Query(default=None, min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    articles, total = news_service.list_news(
        category=category,
        region=region,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(articles),
        "total": total,
        "limit": limit,
        "offset": offset,
        "articles": articles,
    }


@router.post(
    "/agent/collect",
    response_model=NewsCollectionResponse,
    summary="Collect agriculture releases from the official PIB page",
)
def collect_pib_news(
    limit: int = Query(
        default=news_agent_service.MAX_PAGE_SIZE,
        ge=1,
        le=news_agent_service.MAX_PAGE_SIZE,
    ),
    _: None = Depends(require_news_admin),
):
    try:
        return news_agent_service.collect_news(limit=limit)
    except news_agent_service.NewsCollectionError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error


@router.get(
    "/{news_id}",
    response_model=NewsRecord,
    summary="Retrieve an agriculture news article",
)
def get_article(news_id: str):
    article = news_service.get_article(news_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agriculture news article not found.",
        )
    return article


@router.post(
    "",
    response_model=NewsRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Import an agriculture news article",
)
def create_article(
    article: NewsInput,
    _: None = Depends(require_news_admin),
):
    try:
        return news_service.create_article(article)
    except news_service.DuplicateArticleError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An article with this URL already exists.",
        ) from error


@router.put(
    "/{news_id}",
    response_model=NewsRecord,
    summary="Update an agriculture news article",
)
def update_article(
    news_id: str,
    article: NewsInput,
    _: None = Depends(require_news_admin),
):
    try:
        updated = news_service.update_article(news_id, article)
    except news_service.DuplicateArticleError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An article with this URL already exists.",
        ) from error
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agriculture news article not found.",
        )
    return updated
