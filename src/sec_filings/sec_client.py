
from dataclasses import dataclass
from datetime import date

import requests

from sec_filings.config import Company


SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"


@dataclass(frozen=True)
class Filing:
    ticker: str
    company_name: str
    filing_date: date
    report_date: date | None
    accession_number: str
    document_url: str


class SecClient:
    def __init__(self, email: str) -> None:
        if not email or "@" not in email:
            raise ValueError("A valid contact email is required.")

        self.session = requests.Session()
        self.session.headers.update(
    {
        "User-Agent": f"QuartrSecFilings contact {email}",
        "Accept-Encoding": "gzip, deflate",
    }
)
        self.timeout = 30

    def get_submissions(self, company: Company) -> dict:
        url = SEC_SUBMISSIONS_URL.format(cik=company.cik)

        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        return response.json()

    def get_latest_10k(self, company: Company) -> Filing:
        submissions = self.get_submissions(company)
        recent = submissions.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        primary_documents = recent.get("primaryDocument", [])

        matching_indices = [
            index
            for index, form in enumerate(forms)
            if form == "10-K"
            and index < len(filing_dates)
            and index < len(accession_numbers)
            and index < len(primary_documents)
            and filing_dates[index]
            and accession_numbers[index]
            and primary_documents[index]
        ]

        if not matching_indices:
            raise LookupError(
                f"No 10-K filing found for {company.ticker} "
                "in the SEC's recent filings."
            )

        latest_index = max(
            matching_indices,
            key=lambda index: filing_dates[index],
        )

        filing_date = date.fromisoformat(filing_dates[latest_index])
        report_date_value = (
            report_dates[latest_index]
            if latest_index < len(report_dates)
            else ""
        )
        report_date = (
            date.fromisoformat(report_date_value)
            if report_date_value
            else None
        )

        accession_number = accession_numbers[latest_index]
        accession_for_url = accession_number.replace("-", "")
        cik_for_url = str(int(company.cik))
        primary_document = primary_documents[latest_index]

        document_url = (
            f"{SEC_ARCHIVES_URL}/{cik_for_url}/"
            f"{accession_for_url}/{primary_document}"
        )

        return Filing(
            ticker=company.ticker,
            company_name=company.name,
            filing_date=filing_date,
            report_date=report_date,
            accession_number=accession_number,
            document_url=document_url,
        )
