from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query
from starlette import status

from app.core.common.authorization.exceptions import AuthorizationError
from app.core.queries.models.user import ListUsersQm
from app.core.queries.query_support.exceptions import PaginationError
from app.core.queries.search_users import SearchUsers, SearchUsersRequest
from app.inbound.http.errors.callbacks import log_info
from app.inbound.http.errors.router import make_error_aware_router
from app.inbound.http.errors.rules import HTTP_503_SERVICE_UNAVAILABLE_RULE
from app.outbound.auth_ctx.exceptions import AuthenticationError
from app.outbound.exceptions import ReaderError


def make_search_users_router() -> APIRouter:
    router = make_error_aware_router(on_error=log_info)

    @router.get(
        "/search",
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            PaginationError: status.HTTP_400_BAD_REQUEST,
            ReaderError: HTTP_503_SERVICE_UNAVAILABLE_RULE,
        },
        status_code=status.HTTP_200_OK,
        description=getdoc(SearchUsers),
    )
    @inject
    async def search_users(
        q: Annotated[str, Query(min_length=1)],
        interactor: FromDishka[SearchUsers],
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> ListUsersQm:
        return await interactor.execute(
            SearchUsersRequest(query=q, page=page, page_size=page_size),
        )

    return router
