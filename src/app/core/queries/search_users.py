import logging
from dataclasses import dataclass

from app.core.common.authorization.current_user_service import CurrentUserService
from app.core.queries.models.user import ListUsersQm
from app.core.queries.ports.user_reader import UserReader
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class SearchUsersRequest:
    query: str
    page: int
    page_size: int


class SearchUsers:
    """
    - Open to admins.
    - Searches users whose username contains the given text (case-insensitive).
    - Pages are 1-based.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_reader: UserReader,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_reader = user_reader

    async def execute(self, request: SearchUsersRequest) -> ListUsersQm:
        logger.info("Search users: started. Query: '%s'.", request.query)

        current_user = await self._current_user_service.get_current_user()
        logger.debug("Search users requested by '%s'.", current_user.id_)

        pagination = OffsetPaginationParams(
            limit=request.page_size,
            offset=request.page * request.page_size,
        )
        users = await self._user_reader.search_by_username(
            query=request.query,
            pagination=pagination,
        )

        logger.info("Search users: done.")
        return users
