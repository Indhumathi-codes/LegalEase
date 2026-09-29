from io import BytesIO
from pathlib import Path
import html
import re
import textwrap

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from fpdf import FPDF


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"


# ============================================================
# DOCUMENT TITLE
# ============================================================

def get_clean_title(title: str) -> str:
    """
    Convert the selected document type into a clean display title.
    """

    if not title:
        return ""

    title = str(title).strip()
    lower_title = title.lower()

    # NDA
    if (
        "non-disclosure" in lower_title
        or "nondisclosure" in lower_title
        or lower_title == "nda"
        or "(nda)" in lower_title
    ):
        return "NON-DISCLOSURE AGREEMENT (NDA)"

    # Freelance
    if "freelance" in lower_title:
        return "FREELANCE WORK CONTRACT"

    # Employment
    if "employment" in lower_title:
        return "EMPLOYMENT AGREEMENT"

    # Service
    if "service" in lower_title:
        return "SERVICE AGREEMENT"

    # Partnership
    if "partnership" in lower_title:
        return "PARTNERSHIP AGREEMENT"

    # Consulting
    if "consult" in lower_title:
        return "CONSULTING AGREEMENT"

    # Rental / Lease
    if (
        "rental" in lower_title
        or "lease" in lower_title
    ):
        return "RENTAL / LEASE AGREEMENT"

    # Sale
    if "sale" in lower_title:
        return "SALE AGREEMENT"

    # Privacy
    if "privacy" in lower_title:
        return "PRIVACY AGREEMENT"

    # Terms
    if "terms" in lower_title:
        return "TERMS AND CONDITIONS"

    return title.upper()


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_document_text(text: str) -> str:
    """
    Clean generated document text while preserving useful
    line breaks and document structure.
    """

    if text is None:
        return ""

    text = str(text)

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove Markdown code fences
    text = text.replace("```text", "")
    text = text.replace("```plaintext", "")
    text = text.replace("```", "")

    # Remove Markdown bold markers
    text = text.replace("**", "")

    # Remove escaped Markdown characters
    text = text.replace(r"\*", "*")
    text = text.replace(r"\_", "_")

    # Remove escaped bullet markers
    text = re.sub(r"^\\-\s*", "- ", text, flags=re.MULTILINE)

    # Unicode replacements
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
        "\u200b": "",
        "\ufeff": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove excessive blank lines.
    # IMPORTANT: do not use the old invalid regex
    # r"**\n**{4,}"
    text = re.sub(
        r"\n{4,}",
        "\n\n\n",
        text
    )

    return text.strip()


def sanitize_text(text: str) -> str:
    """Compatibility wrapper."""
    return clean_document_text(text)


# ============================================================
# DUPLICATE TITLE REMOVAL
# ============================================================

def remove_duplicate_title(
    text: str,
    title: str
) -> str:
    """
    Remove a title from the beginning of generated content
    when the formatter is already adding the title.

    Also recognizes the shorter NDA title:
    NON-DISCLOSURE AGREEMENT
    when the selected title is:
    NON-DISCLOSURE AGREEMENT (NDA)
    """

    if not text:
        return ""

    text = clean_document_text(text)

    display_title = get_clean_title(title).strip().upper()

    lines = text.splitlines()

    result = []
    title_seen = False

    possible_titles = {
        display_title,
        display_title.replace(" (NDA)", ""),
        title.strip().upper(),
    }

    # Special NDA variants
    if "NON-DISCLOSURE AGREEMENT" in display_title:
        possible_titles.add(
            "NON-DISCLOSURE AGREEMENT"
        )
        possible_titles.add(
            "NON-DISCLOSURE AGREEMENT (NDA)"
        )

    for line in lines:

        stripped = line.strip()
        upper_line = stripped.upper()

        if upper_line in possible_titles:

            if not title_seen:
                title_seen = True

                # Do not keep the content title because the
                # formatter adds the title separately.
                continue

            continue

        result.append(line)

    return "\n".join(result).strip()


# ============================================================
# HEADING HELPERS
# ============================================================

MAIN_HEADING_PATTERN = re.compile(
    r"^(PARTIES|EFFECTIVE DATE|RECITALS|SIGNATURES)$|"
    r"^\d+\.\s+.+$",
    re.IGNORECASE
)

SUBSECTION_PATTERN = re.compile(
    r"^\d+\.\d+\s+.+$",
    re.IGNORECASE
)


def is_bullet(line: str) -> bool:
    return bool(
        re.match(
            r"^[-•]\s+",
            line.strip()
        )
    )


