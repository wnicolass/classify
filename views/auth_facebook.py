import os
import httpx
from typing import Annotated
from urllib.parse import quote_plus as quote
from dotenv import (
    load_dotenv,
    find_dotenv
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter,
    Request,
    Depends,
    responses,
    status,
    HTTPException
)
from jose import jwt
from services import user_service
from common.auth import (
    get_session,
    requires_unauthentication,
    ExternalLoginError,
    set_current_user,
    hash_sub
)
from common.fastapi_utils import get_db_session
from common.utils import (
    is_ascii,
    generate_csrf_token,
    generate_nonce
)