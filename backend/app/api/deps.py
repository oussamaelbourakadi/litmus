"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

# Annotated dependency avoids a function call in argument defaults (ruff B008).
DbSession = Annotated[AsyncSession, Depends(get_db)]
