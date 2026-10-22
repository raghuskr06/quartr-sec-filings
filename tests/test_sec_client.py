
import pytest

from sec_filings.config import Company
from sec_filings.sec_client import SecClient


@pytest.fixture
def company():
    return Company(
        ticker="TEST",
        name="Test Company, Inc.",
        cik="0000123456",
    )


@pytest.fixture
def client():
    return SecClient(email="test@example.com")


def make_submissions():
    return {
        "filings": {
            "recent": {
                "form": ["10-K", "10-K/A", "10-K"],
                "filingDate": [
                    "2023-02-15",
                    "2024-02-20",
                    "2024-02-10",
                ],
                "reportDate": [
                    "2022-12-31",
                    "2023-12-31",
                    "2023-12-31",
                ],
                "accessionNumber": [
                    "0000123456-23-000001",
                    "0000123456-24-000002",
                    "0000123456-24-000003",
                ],
                "primaryDocument": [
                    "annual-2022.htm",
                    "annual-amendment.htm",
                    "annual-2023.htm",
                ],
            }
        }
    }


def test_selects_latest_exact_10k(client, company, monkeypatch):
    monkeypatch.setattr(
        client,
        "get_submissions",
        lambda _company: make_submissions(),
    )

    filing = client.get_latest_10k(company)

    assert filing.ticker == "TEST"
    assert filing.filing_date.isoformat() == "2024-02-10"
    assert filing.report_date.isoformat() == "2023-12-31"
    assert filing.accession_number == "0000123456-24-000003"


def test_builds_correct_document_url(client, company, monkeypatch):
    monkeypatch.setattr(
        client,
        "get_submissions",
        lambda _company: make_submissions(),
    )

    filing = client.get_latest_10k(company)

    assert filing.document_url == (
        "https://www.sec.gov/Archives/edgar/data/"
        "123456/000012345624000003/annual-2023.htm"
    )


def test_raises_error_when_no_10k_exists(client, company, monkeypatch):
    submissions = {
        "filings": {
            "recent": {
                "form": ["8-K", "10-Q"],
                "filingDate": ["2024-01-10", "2024-02-10"],
                "reportDate": ["2024-01-10", "2024-01-31"],
                "accessionNumber": [
                    "0000123456-24-000001",
                    "0000123456-24-000002",
                ],
                "primaryDocument": ["report.htm", "quarterly.htm"],
            }
        }
    }

    monkeypatch.setattr(
        client,
        "get_submissions",
        lambda _company: submissions,
    )

    with pytest.raises(LookupError, match="No 10-K filing found"):
        client.get_latest_10k(company)


def test_rejects_missing_email():
    with pytest.raises(ValueError, match="contact email"):
        SecClient(email="")
