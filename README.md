# SEC 10-K Filing Downloader

A Python application that automatically finds the latest annual financial reports (10-K filings) for six major US companies, downloads them from the US Securities and Exchange Commission (SEC), and converts them into PDF files.

The goal is simple: instead of manually searching for each company's annual report, you can run one command and let the application handle the process.

## 1. What Does This Project Do?

Every year, publicly traded US companies publish annual reports called **10-K filings**. These reports contain important information about a company's business, financial performance, risks, and operations.

The SEC makes these reports publicly available through its EDGAR filing system.

This application automates the process of finding and saving the latest available 10-K report for each of the following companies:

| Company | Stock ticker |
|---|---|
| Apple | AAPL |
| Meta Platforms | META |
| Alphabet (Google) | GOOGL |
| Amazon | AMZN |
| Netflix | NFLX |
| Goldman Sachs | GS |

For each company, the application:

1. Looks up its filing information using the SEC's public API.
2. Identifies the latest filing whose form type is exactly `10-K`, excluding amendments such as `10-K/A`.
3. Downloads the filing's HTML document from SEC EDGAR.
4. Converts the HTML document into a PDF using Playwright and Chromium.
5. Saves the PDF and records the result in a JSON manifest.

The application processes companies one at a time. If one company's filing cannot be processed, it records the error and continues with the remaining companies.

## 2. Example Output

After a successful run, the output directory contains one PDF per company and a manifest file.

```text
output/
├── AAPL_2025-10-31.pdf
├── META_<filing-date>.pdf
├── GOOGL_<filing-date>.pdf
├── AMZN_<filing-date>.pdf
├── NFLX_<filing-date>.pdf
├── GS_<filing-date>.pdf
└── manifest.json
```

The dates above are examples of the filename format. Actual filenames depend on the latest filings available when you run the application.

### What is `manifest.json`?

The manifest is a summary of the processing run. It records:

- When the application ran.
- How many companies were processed successfully or unsuccessfully.
- Each company's name and ticker.
- Filing date, report date, and SEC accession number when available.
- The source document URL.
- The generated PDF path for successful conversions.
- Error details for failed companies.

This makes it easier to check the results without opening every PDF individually.

## 3. How Does It Work?

The application separates the main responsibilities into small Python modules.

```text
SEC Submissions API
        |
        v
   SecClient
   Finds the latest 10-K filing
        |
        v
   SEC EDGAR
   Downloads the filing's HTML
        |
        v
   PdfConverter
   Uses Playwright and Chromium
        |
        v
   PDF files + manifest.json
```

### Main components

| File | Responsibility |
|---|---|
| `config.py` | Stores the company names, stock tickers, and SEC CIK identifiers. |
| `sec_client.py` | Communicates with the SEC API and identifies the latest exact `10-K` filing. |
| `pdf_converter.py` | Downloads the filing HTML and renders it as a PDF. |
| `main.py` | Coordinates the workflow, handles individual company failures, and generates the manifest. |
| `tests/` | Contains automated tests for key application behavior. |

This structure keeps API communication, PDF generation, configuration, and orchestration separate, making the application easier to maintain and test.

## 4. Technology Stack

- **Python** — application logic and workflow orchestration.
- **Requests** — HTTP requests to the SEC API and filing archive.
- **Playwright** — controls a browser to render HTML documents.
- **Chromium** — renders the filing and generates the PDF.
- **pytest** — automated testing.
- **JSON** — records the processing summary in `manifest.json`.

## 5. Getting Started

### Prerequisites

Before running the application, install:

- Python 3.10 or newer.
- Git, if you want to clone the repository.
- A contact email address for the SEC User-Agent.
- Playwright and its Chromium browser.

### Step 1: Get the project

Clone the repository and navigate into its directory:

```powershell
git clone <your-repository-url>
cd quartr-sec-filings
```

Alternatively, open the project directory directly in VS Code.

