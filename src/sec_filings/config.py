
from dataclasses import dataclass


@dataclass(frozen=True)
class Company:
    ticker: str
    name: str
    cik: str


COMPANIES = (
    Company(
        ticker="AAPL",
        name="Apple Inc.",
        cik="0000320193",
    ),
    Company(
        ticker="META",
        name="Meta Platforms, Inc.",
        cik="0001326801",
    ),
    Company(
        ticker="GOOGL",
        name="Alphabet Inc.",
        cik="0001652044",
    ),
    Company(
        ticker="AMZN",
        name="Amazon.com, Inc.",
        cik="0001018724",
    ),
    Company(
        ticker="NFLX",
        name="Netflix, Inc.",
        cik="0001065280",
    ),
    Company(
        ticker="GS",
        name="The Goldman Sachs Group, Inc.",
        cik="0000886982",
    ),
)
