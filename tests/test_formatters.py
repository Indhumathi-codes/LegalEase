from document_utils.formatters import (
    format_docx,
    format_pdf,
    format_txt,
    sanitize_text
)


def test_sanitize_text():

    assert (
        sanitize_text(
            "“Hello” – world"
        )
        == '"Hello" - world'
    )


def test_txt_export():

    result = format_txt(
        "TEST DOCUMENT"
    )

    assert (
        b"TEST DOCUMENT"
        in result
    )


def test_docx_export():

    result = format_docx(
        "TEST DOCUMENT\n\n1. TERMS\nPayment",
        "Agreement"
    )

    assert result[:2] == b"PK"


def test_pdf_export():

    result = format_pdf(
        "TEST DOCUMENT\n\n1. TERMS\nPayment",
        "Agreement"
    )

    assert result.startswith(
        b"%PDF"
    )
