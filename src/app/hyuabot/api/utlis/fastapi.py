import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncIterator

from fastapi import Request
from sqlalchemy.orm import Session

from app.hyuabot.api.context import AppContext


_SQLA_SESSION_CLOSER_THREADPOOL = ThreadPoolExecutor(1)


async def get_db_session(request: Request) -> AsyncIterator[Session]:
    db_engine = AppContext.from_app(request.app).db_engine
    loop = asyncio.get_event_loop()
    session = Session(db_engine)

    try:
        yield session
    finally:
        await loop.run_in_executor(_SQLA_SESSION_CLOSER_THREADPOOL, session.close)
