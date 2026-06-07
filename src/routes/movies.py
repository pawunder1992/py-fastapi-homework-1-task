from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import get_db, models

router = APIRouter()


@router.get(
    "/movies/{movie_id}/", response_model=schemas.MovieDetailResponseSchema
)
async def read_detail_movie(
    movie_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    db_movie = await db.scalar(
        select(models.MovieModel).where(models.MovieModel.id == movie_id)
    )

    if not db_movie:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )

    return db_movie


@router.get("/movies/", response_model=schemas.MovieListResponseSchema)
async def get_movies(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
):

    total_count = await db.scalar(select(func.count(models.MovieModel.id)))
    total_pages = ceil(total_count / per_page)

    offset = (page - 1) * per_page
    query = select(models.MovieModel).offset(offset).limit(per_page)
    result = await db.execute(query)
    movies = result.scalars().all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    base_url = "/theater/movies/"
    prev_page = (
        f"{base_url}?page={page - 1}&per_page={per_page}"
        if (page > 1)
        else None
    )
    next_page = (
        f"{base_url}?page={page + 1}&per_page={per_page}"
        if (page < total_pages)
        else None
    )

    return {
        "movies": movies,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": total_count,
    }
