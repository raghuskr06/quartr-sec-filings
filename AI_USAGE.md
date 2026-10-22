# AI Usage Log

## Tool Used

- **Tool:** ChatGPT
- **Purpose:** Learning support, implementation guidance, debugging, testing, and documentation during development of the SEC 10-K filing downloader.

## Summary of AI Assistance

The following summarizes the areas in which AI assistance was used during development. This is a summary, not a verbatim transcript of every prompt.

| Area | Purpose of assistance |
|---|---|
| Project structure | Discussing how to organize the Python application into configuration, SEC API client, PDF converter, and entry-point modules. |
| SEC API integration | Understanding how to retrieve filing metadata, select the latest exact `10-K` filing, and construct SEC archive URLs. |
| PDF conversion | Troubleshooting PDF conversion on Windows and evaluating alternative HTML-to-PDF approaches before implementing Playwright with Chromium. |
| Application workflow | Developing the main execution flow, ticker selection, error handling, output directory management, and JSON manifest. |
| Automated testing | Writing and refining pytest tests for filing selection, URL construction, validation, and PDF output handling. |
| Documentation | Preparing installation instructions, usage examples, architecture explanations, and project limitations. |

## Example Prompt Topics

Examples of the kinds of prompts used during development include:

- How should a Python project be structured for downloading SEC 10-K filings and converting them to PDFs?
- How can the SEC submissions API be used to identify the latest exact `10-K` filing for a company?
- How can HTML filings be converted to PDF reliably on Windows?
- How should the application handle failures for individual companies without stopping the whole run?
- How can the filing client and PDF converter be tested using pytest?
- How should the README explain the application to both technical and non-technical readers?

These are representative topics, not necessarily the exact wording of the original prompts.

## Developer Verification

The generated code was run and tested during development. The application successfully generated PDFs for all six configured companies, and the automated test suite passed six tests.

AI-generated suggestions were reviewed and adjusted during implementation, including troubleshooting dependency and PDF-rendering issues.
