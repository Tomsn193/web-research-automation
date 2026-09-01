"""
Web research automation tool for enriching company data with public information.

This module searches for company websites, fetches descriptions, and classifies
companies into industries using keyword matching.
"""

import argparse
import time
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Ensures required search library is installed, exits if missing
try:
    from duckduckgo_search import DDGS
except ImportError:
    print("Missing dependency. Run: pip install -r requirements.txt")
    sys.exit(1)

# HTTP request configuration
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
REQUEST_DELAY_SECONDS = 2.0 # Rate limit delay between requests

# Industry classification keywords used for guessing company sectors
INDUSTRY_KEYWORDS = {
    "fintech": ["payments", "banking", "fintech", "financial"],
    "e-commerce": ["shop", "store", "marketplace", "ecommerce"],
    "healthcare": ["health", "medical", "clinic", "hospital"],
    "edtech": ["education", "learning", "school", "edtech"],
    "logistics": ["delivery", "logistics", "shipping", "freight"],
    "ai/tech": ["ai", "artificial intelligence", "claude", "models", "safety", "research"],
}

# Searches DuckDuckGo for a company's official website and returns the top result's URL and snippet.
def search_company(company_name: str) -> dict | None:
    query = f"{company_name} official website"
    
    # Try with DuckDuckGo backend fallbacks
    for backend in ["lite", "html", "api"]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3, backend=backend))
            if results:
                top = results[0]
                return {"url": top.get("href", ""), "snippet": top.get("body", "")}
        except Exception as e:
            continue  # Fall through to next backend if rate-limited
            
    print(f"  [!] Could not fetch search results for: {company_name}")
    return None

# Fetches a web page's HTML to extract its meta description, falling back to the page title on failure.
def fetch_page_description(url: str) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            content = meta["content"]
            if isinstance(content, list):
                content = " ".join(content)
            return content.strip()
        title = soup.find("title")
        return title.text.strip() if title else ""
    except requests.RequestException:
        return ""

def guess_industry(text: str) -> str:
    text_lower = text.lower()
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return industry
    return "unknown"

# Orchestrates company lookup, web scraping, and classification to return enriched company metadata.
def enrich_company(company_name: str) -> dict:
    result = {
        "company_name": company_name,
        "website": "",
        "description": "",
        "likely_industry": "",
        "status": "not_found",
    }

    search_result = search_company(company_name)
    if not search_result:
        return result

    url = search_result["url"]
    snippet = search_result["snippet"]
    description = fetch_page_description(url) or snippet
    industry = guess_industry(f"{snippet} {description}")

    result.update({
        "website": url,
        "description": description[:300],
        "likely_industry": industry,
        "status": "ok"
    })
    return result

def main():
    parser = argparse.ArgumentParser(description="Enrich a list of company names with public info.")
    parser.add_argument("--input", required=True, help="Path to input CSV with a 'company_name' column")
    parser.add_argument("--output", required=True, help="Path to write the enriched CSV")
    args = parser.parse_args()

    df_in = pd.read_csv(args.input)
    if "company_name" not in df_in.columns:
        raise ValueError("Input CSV must have a 'company_name' column")

    rows = []
    not_found = []

    for i, company_name in enumerate(df_in["company_name"], start=1):
        print(f"[{i}/{len(df_in)}] Researching: {company_name}")
        row = enrich_company(str(company_name))
        rows.append(row)
        if row["status"] != "ok":
            not_found.append(company_name)
        time.sleep(REQUEST_DELAY_SECONDS)

    df_out = pd.DataFrame(rows)
    df_out.to_csv(args.output, index=False)
    print(f"\nDone. Wrote {len(df_out)} rows to {args.output}")

    if not_found:
        print(f"\n{len(not_found)} companies need manual follow-up (no confident match):")
        for name in not_found:
            print(f" - {name}")

if __name__ == "__main__":
    main()