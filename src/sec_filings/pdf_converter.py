
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

from sec_filings.sec_client import Filing


class PdfConverter:
    def __init__(
        self,
        session: requests.Session,
        timeout: int = 60,
    ) -> None:
        self.session = session
        self.timeout = timeout

    def convert(self, filing: Filing, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = (
            f"{filing.ticker}_{filing.filing_date.isoformat()}.pdf"
        )
        output_path = output_dir / filename
        temporary_path = output_dir / f"{filename}.tmp"

        response = self.session.get(
            filing.document_url,
            timeout=self.timeout,
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        if (
            "html" not in content_type
            and not response.text.lstrip().startswith("<")
        ):
            raise ValueError(
                f"The SEC response for {filing.ticker} "
                "does not appear to be HTML."
            )

        html = response.text

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page()

                page.set_content(
                    html,
                    wait_until="load",
                    timeout=self.timeout * 1000,
                )

                page.pdf(
                    path=str(temporary_path),
                    format="Letter",
                    landscape=True,
                    print_background=True,
                    prefer_css_page_size=True,
                )

                browser.close()

            with temporary_path.open("rb") as pdf_file:
                if pdf_file.read(5) != b"%PDF-":
                    raise ValueError(
                        "The generated file is not a valid PDF."
                    )

            temporary_path.replace(output_path)

        finally:
            if temporary_path.exists():
                temporary_path.unlink()

        return output_path
