from fastapi import APIRouter, HTTPException

from backend.schemas import (
    DocumentRequest,
    DocumentResponse
)

from ai_core.gemini_generator import (
    GeminiDocumentGenerator
)


router = APIRouter(
    tags=["documents"]
)


generator = GeminiDocumentGenerator()


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    request: DocumentRequest
):

    try:

        result = generator.generate_document(
            request
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected generation error: {exc}"
        )
