
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from sec_filings.config import COMPANIES
from sec_filings.pdf_converter import PdfConverter
from sec_filings.sec_client import SecClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download the latest SEC 10-K filings as PDFs."
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="Optional list of tickers, for example: AAPL META",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where PDFs and manifest.json will be saved.",
    )
    parser.add_argument(
        "--email",
        default=os.getenv("SEC_USER_EMAIL"),
        help="Contact email for the SEC User-Agent; alternatively set SEC_USER_EMAIL.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.email:
        print(
            "Error: provide --email or set the SEC_USER_EMAIL environment variable."
        )
        return 1

    requested_tickers = (
        {ticker.upper() for ticker in args.tickers}
        if args.tickers
        else None
    )

    if requested_tickers is None:
        companies = COMPANIES
    else:
        companies = tuple(
            company
            for company in COMPANIES
            if company.ticker in requested_tickers
        )
        unknown_tickers = requested_tickers - {
            company.ticker for company in companies
        }
        if unknown_tickers:
            print(
                "Error: unknown ticker(s): "
                + ", ".join(sorted(unknown_tickers))
            )
            return 1

    client = SecClient(email=args.email)
    converter = PdfConverter(session=client.session)
    results = []

    for company in companies:
        print(f"\nProcessing {company.ticker} — {company.name}")

        result = {
            "ticker": company.ticker,
            "company_name": company.name,
            "status": "failed",
            "filing_date": None,
            "report_date": None,
            "accession_number": None,
            "document_url": None,
            "pdf_path": None,
            "error": None,
        }

        try:
            filing = client.get_latest_10k(company)

            result.update(
                {
                    "filing_date": filing.filing_date.isoformat(),
                    "report_date": (
                        filing.report_date.isoformat()
                        if filing.report_date
                        else None
                    ),
                    "accession_number": filing.accession_number,
                    "document_url": filing.document_url,
                }
            )

            pdf_path = converter.convert(filing, args.output_dir)

            result.update(
                {
                    "status": "success",
                    "pdf_path": str(pdf_path.resolve()),
                }
            )
            print(f"Success: {pdf_path}")

        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
            print(f"Failed: {result['error']}")

        results.append(result)

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_companies": len(results),
        "successful": sum(
            item["status"] == "success" for item in results
        ),
        "failed": sum(
            item["status"] == "failed" for item in results
        ),
        "results": results,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print("\nRun summary")
    print(f"Successful: {manifest['successful']}")
    print(f"Failed: {manifest['failed']}")
    print(f"Manifest: {manifest_path}")

    return 0 if manifest["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
