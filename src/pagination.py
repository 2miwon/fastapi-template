from typing import Annotated

from fastapi import Depends, Query

from src.schemas import CustomModel


class PaginationParams(CustomModel):
    limit: int
    offset: int


class Page[T](CustomModel):
    items: list[T]
    total: int
    limit: int
    offset: int


async def pagination_params(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


Pagination = Annotated[PaginationParams, Depends(pagination_params)]
