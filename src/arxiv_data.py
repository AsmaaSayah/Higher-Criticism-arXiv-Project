import arxiv
import datetime
import json
import requests
import concurrent.futures
import calendar
import time
import os
import re
from io import BytesIO
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError


def get_pdf_text(pdf_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    for attempt in range(2):
        try:
            response = requests.get(pdf_url, headers=headers, stream=True, timeout=15)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "pdf" not in content_type.lower():
                print(f"⚠️ Not a PDF (Content-Type): {content_type} — {pdf_url}")
                return ""

            with BytesIO(response.content) as f:
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
                text = re.sub(r'\n\s*\n', '\n\n', text)
                text = re.sub(r'\s+', ' ', text)
                return text.strip()
        except (PdfReadError, Exception) as e:
            print(f"⚠️ Error fetching/parsing PDF ({attempt+1}/2): {e}")
            time.sleep(5)

    return ""


def split_date_range(start_date, end_date, chunk_days=7):
    ranges = []
    current = start_date
    while current <= end_date:
        next_chunk = current + datetime.timedelta(days=chunk_days - 1)
        if next_chunk > end_date:
            next_chunk = end_date
        ranges.append((current, next_chunk))
        current = next_chunk + datetime.timedelta(days=1)
    return ranges


def fetch_chunk(start, end, download_pdf=False):
    start_str = start.strftime("%Y%m%d")
    end_str = end.strftime("%Y%m%d")
    query = f"submittedDate:[{start_str} TO {end_str}]"
    print(f"    Thread fetching: {query}")

    client = arxiv.Client(page_size=100, delay_seconds=3)
    search = arxiv.Search(
        query=query,
        max_results=5000,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Ascending,
    )

    chunk_results = []
    for result in client.results(search):
        paper = {
            "id": result.entry_id,
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "published": result.published.isoformat(),
            "summary": result.summary,
            "categories": result.categories,
            "pdf_url": result.pdf_url,
        }

        if download_pdf:
            print(f"      Downloading PDF for: {paper['title'][:60]}...")
            paper["pdf_content"] = get_pdf_text(result.pdf_url)

        chunk_results.append(paper)

    print(f"    ✅ Done: {len(chunk_results)} papers from {start_str} to {end_str}")
    return chunk_results


def fetch_arxiv_data_for_year_parallel(year, month=3, download_pdf=False, chunk_days=7, max_workers=4):
    print(f"🔄 Fetching March {year} papers in parallel...")

    last_day = calendar.monthrange(year, month)[1]
    start_date = datetime.datetime(year, month, 1)
    end_date = datetime.datetime(year, month, last_day, 23, 59, 59)
    date_ranges = split_date_range(start_date, end_date, chunk_days)

    if download_pdf:
        max_workers = min(max_workers, 2)  # Be gentle when downloading PDFs

    all_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_chunk, start, end, download_pdf) for start, end in date_ranges]

        for future in concurrent.futures.as_completed(futures):
            try:
                chunk = future.result()
                all_results.extend(chunk)
            except Exception as e:
                print(f"⚠️ Error in thread: {e}")

    print(f"✅ Total for March {year}: {len(all_results)} papers")
    return all_results


def fetch_all_years(start_year=1991, end_year=None, month=3, download_pdf=False, output_dir="data"):
    from pathlib import Path
    if end_year is None:
        end_year = datetime.datetime.now().year

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for year in range(start_year, end_year + 1):
        print(f"\n📅 Fetching March {year}...")
        papers = fetch_arxiv_data_for_year_parallel(year, month, download_pdf=download_pdf)

        year_file = os.path.join(output_dir, f"arxiv_march_{year}.json")
        with open(year_file, "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=2)
        print(f"✅ Saved {len(papers)} papers to {year_file}")
