import os
import re
import time
from typing import Any

from dotenv import load_dotenv

from backend.schemas import DocumentRequest


load_dotenv()


SYSTEM_INSTRUCTION = """
You are LegalEase, an AI-assisted legal document drafting engine.

Draft clear, professional legal-document language from the supplied facts.

Do not invent:
- names
- dates
- money amounts
- addresses
- statutes
- court cases
- licenses
- other material facts

Do not claim that the document is:
- legally valid
- legally enforceable
- reviewed by a lawyer
- compliant with a particular jurisdiction
unless the user explicitly provides information supporting that claim.

Use this structure where appropriate:

TITLE

PARTIES

EFFECTIVE DATE

RECITALS

1. PURPOSE

2. TERMS AND OBLIGATIONS

3. CONFIDENTIALITY

4. PAYMENT / COMPENSATION

5. TERM AND TERMINATION

6. REPRESENTATIONS

7. DISPUTE / GOVERNING LAW

8. GENERAL PROVISIONS

SIGNATURES

Adapt the sections according to the requested document type.

Preserve every user-supplied term in substance.

If a section is not applicable, omit it.

Return only the document body in plain text.

Do not use Markdown code fences.
"""


DISCLAIMER = (
    "AI-generated draft for informational and drafting assistance only. "
    "It is not legal advice and has not been reviewed by a lawyer. "
    "Check the document against applicable law and have a qualified legal "
    "professional review it before signing or relying on it."
)


