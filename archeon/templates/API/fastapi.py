# @archeon:file
# @glyph {GLYPH_QUALIFIED_NAME}
# @intent {ENDPOINT_INTENT}
# @chain {CHAIN_REFERENCE}

# @archeon:section imports
# External dependencies and internal modules
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
{IMPORTS}
# @archeon:endsection

router = APIRouter(prefix="{ROUTE_PREFIX}", tags=["{TAG}"])

# @archeon:section models
# Request/response Pydantic models

class {REQUEST_MODEL}(BaseModel):
{REQUEST_FIELDS}


class {RESPONSE_MODEL}(BaseModel):
{RESPONSE_FIELDS}


class {ERROR_MODEL}(BaseModel):
    detail: str
    code: str
# @archeon:endsection

# @archeon:section endpoint
# {METHOD} {ROUTE} endpoint handler

@router.{METHOD}("{ROUTE}")
async def {HANDLER_NAME}(
{PARAMETERS}
) -> {RESPONSE_MODEL}:
    """
    {DOCSTRING}
    """
{HANDLER_BODY}
# @archeon:endsection