# ============================================================
# DOCX
# ============================================================

def create_docx(
    title: str,
    content: str,
    output_path=None,
):
    """
    Create a professionally formatted DOCX document.
    """

    title = get_clean_title(title)

    content = clean_document_text(content)

    content = remove_duplicate_title(
        content,
        title
    )

    document = Document()

    # --------------------------------------------------------
    # Page settings
    # --------------------------------------------------------

    section = document.sections[0]

    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    # --------------------------------------------------------
    # Normal font
    # --------------------------------------------------------

    normal_style = document.styles["Normal"]

    normal_style.font.name = "Arial"
    normal_style.font.size = Pt(10.5)

    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    if LOGO_PATH.exists():

        try:

            logo_paragraph = document.add_paragraph()

            logo_paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

            logo_paragraph.paragraph_format.space_after = Pt(3)

            run = logo_paragraph.add_run()

            run.add_picture(
                str(LOGO_PATH),
                width=Inches(0.75)
            )

        except Exception:
            pass

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title_paragraph = document.add_paragraph()

    title_paragraph.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    title_paragraph.paragraph_format.space_after = Pt(12)

    title_run = title_paragraph.add_run(
        title
    )

    title_run.bold = True
    title_run.font.name = "Arial"
    title_run.font.size = Pt(16)

    # --------------------------------------------------------
    # Content
    # --------------------------------------------------------

    for raw_line in content.splitlines():

        line = raw_line.strip()

        # Empty line
        if not line:

            paragraph = document.add_paragraph()

            paragraph.paragraph_format.space_after = Pt(2)

            continue

        # Safety: remove duplicate title
        if line.upper() in {
            title.upper(),
            "NON-DISCLOSURE AGREEMENT",
        } and "NON-DISCLOSURE" in title.upper():

            continue

        # ----------------------------------------------------
        # Main heading
        # ----------------------------------------------------

        if MAIN_HEADING_PATTERN.match(line):

            paragraph = document.add_paragraph()

            paragraph.paragraph_format.space_before = Pt(7)
            paragraph.paragraph_format.space_after = Pt(4)
            paragraph.paragraph_format.line_spacing = 1.0

            run = paragraph.add_run(line)

            run.bold = True
            run.font.name = "Arial"
            run.font.size = Pt(11.5)

        # ----------------------------------------------------
        # Subsection
        # ----------------------------------------------------

        elif SUBSECTION_PATTERN.match(line):

            paragraph = document.add_paragraph()

            paragraph.paragraph_format.space_before = Pt(5)
            paragraph.paragraph_format.space_after = Pt(3)

            run = paragraph.add_run(line)

            run.bold = True
            run.font.name = "Arial"
            run.font.size = Pt(10.5)

        # ----------------------------------------------------
        # Bullet
        # ----------------------------------------------------

        elif is_bullet(line):

            bullet_text = re.sub(
                r"^[-•]\s*",
                "",
                line
            )

            paragraph = document.add_paragraph(
                style="List Bullet"
            )

            paragraph.paragraph_format.left_indent = Inches(0.25)
            paragraph.paragraph_format.first_line_indent = Inches(-0.12)
            paragraph.paragraph_format.space_after = Pt(3)
            paragraph.paragraph_format.line_spacing = 1.05

            run = paragraph.add_run(
                bullet_text
            )

            run.font.name = "Arial"
            run.font.size = Pt(10.5)

        # ----------------------------------------------------
        # Normal paragraph
        # ----------------------------------------------------

        else:

            paragraph = document.add_paragraph()

            paragraph.paragraph_format.space_after = Pt(5)
            paragraph.paragraph_format.line_spacing = 1.08

            run = paragraph.add_run(line)

            run.font.name = "Arial"
            run.font.size = Pt(10.5)

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    footer = section.footer

    footer_paragraph = footer.paragraphs[0]

    footer_paragraph.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    footer_run = footer_paragraph.add_run(
        "LegalEase | AI-generated draft | Not legal advice"
    )

    footer_run.font.name = "Arial"
    footer_run.font.size = Pt(8)

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    if output_path:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        document.save(output_path)

        return output_path

    buffer = BytesIO()

    document.save(buffer)

    return buffer.getvalue()


# ============================================================
# PDF CLASS
# ============================================================

