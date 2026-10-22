
from datetime import date
from unittest.mock import Mock

import pytest

from sec_filings.pdf_converter import PdfConverter
from sec_filings.sec_client import Filing


@pytest.fixture
def filing():
    return Filing(
        ticker="TEST",
        company_name="Test Company, Inc.",
        filing_date=date(2025, 10, 31),
        report_date=date(2025, 9, 27),
        accession_number="0000123456-25-000001",
        document_url="https://www.sec.gov/example.htm",
    )


@pytest.fixture
def session():
    mock_session = Mock()
    response = Mock()
    response.headers = {"Content-Type": "text/html"}
    response.text = "<html><body>Test filing</body></html>"
    response.raise_for_status.return_value = None
    mock_session.get.return_value = response
    return mock_session


def test_converter_rejects_non_html_response(filing, tmp_path):
    session = Mock()
    response = Mock()
    response.headers = {"Content-Type": "application/pdf"}
    response.text = "This is not HTML."
    response.raise_for_status.return_value = None
    session.get.return_value = response

    converter = PdfConverter(session=session)

    with pytest.raises(ValueError, match="does not appear to be HTML"):
        converter.convert(filing, tmp_path)

    session.get.assert_called_once_with(
        filing.document_url,
        timeout=60,
    )


def test_converter_creates_output_directory(
    filing, tmp_path, session, monkeypatch
):
    output_dir = tmp_path / "nested" / "output"

    class FakePage:
        def set_content(self, html, **kwargs):
            assert html == "<html><body>Test filing</body></html>"

        def pdf(self, path, **kwargs):
            with open(path, "wb") as pdf_file:
                pdf_file.write(b"%PDF-test")

    class FakeBrowser:
        def new_page(self):
            return FakePage()

        def close(self):
            pass

    class FakeChromium:
        def launch(self):
            return FakeBrowser()

    class FakePlaywright:
        chromium = FakeChromium()

    class FakePlaywrightContext:
        def __enter__(self):
            return FakePlaywright()

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(
        "sec_filings.pdf_converter.sync_playwright",
        lambda: FakePlaywrightContext(),
    )

    converter = PdfConverter(session=session)
    result = converter.convert(filing, output_dir)

    assert output_dir.is_dir()
    assert result.name == "TEST_2025-10-31.pdf"
    assert result.read_bytes().startswith(b"%PDF-")
