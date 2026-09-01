# Web Research Automation Tool

A Python-based CLI tool that automates company research by searching for company websites, extracting meta descriptions/page titles using web scraping, and classifying companies into industry sectors using keyword matching.

---

## Features

- **Automated Web Search:** Uses DuckDuckGo to discover company official web links and snippets.
- **Web Scraping & Metadata Extraction:** Fetches page content via `requests` and `BeautifulSoup` to extract page meta descriptions or `<title>` tags.
- **Industry Classification:** Matches extracted text against predefined industry keyword rules (Fintech, E-commerce, Healthcare, EdTech, Logistics, AI/Tech).
- **Batch Processing & CLI Support:** Accepts input CSV files, processes companies sequentially with rate limiting, and exports structured results to a designated CSV file.
- **Graceful Error Handling:** Provides status tracking (`ok` vs. `not_found`) and outputs a clear follow-up list for manual review.

---

## Directory Structure

```text
.
├── input/
│   └── companies.csv          # Input CSV with target company names
├── output/
│   └── companies_enriched.csv # Generated output CSV with enriched company metadata
├── .gitignore                 # Prevents tracking of .venv, output files, and cache
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
└── research.py                # Main executable script
```

---

## Prerequisites

- **Python 3.10+** installed on your system.
- An active virtual environment (recommended).

---

## Installation

1. **Clone or download this repository:**
   ```bash
   git clone https://github.com/Tomsn193/web-research-automation.git
   cd company-research-automation
   ```

2. **Create and activate a virtual environment:**
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```cmd
     python -m venv .venv
     .venv\Scripts\activate.bat
     ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Input CSV Format

Ensure your input CSV file contains a column header named `company_name`.

Example (`input/companies.csv`):
```csv
company_name
Anthropic
Paystack
Flutterwave
Interswitch
```

---

## Usage

Run the main script by passing the paths to your input and output CSV files:

```bash
python research.py --input input/companies.csv --output output/companies_enriched.csv
```

### CLI Arguments

| Argument | Required | Description |
| :--- | :---: | :--- |
| `--input` | **Yes** | Path to the source CSV file containing a `company_name` column. |
| `--output` | **Yes** | Path where the enriched output CSV file will be written. |

---

## Output CSV Format

The script produces a CSV file containing the following fields:

| Column | Description |
| :--- | :--- |
| `company_name` | Name of the company searched. |
| `website` | Discovered official website URL. |
| `description` | Extracted page description or search snippet (truncated to 300 characters). |
| `likely_industry` | Guessed industry classification based on keyword matching. |
| `status` | Search status (`ok` if website found, `not_found` if missing/failed). |

Example Output:
```csv
company_name,website,description,likely_industry,status
Paystack,https://paystack.com,"Paystack helps businesses in Africa get paid by anyone, anywhere in the world.",fintech,ok
Anthropic,https://www.anthropic.com,"Anthropic is an AI safety and research company that builds reliable, interpretable, and steerable AI systems.",ai/tech,ok
```

---

## Dependencies

- **`pandas`**: Handles CSV reading, DataFrame manipulation, and writing output.
- **`requests`**: Handles HTTP network requests to fetch website HTML.
- **`beautifulsoup4`**: Parses HTML to extract `<meta>` and `<title>` tags.
- **`duckduckgo-search`**: Programmatic interface for search engine queries.

Sample `requirements.txt`:
```text
pandas>=2.0.0
requests>=2.28.0
beautifulsoup4>=4.12.0
duckduckgo-search>=6.0.0
```

---

## Configuration & Rate Limiting

- **Request Delay:** The script incorporates a `REQUEST_DELAY_SECONDS = 2.0` pause between requests to prevent IP rate-limiting from search engines and target servers.
- **Custom User-Agent:** HTTP requests include a browser User-Agent header to prevent automated scraping blocks.