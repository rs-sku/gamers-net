from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, Field

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100


class Pagination(BaseModel):
    limit: int = Field(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)
    offset: int = Field(0, ge=0)


def get_pagination(
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Pagination:
    return Pagination(limit=limit, offset=offset)


PaginationDep = Annotated[Pagination, Depends(get_pagination)]
