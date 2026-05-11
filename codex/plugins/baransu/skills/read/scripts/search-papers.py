#!/usr/bin/env python3
"""Search academic papers from OpenAlex and Semantic Scholar."""

import json
import sys
import threading
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError


def reconstruct_abstract(abstract_inverted_index):
    """Reconstruct abstract text from OpenAlex inverted index format.

    The inverted index maps {word: [position1, position2, ...]}. Reconstruct
    by flattening to (position, word) pairs, sorting by position, and joining.
    """
    if not abstract_inverted_index:
        return ""
    pairs = []
    for word, positions in abstract_inverted_index.items():
        for pos in positions:
            pairs.append((pos, word))
    pairs.sort(key=lambda x: x[0])
    return " ".join(word for _, word in pairs)


def query_openalex(keyword):
    """Query OpenAlex for open-access papers matching keyword.

    Returns list of raw result dicts, or [] on failure.
    On HTTP 429: wait 1s and retry once.
    """
    params = urllib.parse.urlencode({
        "search": keyword,
        "filter": "open_access.is_oa:true",
        "sort": "cited_by_count:desc",
        "per-page": "10",
    })
    url = f"https://api.openalex.org/works?{params}"

    def _fetch():
        req = urllib.request.Request(url, headers={"User-Agent": "search-papers/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    try:
        data = _fetch()
    except HTTPError as e:
        if e.code == 429:
            time.sleep(1)
            try:
                data = _fetch()
            except Exception as retry_err:
                print(f"OpenAlex retry failed: {retry_err}", file=sys.stderr)
                return []
        else:
            print(f"OpenAlex HTTP error {e.code}: {e}", file=sys.stderr)
            return []
    except (URLError, Exception) as e:
        print(f"OpenAlex query failed: {e}", file=sys.stderr)
        return []

    results = data.get("results", [])
    papers = []
    for item in results:
        author_names = [
            a.get("author", {}).get("display_name", "")
            for a in item.get("authorships", [])
            if a.get("author", {}).get("display_name")
        ]
        abstract_text = reconstruct_abstract(item.get("abstract_inverted_index") or {})
        oa_url = (item.get("open_access") or {}).get("oa_url")
        doi = item.get("doi")
        papers.append({
            "title": item.get("title", ""),
            "authors": author_names,
            "year": item.get("publication_year"),
            "abstract_text": abstract_text,
            "pdf_url": oa_url,
            "doi": doi,
            "_source": "openalex",
        })
    return papers


def query_semantic_scholar(keyword):
    """Query Semantic Scholar for papers matching keyword.

    Returns list of raw result dicts, or [] on failure.
    """
    params = urllib.parse.urlencode({
        "query": keyword,
        "fields": "title,authors,year,abstract,openAccessPdf,externalIds",
        "limit": "10",
    })
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "search-papers/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Semantic Scholar query failed: {e}", file=sys.stderr)
        return []

    papers = []
    for item in data.get("data", []):
        author_names = [
            a.get("name", "")
            for a in item.get("authors", [])
            if a.get("name")
        ]
        oa_pdf = item.get("openAccessPdf") or {}
        pdf_url = oa_pdf.get("url")
        external_ids = item.get("externalIds") or {}
        doi = external_ids.get("DOI")
        papers.append({
            "title": item.get("title", ""),
            "authors": author_names,
            "year": item.get("year"),
            "abstract_text": item.get("abstract") or "",
            "pdf_url": pdf_url,
            "doi": doi,
            "_source": "semantic_scholar",
        })
    return papers


def normalize(paper, source):
    """Normalize a raw paper dict into the standard output format."""
    authors = paper.get("authors", [])
    if len(authors) > 5:
        authors = authors[:5] + ["et al."]

    abstract_text = paper.get("abstract_text", "") or ""
    abstract_preview = abstract_text[:150]

    year = paper.get("year")
    if year is not None:
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = None

    return {
        "title": paper.get("title", "") or "",
        "authors": authors,
        "year": year,
        "abstract_preview": abstract_preview,
        "pdf_url": paper.get("pdf_url"),
        "doi": paper.get("doi"),
        "source": source,
    }


def _normalize_title(title):
    """Lowercase and strip punctuation for title comparison."""
    import string
    return "".join(
        c for c in (title or "").lower()
        if c not in string.punctuation
    ).strip()


def dedup_merge(openalex_results, ss_results):
    """Merge results from both sources, deduplicating by DOI or normalized title.

    When DOI is not None, prefer openalex. Returns at most 10 results.
    """
    seen_dois = set()
    seen_titles = set()
    merged = []

    def _add(paper, source):
        if len(merged) >= 10:
            return
        norm = normalize(paper, source)
        doi = norm["doi"]
        title_key = _normalize_title(norm["title"])

        if doi is not None:
            if doi in seen_dois:
                return
            seen_dois.add(doi)
        else:
            if title_key in seen_titles:
                return
            seen_titles.add(title_key)

        merged.append(norm)

    # Iterate openalex first (preferred when DOI matches)
    for paper in openalex_results:
        _add(paper, "openalex")

    # Add semantic scholar entries not already present
    for paper in ss_results:
        doi = paper.get("doi")
        title_key = _normalize_title(paper.get("title", ""))
        if doi is not None and doi in seen_dois:
            continue
        if doi is None and title_key in seen_titles:
            continue
        _add(paper, "semantic_scholar")

    return merged


def main():
    if len(sys.argv) < 2:
        print("Usage: search-papers.py <keyword>", file=sys.stderr)
        print("[]")
        sys.exit(1)

    keyword = sys.argv[1]
    openalex_results = []
    ss_results = []

    def run_openalex():
        nonlocal openalex_results
        openalex_results = query_openalex(keyword)

    def run_ss():
        nonlocal ss_results
        ss_results = query_semantic_scholar(keyword)

    t1 = threading.Thread(target=run_openalex)
    t2 = threading.Thread(target=run_ss)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    result = dedup_merge(openalex_results, ss_results)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