class LegalEasePDF(FPDF):

    def __init__(self):

        super().__init__()

        self.set_auto_page_break(
            auto=True,
            margin=20
        )

        self.set_margins(
            left=18,
            top=18,
            right=18
        )

        self.set_title(
            "LegalEase Document"
        )

        self.set_author(
            "LegalEase"
        )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    def header(self):

        # No header on first page.
        if self.page_no() == 1:
            return

        if LOGO_PATH.exists():

            try:

                self.image(
                    str(LOGO_PATH),
                    x=18,
                    y=8,
                    w=14
                )

                self.set_font(
                    "Helvetica",
                    "B",
                    9
                )

                self.set_xy(
                    36,
                    10
                )

                self.cell(
                    0,
                    5,
                    "LegalEase"
                )

                self.set_y(18)

            except Exception:
                pass

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    def footer(self):

        self.set_y(-15)

        self.set_font(
            "Helvetica",
            "",
            8
        )

        self.cell(
            0,
            5,
            f"LegalEase | AI draft | Page {self.page_no()}",
            align="C"
        )


# ============================================================
# PDF TEXT SAFETY
# ============================================================

def safe_pdf_text(text: str) -> str:
    """
    Convert text to a form that FPDF Helvetica can handle.

    IMPORTANT:
    We do NOT insert spaces every 18 characters.
    That was causing the PDF to wrap normal sentences
    into tiny pieces.

    Only genuinely long unbroken strings are split.
    """

    if text is None:
        return ""

    text = str(text)

    # --------------------------------------------------------
    # Unicode replacements
    # --------------------------------------------------------

    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
        "\u200b": "",
        "\ufeff": "",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    # --------------------------------------------------------
    # Convert unsupported characters
    # --------------------------------------------------------

    text = (
        text
        .encode(
            "latin-1",
            errors="replace"
        )
        .decode("latin-1")
    )

    # --------------------------------------------------------
    # Only break extremely long unbroken words.
    #
    # Normal sentences are NOT modified.
    # --------------------------------------------------------

    text = re.sub(
        r"(\S{45})(?=\S)",
        r"\1 ",
        text
    )

    return text


# ============================================================
# PDF LINE WRITER
# ============================================================

def pdf_write_line(
    pdf,
    line,
    font_size=10,
    bold=False,
    line_height=5.5,
):
    """
    Write a line using the full available PDF width.
    """

    line = safe_pdf_text(line)

    if not line:

        pdf.ln(3)

        return

    # --------------------------------------------------------
    # Font
    # --------------------------------------------------------

    style = "B" if bold else ""

    pdf.set_font(
        "Helvetica",
        style,
        font_size
    )

    # --------------------------------------------------------
    # Available width
    # --------------------------------------------------------

    available_width = (
        pdf.w
        - pdf.l_margin
        - pdf.r_margin
    )

    # --------------------------------------------------------
    # Wrap by characters.
    #
    # 95 is intentionally generous.
    # FPDF's multi_cell will perform final width wrapping.
    # --------------------------------------------------------

    wrapped_lines = textwrap.wrap(
        line,
        width=95,
        break_long_words=True,
        break_on_hyphens=False,
        replace_whitespace=False,
        drop_whitespace=True
    )

    if not wrapped_lines:
        wrapped_lines = [""]

    # --------------------------------------------------------
    # Write wrapped lines
    # --------------------------------------------------------

    for piece in wrapped_lines:

        piece = safe_pdf_text(piece)

        if not piece:
            continue

        pdf.multi_cell(
            w=available_width,
            h=line_height,
            text=piece,
            border=0,
            align="L",
            new_x="LMARGIN",
            new_y="NEXT"
        )


# ============================================================
# CREATE PDF
# ============================================================