### Step 2: Create a virtual environment

A virtual environment keeps this project's Python dependencies separate from other projects.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
python -m playwright install chromium
```

The last command installs the browser required to convert HTML filings into PDFs.

## 6. Configure Your SEC Contact Email

The SEC asks applications making automated requests to identify themselves with a descriptive User-Agent. This project uses a User-Agent containing a contact email.

You can configure the email through an environment variable in PowerShell:

```powershell
$env:SEC_USER_EMAIL = "your-email@example.com"
```

Replace the example with your own contact email address.

Alternatively, pass the email directly in a command. You do not need to configure both.

## 7. Run the Application

### Download all six companies

If you configured `SEC_USER_EMAIL`:

```powershell
python -m sec_filings.main
```

Or provide the email directly:

```powershell
python -m sec_filings.main --email "your-email@example.com"
```

### Process selected companies

For example, to process Apple and Meta only:

```powershell
python -m sec_filings.main --tickers AAPL META --email "your-email@example.com"
```

Supported tickers are `AAPL`, `META`, `GOOGL`, `AMZN`, `NFLX`, and `GS`.

### Choose an output directory

To save the results in a different directory:

```powershell
python -m sec_filings.main --output-dir ".\my-output" --email "your-email@example.com"
```

The directory is created automatically if it does not exist.

### Understand the run summary

At the end of the run, the application reports the number of successful and failed companies and the location of `manifest.json`.

It returns exit code `0` if all selected companies succeed and exit code `1` if any fail. Detailed outcomes are recorded in the manifest.

## 8. Run the Tests

To run the automated test suite:

```powershell
python -m pytest -v
```

The tests cover key behaviors, including:

- Selecting the latest exact `10-K` rather than a `10-K/A` amendment.
- Constructing the SEC document URL correctly.
- Handling the absence of a matching filing.
- Rejecting a missing contact email.
- Rejecting a response that does not appear to contain HTML.
- Testing PDF output handling with a simulated browser.

The automated tests use mocked responses where appropriate, so they do not need to download live filings.

**Note:** The PDF converter test uses a simulated PDF header; it does not validate the visual quality of a real rendered report. A separate manual run has been used to verify an actual generated PDF.

## 9. Data Sources

The application uses public SEC resources:

- [SEC submissions API](https://data.sec.gov/submissions/)
- [SEC EDGAR filing archive](https://www.sec.gov/Archives/edgar/data/)

The application retrieves filing metadata from the submissions API and uses the resulting archive URL to download the filing document.

Requests are made sequentially rather than concurrently.

## 10. Design Decisions and Limitations

### Why select the exact `10-K` form?

The SEC may list amended annual reports as `10-K/A`. This application selects the latest filing whose form type is exactly `10-K`, rather than treating amendments as equivalent to the original form.

### Why use a browser for PDF conversion?

SEC filings often contain complex tables, styles, and other HTML elements. Playwright uses Chromium's browser rendering engine, which is designed to render HTML and CSS. This is a better fit for these documents than a converter with limited support for complex layouts.

### What should users be aware of?

- The application currently supports the six companies configured in `config.py`.
- PDF appearance can differ from the original web document, particularly for complex tables, images, or embedded resources.
- The program records processing failures in the manifest, but it does not automatically retry failed requests.
- The application downloads the primary document identified by the SEC API; it does not attempt to combine every exhibit attached to a filing.
- The latest filing is determined from the SEC submission data available when the application runs.

## 11. Possible Future Improvements

Potential extensions include:

- Adding retries and backoff for transient HTTP errors.
- Validating generated PDFs more thoroughly.
- Adding integration tests against controlled sample HTML filings.
- Running the application on a scheduled basis.
- Packaging the application in Docker for easier deployment across environments.

## 12. Project Status

The application has successfully generated PDFs for all six configured companies in a manual run. The current automated test suite contains six passing tests.
