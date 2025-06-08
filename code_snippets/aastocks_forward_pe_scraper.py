"""A simple example showing how to scrape forward P/E, last price, and daily change
for the members of the HSI, HSTECH, and HSCEI indices from AASTOCKS.

The gathered data for each constituent is saved to ``aastocks_pe_data.csv``.

This script requires the packages `requests`, `beautifulsoup4`, and `pandas`.
Due to restrictions on the execution environment, this example has not been
verified against the live site. You may need to adjust the CSS selectors or
URL patterns based on the current HTML structure of aastocks.com.
Before scraping, ensure your use complies with AASTOCKS' terms of service.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Index symbols to scrape
INDICES = ["HSI", "HSTECH", "HSCEI"]

# File where results will be saved
OUTPUT_CSV = "aastocks_pe_data.csv"

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CodexBot/1.0)"
}


def fetch_index_components(index: str) -> pd.DataFrame:
    """Fetch the constituent stock table for the given index symbol."""
    url = (
        "https://www.aastocks.com/en/stocks/market/index/"\
        f"hk-index-components.aspx?index={index}"
    )
    resp = requests.get(url, headers=BASE_HEADERS)
    resp.raise_for_status()
    # pandas can often parse the table directly
    tables = pd.read_html(resp.text)
    if not tables:
        raise ValueError(f"No tables found on {url}")
    components = tables[0]
    return components


def parse_stock_row(row: pd.Series) -> dict:
    """Extract relevant fields from a table row."""
    return {
        "code": row.get("Code") or row.get("Stock") or row.get("Ticker"),
        "name": row.get("Name") or row.get("Stock"),
        "price": row.get("Last") or row.get("Price"),
        "change": row.get("Change") or row.get("Chg"),
        "pe_fwd": row.get("P/E (Forecast)") or row.get("P/E Forward"),
    }


def scrape_index(index: str) -> pd.DataFrame:
    """Return a DataFrame with stock info for all constituents of an index."""
    table = fetch_index_components(index)
    records = []
    for _, row in table.iterrows():
        records.append(parse_stock_row(row))
    df = pd.DataFrame(records)
    df["index"] = index
    return df


def main():
    all_results = []
    for index in INDICES:
        try:
            df = scrape_index(index)
            all_results.append(df)
        except Exception as exc:
            print(f"Failed to scrape {index}: {exc}")
    if all_results:
        result = pd.concat(all_results, ignore_index=True)
        print(result)
        result.to_csv(OUTPUT_CSV, index=False)
        print(f"Saved data to {OUTPUT_CSV}")
    else:
        print("No data scraped.")


if __name__ == "__main__":
    main()