def create_pdf(
    title: str,
    content: str,
    output_path=None,
):
    """
    Create a professionally formatted PDF.
    """

    title = get_clean_title(title)

    content = clean_document_text(content)

    content = remove_duplicate_title(
        content,
        title
    )

    # --------------------------------------------------------
    # Create PDF
    # --------------------------------------------------------

    pdf = LegalEasePDF()

    pdf.add_page()

    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    if LOGO_PATH.exists():

        try:

            pdf.image(
                str(LOGO_PATH),
                x=pdf.w - 35,
                y=10,
                w=17
            )

        except Exception:
            pass

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    pdf.ln(8)

    pdf_write_line(
        pdf,
        title,
        font_size=16,
        bold=True,
        line_height=8
    )

    pdf.ln(5)

    # --------------------------------------------------------
    # Body
    # --------------------------------------------------------

    for raw_line in content.splitlines():

        line = raw_line.strip()

        # ----------------------------------------------------
        # Empty line
        # ----------------------------------------------------

        if not line:

            pdf.ln(3)

            continue

        # ----------------------------------------------------
        # Remove duplicate title
        # ----------------------------------------------------

        if (
            line.upper() == title.upper()
            or (
                "NON-DISCLOSURE AGREEMENT" in title.upper()
                and line.upper() == "NON-DISCLOSURE AGREEMENT"
            )
        ):

            continue

        # ----------------------------------------------------
        # Main heading
        # ----------------------------------------------------

        if MAIN_HEADING_PATTERN.match(line):

            pdf.ln(2)

            pdf_write_line(
                pdf,
                line,
                font_size=11,
                bold=True,
                line_height=6
            )

            pdf.ln(1)

        # ----------------------------------------------------
        # Subsection
        # ----------------------------------------------------

        elif SUBSECTION_PATTERN.match(line):

            pdf.ln(1)

            pdf_write_line(
                pdf,
                line,
                font_size=10,
                bold=True,
                line_height=5.5
            )

            pdf.ln(1)

        # ----------------------------------------------------
        # Bullet
        # ----------------------------------------------------

        elif is_bullet(line):

            bullet_text = re.sub(
                r"^[-•]\s*",
                "",
                line
            )

            # Use an actual bullet-like dash.
            bullet_line = (
                "- " + bullet_text
            )

            pdf_write_line(
                pdf,
                bullet_line,
                font_size=10,
                bold=False,
                line_height=5.5
            )

        # ----------------------------------------------------
        # Normal paragraph
        # ----------------------------------------------------

        else:

            pdf_write_line(
                pdf,
                line,
                font_size=10,
                bold=False,
                line_height=5.5
            )

    # --------------------------------------------------------
    # Generate bytes
    # --------------------------------------------------------

    pdf_bytes = bytes(
        pdf.output()
    )

    # --------------------------------------------------------
    # Save if requested
    # --------------------------------------------------------

    if output_path:

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path.write_bytes(
            pdf_bytes
        )

        return output_path

    return pdf_bytes


# ============================================================
# TXT
# ============================================================

def create_txt(
    title: str,
    content: str,
    output_path=None,
):

    title = get_clean_title(title)

    content = clean_document_text(content)

    content = remove_duplicate_title(
        content,
        title
    )

    final_text = (
        f"{title}\n\n"
        f"{content}\n"
    )

    if output_path:

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path.write_text(
            final_text,
            encoding="utf-8"
        )

        return output_path

    return final_text.encode(
        "utf-8"
    )


# ============================================================
# FORMATTERS USED BY FRONTEND
# ============================================================

def format_docx(
    text,
    doc_type
):

    return create_docx(
        title=doc_type,
        content=text
    )


def format_pdf(
    text,
    doc_type
):

    return create_pdf(
        title=doc_type,
        content=text
    )


def format_txt(
    text,
    doc_type=None
):

    # Frontend currently calls:
    #
    # format_txt(edited)
    #
    # so support that too.

    if doc_type is None:

        cleaned = clean_document_text(
            text
        )

        return cleaned.encode(
            "utf-8"
        )

    return create_txt(
        title=doc_type,
        content=text
    )


# ============================================================
# HTML PREVIEW
# ============================================================

def format_html_preview(text):

    text = sanitize_text(text)

    html_parts = []

    for line in text.splitlines():

        line = line.strip()

        # Empty line
        if not line:

            html_parts.append(
                "<br>"
            )

            continue

        escaped = html.escape(
            line
        )

        # ----------------------------------------------------
        # Main headings
        # ----------------------------------------------------

        if MAIN_HEADING_PATTERN.match(line):

            html_parts.append(
                f"<h3>{escaped}</h3>"
            )

        # ----------------------------------------------------
        # Bullet
        # ----------------------------------------------------

        elif is_bullet(line):

            bullet_text = re.sub(
                r"^[-•]\s*",
                "",
                escaped
            )

            html_parts.append(
                f"<p>• {bullet_text}</p>"
            )

        # ----------------------------------------------------
        # Subsection
        # ----------------------------------------------------

        elif SUBSECTION_PATTERN.match(line):

            html_parts.append(
                f"<strong>{escaped}</strong>"
            )

        # ----------------------------------------------------
        # Normal paragraph
        # ----------------------------------------------------

        else:

            html_parts.append(
                f"<p>{escaped}</p>"
            )

    return "\n".join(
        html_parts
    )