class GeminiDocumentGenerator:

    def __init__(self):
        self.api_key = os.getenv(
            "GEMINI_API_KEY",
            ""
        ).strip()

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.7-flash"
        ).strip()

        self.demo_mode = (
            os.getenv(
                "DEMO_MODE",
                "false"
            ).strip().lower() == "true"
        )

        self._client = None

        # Create Gemini client only when DEMO_MODE is disabled.
        if self.api_key and not self.demo_mode:
            try:
                from google import genai

                self._client = genai.Client(
                    api_key=self.api_key
                )

            except ImportError as exc:
                raise RuntimeError(
                    "google-genai is not installed. "
                    "Run: pip install -r requirements.txt"
                ) from exc

    # ---------------------------------------------------------
    # BUILD GEMINI PROMPT
    # ---------------------------------------------------------

    def _build_prompt(
        self,
        request: DocumentRequest
    ) -> str:

        terms = "\n".join(
            f"- {term}"
            for term in request.terms
        )

        prompt = f"""
{SYSTEM_INSTRUCTION}

DOCUMENT TYPE:
{request.document_type}

PARTIES:
{request.parties}

EFFECTIVE DATE:
{request.effective_date}

JURISDICTION:
{request.jurisdiction}

KEY TERMS:
{terms}

ADDITIONAL INSTRUCTIONS:
{request.additional_instructions or "None"}

Write the complete document draft now.
"""

        return prompt.strip()

    # ---------------------------------------------------------
    # GET DOCUMENT TITLE
    # ---------------------------------------------------------

    @staticmethod
    def _get_document_title(
        document_type: str
    ) -> str:

        doc_type = document_type.strip()
        lower_type = doc_type.lower()

        # NDA
        if (
            "non-disclosure" in lower_type
            or "nondisclosure" in lower_type
            or lower_type == "nda"
            or "(nda)" in lower_type
        ):
            return "NON-DISCLOSURE AGREEMENT"

        # Freelance
        if "freelance" in lower_type:
            return "FREELANCE WORK CONTRACT"

        # Employment
        if "employment" in lower_type:
            return "EMPLOYMENT AGREEMENT"

        # Service
        if "service" in lower_type:
            return "SERVICE AGREEMENT"

        # Partnership
        if "partnership" in lower_type:
            return "PARTNERSHIP AGREEMENT"

        # Consulting
        if "consult" in lower_type:
            return "CONSULTING AGREEMENT"

        # Rental / Lease
        if (
            "rental" in lower_type
            or "lease" in lower_type
        ):
            return "RENTAL / LEASE AGREEMENT"

        # Sale
        if "sale" in lower_type:
            return "SALE AGREEMENT"

        # Privacy
        if "privacy" in lower_type:
            return "PRIVACY AGREEMENT"

        # Terms
        if "terms" in lower_type:
            return "TERMS AND CONDITIONS"

        # Generic fallback
        return doc_type.upper()

    # ---------------------------------------------------------
    # GET PURPOSE
    # ---------------------------------------------------------

    @staticmethod
    def _get_purpose(
        document_type: str
    ) -> str:

        doc_type = document_type.strip()
        lower_type = doc_type.lower()

        # NDA
        if (
            "non-disclosure" in lower_type
            or "nondisclosure" in lower_type
            or lower_type == "nda"
            or "(nda)" in lower_type
        ):
            return (
                "The parties intend to enter into this "
                "non-disclosure agreement on the terms set out below."
            )

        # Freelance
        if "freelance" in lower_type:
            return (
                "The parties intend to enter into this "
                "freelance work contract on the terms set out below."
            )

        # Employment
        if "employment" in lower_type:
            return (
                "The parties intend to establish an employment "
                "relationship on the terms set out below."
            )

        # Service
        if "service" in lower_type:
            return (
                "The parties intend to establish the terms and "
                "conditions for the provision of services."
            )

        # Partnership
        if "partnership" in lower_type:
            return (
                "The parties intend to establish a business "
                "partnership on the terms set out below."
            )

        # Consulting
        if "consult" in lower_type:
            return (
                "The parties intend to establish the terms for "
                "the provision of consulting services."
            )

        # Generic fallback
        return (
            f"The parties intend to enter into this "
            f"{doc_type.lower()} on the terms set out below."
        )

    # ---------------------------------------------------------
    # DEMO DOCUMENT
    # ---------------------------------------------------------

    def _demo_document(
        self,
        request: DocumentRequest
    ) -> str:

        title = self._get_document_title(
            request.document_type
        )

        purpose = self._get_purpose(
            request.document_type
        )

        lines = [
            title,
            "",
            "PARTIES",
            request.parties.strip(),
            "",
            "EFFECTIVE DATE",
            request.effective_date.strip(),
            "",
            "1. PURPOSE",
            purpose,
            "",
            "2. TERMS AND OBLIGATIONS",
        ]

        # Add terms
        for term in request.terms:

            cleaned_term = str(term).strip()

            if not cleaned_term:
                continue

            # Avoid duplicate "-" if the user already entered one.
            if cleaned_term.startswith("-"):
                lines.append(cleaned_term)
            else:
                lines.append(
                    f"- {cleaned_term}"
                )

        lines.extend(
            [
                "",
                "3. GENERAL PROVISIONS",
                (
                    "The parties should review and complete "
                    "any provisions required for their circumstances."
                ),
                "",
                "SIGNATURES",
                (
                    "Party 1: ______________________________ "
                    "Date: ______________"
                ),
                (
                    "Party 2: ______________________________ "
                    "Date: ______________"
                ),
            ]
        )

        return "\n".join(lines)

    # ---------------------------------------------------------
    # GENERATE DOCUMENT
    # ---------------------------------------------------------

    def generate_document(
        self,
        request: DocumentRequest
    ) -> dict[str, Any]:

        prompt = self._build_prompt(request)

        # -----------------------------------------------------
        # DEMO MODE
        # -----------------------------------------------------

        if self.demo_mode:

            content = self._demo_document(
                request
            )

        # -----------------------------------------------------
        # GEMINI CLIENT NOT AVAILABLE
        # -----------------------------------------------------

        elif not self._client:

            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Add it to .env or set DEMO_MODE=true "
                "for local testing."
            )

        # -----------------------------------------------------
        # REAL GEMINI GENERATION
        # -----------------------------------------------------

        else:

            try:

                content = ""
                last_error = None

                # Retry transient Gemini errors.
                for attempt in range(3):

                    try:

                        response = (
                            self._client
                            .models
                            .generate_content(
                                model=self.model,
                                contents=prompt
                            )
                        )

                        content = (
                            response.text or ""
                        ).strip()

                        if content:
                            break

                        last_error = RuntimeError(
                            "Gemini returned an empty response."
                        )

                    except Exception as exc:

                        last_error = exc

                        error_text = str(
                            exc
                        ).upper()

                        # Retry temporary errors.
                        retryable = (
                            "503" in error_text
                            or "UNAVAILABLE" in error_text
                            or "429" in error_text
                            or "RESOURCE_EXHAUSTED" in error_text
                            or "QUOTA" in error_text
                        )

                        if not retryable:
                            raise

                    if attempt < 2:

                        # 2 seconds, then 4 seconds.
                        time.sleep(
                            2 ** (attempt + 1)
                        )

                if not content and last_error:
                    raise last_error

            except Exception as exc:

                raise RuntimeError(
                    "Gemini request failed. "
                    "Check GEMINI_API_KEY, GEMINI_MODEL, "
                    "quota/access and internet connection. "
                    f"Details: {exc}"
                ) from exc

        # -----------------------------------------------------
        # CHECK CONTENT
        # -----------------------------------------------------

        if not content:

            raise RuntimeError(
                "Gemini returned an empty document."
            )

        # -----------------------------------------------------
        # CLEAN OUTPUT
        # -----------------------------------------------------

        content = self._sanitize_model_output(
            content
        )

        # -----------------------------------------------------
        # EXTRACT TITLE
        # -----------------------------------------------------

        title = self._extract_title(
            content,
            request.document_type
        )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {
            "document_type": request.document_type,
            "title": title,
            "content": content,
            "terms": request.terms,
            "disclaimer": DISCLAIMER
        }

    # ---------------------------------------------------------
    # SANITIZE GEMINI OUTPUT
    # ---------------------------------------------------------

    @staticmethod
    def _sanitize_model_output(
        text: str
    ) -> str:

        if not text:
            return ""

        # Remove Markdown code fences.
        text = text.replace(
            "```text",
            ""
        )

        text = text.replace(
            "```plaintext",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        # Normalize line endings.
        text = text.replace(
            "\r\n",
            "\n"
        )

        text = text.replace(
            "\r",
            "\n"
        )

        # Remove excessive blank lines.
        #
        # IMPORTANT:
        # The correct regex is \n{4,}
        # NOT **\n**{4,}
        text = re.sub(
            r"\n{4,}",
            "\n\n\n",
            text
        )

        return text.strip()

    # ---------------------------------------------------------
    # EXTRACT TITLE
    # ---------------------------------------------------------

    @staticmethod
    def _extract_title(
        text: str,
        fallback: str
    ) -> str:

        first = next(
            (
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ),
            ""
        )

        if first:
            return first[:160]

        return fallback
