import requests
import tarfile
from io import BytesIO
import json
import os
import re
import concurrent.futures
from datetime import datetime
import fitz  # PyMuPDF


def get_latex_source_text(arxiv_id):
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        content = response.content

        if len(content) < 2000 and b"<html" in content.lower():
            print(f"⚠️ No LaTeX source available for {arxiv_id} (HTML fallback)")
            return ""

        try:
            f = BytesIO(content)
            mode = "r:gz" if content[:2] == b'\x1f\x8b' else "r:"
            with tarfile.open(fileobj=f, mode=mode) as tar:
                tex_text = ""
                for member in tar.getmembers():
                    if member.name.endswith(".tex"):
                        f = tar.extractfile(member)
                        if f:
                            tex = f.read().decode("utf-8", errors="ignore")
                            tex_text += tex + "\n"
                if tex_text:
                    return tex_text.strip()
        except tarfile.ReadError:
            pass

        text = content.decode("utf-8", errors="ignore")
        if "\\documentclass" in text or "\\begin{document}" in text:
            return text.strip()
        else:
            print(f"⚠️ Fallback not LaTeX-looking: {arxiv_id}")
            return ""

    except Exception as e:
        print(f"❌ Error downloading LaTeX for {arxiv_id}: {e}")
        return ""


def get_pdf_text(pdf_url):
    try:
        response = requests.get(pdf_url, stream=True, timeout=15)
        response.raise_for_status()
        if "pdf" not in response.headers.get("Content-Type", "").lower():
            print(f"⚠️ Not a valid PDF: {pdf_url}")
            return ""

        with BytesIO(response.content) as f:
            doc = fitz.open(stream=f.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r'\s+', ' ', text)
            print(f"✅ Extracted {len(text)} characters from: {pdf_url}")
            return text.strip()
    except Exception as e:
        print(f"⚠️ PDF extraction error for {pdf_url}: {e}")
        return ""


def process_paper(paper):
    arxiv_id = paper["id"].replace("http://arxiv.org/abs/", "")
    print(f"📄 Processing {arxiv_id}")
    try:
        latex = get_latex_source_text(arxiv_id)
        if latex:
            paper["latex_source"] = latex
            paper["latex_source_available"] = True
            paper["from_pdf"] = False
        else:
            print(f"🔁 Falling back to PDF for {arxiv_id}")
            pdf_url = paper.get("pdf_url")
            pdf_text = get_pdf_text(pdf_url) if pdf_url else ""
            paper["latex_source"] = pdf_text
            paper["latex_source_available"] = False
            paper["from_pdf"] = True
        return paper, None
    except Exception as e:
        return paper, arxiv_id


def enrich_json_with_latex(input_path, output_dir, max_workers=4):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    failed_ids = []
    from_latex = 0
    from_pdf = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_paper, paper) for paper in data]
        enriched_data = []
        for future in concurrent.futures.as_completed(futures):
            paper, failed_id = future.result()
            enriched_data.append(paper)
            if failed_id:
                failed_ids.append(failed_id)
            elif paper.get("from_pdf"):
                from_pdf += 1
            else:
                from_latex += 1

    now = datetime.now().strftime("%Y%m")
    output_path = os.path.join(output_dir, f"enriched_arxiv_{now}.json.gz")
    import gzip
    with gzip.open(output_path, "wt", encoding="utf-8") as f:
        json.dump(enriched_data, f, indent=2)
    print(f"✅ Done: Saved enriched file to {output_path}")

    if failed_ids:
        with open(os.path.join(output_dir, "failed_ids.txt"), "w") as f:
            f.write("\n".join(failed_ids))
        print(f"⚠️ Logged {len(failed_ids)} failed downloads in failed_ids.txt")

    print("\n📊 Summary Report")
    print("----------------------")
    print(f"Total papers: {len(enriched_data)}")
    print(f"  ✅ From LaTeX: {from_latex}")
    print(f"  🔁 From PDF fallback: {from_pdf}")
    print(f"  ❌ Failed: {len(failed_ids)}")
