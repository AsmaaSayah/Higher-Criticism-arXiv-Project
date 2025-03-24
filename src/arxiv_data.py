import arxiv
import datetime
import json
import requests
from io import BytesIO
import PyPDF2
from PyPDF2 import PdfReader
import re

def get_pdf_text(pdf_url):
    """
    Downloads the PDF from pdf_url, extracts its text using PyPDF2, 
    and performs basic cleanup on the extracted text.
    
    Returns an empty string if extraction fails.
    """
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with BytesIO(response.content) as f:
                try:
                    pdf_reader = PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    
                    # Basic post-processing cleanup:
                    # 1. Replace common ligatures
                    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
                    
                    # 2. Remove excessive newlines and whitespace
                    text = re.sub(r'\n\s*\n', '\n\n', text)
                    text = re.sub(r'\s+', ' ', text)
                    
                    return text.strip()
                except Exception as e:
                    print(f"Error extracting text from PDF: {e}")
                    return ""
        else:
            print(f"Error downloading PDF: HTTP {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error during PDF request: {e}")
        return ""

def fetch_arxiv_data_for_year(year, month=3, max_results=200, download_pdf=False):
    """
    Fetch arXiv papers submitted in the given month of a specific year using a date-range query.
    """
    # Define the date range for the month
    start_date = datetime.datetime(year, month, 1)
    end_date = datetime.datetime(year, month, 31, 23, 59, 59)
    
    # Format dates as YYYYMMDD for the query
    start_date_str = start_date.strftime("%Y%m%d")
    end_date_str = end_date.strftime("%Y%m%d")
    
    # Construct a query filtering on submittedDate
    query = f"submittedDate:[{start_date_str} TO {end_date_str}]"
    print(f"Query for March {year}: {query}")
    
    # Build the search object
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Ascending,
    )
    
    # Use the new client interface
    client = arxiv.Client(page_size=100, delay_seconds=3)
    
    results = []
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
            print(f"Downloading PDF for paper: {result.entry_id}")
            paper["pdf_content"] = get_pdf_text(result.pdf_url)
        results.append(paper)
    
    return results

def fetch_all_years(start_year=1970, end_year=None, month=3, download_pdf=False):
    """
    Fetch arXiv papers for the given month (default March) for each year in the range.
    """
    if end_year is None:
        end_year = datetime.datetime.now().year
        
    all_data = {}
    for year in range(start_year, end_year + 1):
        print(f"Fetching data for March {year}...")
        papers = fetch_arxiv_data_for_year(year, month, download_pdf=download_pdf)
        all_data[year] = papers
        print(f"  Found {len(papers)} papers.")
    return all_data

def save_data(data, filename):
    """
    Save data to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")



