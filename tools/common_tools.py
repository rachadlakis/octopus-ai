"""
Common tools shared across agents.
"""
import json
import re
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import urlparse, urlencode, quote_plus


def get_current_time() -> dict:
    """
    Get the current time in HH:MM:SS format.

    Returns:
        dict: A dictionary containing the current time
    """
    return {
        "current_time": datetime.now().strftime("%H:%M:%S"),
    }


def get_date() -> dict:
    """
    Get the current date in YYYY-MM-DD format.

    Returns:
        dict: A dictionary containing the current date
    """
    return {
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }


def web_search(query: str, num_results: int = 5) -> dict:
    """
    Search the web using DuckDuckGo (no API key required).

    Args:
        query: Search query string
        num_results: Number of results to return (default 5, max 10)

    Returns:
        dict: Contains 'results' list with title, url, snippet for each result
    """
    try:
        num_results = min(max(1, num_results), 10)

        # Use DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        req = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="replace")

        results = []

        # Parse results from DuckDuckGo HTML response
        # Look for result links and snippets
        result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]*(?:<[^>]*>[^<]*)*)</a>'

        links = re.findall(result_pattern, html)
        snippets = re.findall(snippet_pattern, html)

        for i, (url, title) in enumerate(links[:num_results]):
            # Clean up the URL (DuckDuckGo wraps URLs)
            if "uddg=" in url:
                url_match = re.search(r'uddg=([^&]+)', url)
                if url_match:
                    url = urllib.request.unquote(url_match.group(1))

            result = {
                "title": title.strip(),
                "url": url,
                "snippet": ""
            }

            if i < len(snippets):
                # Clean HTML tags from snippet
                snippet = re.sub(r'<[^>]+>', '', snippets[i])
                result["snippet"] = snippet.strip()

            results.append(result)

        return {
            "query": query,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        return {"error": str(e), "query": query}


def fetch_url(url: str) -> dict:
    """
    Fetch content from a URL.

    Args:
        url: The URL to fetch

    Returns:
        dict: Contains 'content', 'status_code', and 'content_type'
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {"error": "Only HTTP/HTTPS URLs are supported"}

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AI-Company-Agent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8", errors="replace")
            return {
                "content": content[:50000],  # Limit size
                "status_code": response.status,
                "content_type": response.headers.get("Content-Type", ""),
            }
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def read_file(file_path: str) -> dict:
    """
    Read content from a local file.

    Args:
        file_path: Path to the file to read

    Returns:
        dict: Contains 'content' or 'error'
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content, "size": len(content)}
    except FileNotFoundError:
        return {"error": f"File not found: {file_path}"}
    except Exception as e:
        return {"error": str(e)}


def write_file(file_path: str, content: str) -> dict:
    """
    Write content to a local file.

    Args:
        file_path: Path to the file to write
        content: Content to write

    Returns:
        dict: Contains 'success' and 'bytes_written' or 'error'
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "bytes_written": len(content)}
    except Exception as e:
        return {"error": str(e)}


def calculate(expression: str) -> dict:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: Math expression (e.g., "2 + 2 * 3", "sqrt(16)")

    Returns:
        dict: Contains 'result' or 'error'
    """
    import math

    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "len": len,
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
        "tan": math.tan, "log": math.log, "log10": math.log10,
        "exp": math.exp, "floor": math.floor, "ceil": math.ceil,
        "pi": math.pi, "e": math.e,
    }

    try:
        # Only allow safe characters
        if not re.match(r'^[\d\s\+\-\*\/\.\(\)\,a-zA-Z_]+$', expression):
            return {"error": "Invalid characters in expression"}

        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e)}


def word_count(text: str) -> dict:
    """
    Count words, characters, sentences, and paragraphs in text.

    Args:
        text: The text to analyze

    Returns:
        dict: Word count statistics
    """
    words = len(text.split())
    characters = len(text)
    characters_no_spaces = len(text.replace(" ", ""))
    sentences = len(re.findall(r'[.!?]+', text))
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])

    return {
        "words": words,
        "characters": characters,
        "characters_no_spaces": characters_no_spaces,
        "sentences": sentences,
        "paragraphs": paragraphs,
        "avg_word_length": round(characters_no_spaces / words, 2) if words > 0 else 0,
    }


def extract_urls(text: str) -> dict:
    """
    Extract all URLs from text.

    Args:
        text: Text containing URLs

    Returns:
        dict: Contains list of 'urls' found
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return {"urls": urls, "count": len(urls)}


def extract_emails(text: str) -> dict:
    """
    Extract all email addresses from text.

    Args:
        text: Text containing email addresses

    Returns:
        dict: Contains list of 'emails' found
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return {"emails": emails, "count": len(emails)}


def json_parse(json_string: str) -> dict:
    """
    Parse a JSON string into a Python object.

    Args:
        json_string: JSON string to parse

    Returns:
        dict: Contains 'data' or 'error'
    """
    try:
        data = json.loads(json_string)
        return {"data": data}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}


def json_format(data: str, indent: int = 2) -> dict:
    """
    Format/prettify a JSON string.

    Args:
        data: JSON string to format
        indent: Number of spaces for indentation

    Returns:
        dict: Contains 'formatted' JSON string or 'error'
    """
    try:
        parsed = json.loads(data)
        formatted = json.dumps(parsed, indent=indent, ensure_ascii=False)
        return {"formatted": formatted}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}


def text_replace(text: str, find: str, replace: str, case_sensitive: bool = True) -> dict:
    """
    Find and replace text.

    Args:
        text: The original text
        find: Text to find
        replace: Text to replace with
        case_sensitive: Whether to match case

    Returns:
        dict: Contains 'result' and 'replacements' count
    """
    if case_sensitive:
        count = text.count(find)
        result = text.replace(find, replace)
    else:
        pattern = re.compile(re.escape(find), re.IGNORECASE)
        count = len(pattern.findall(text))
        result = pattern.sub(replace, text)

    return {"result": result, "replacements": count}


def slugify(text: str) -> dict:
    """
    Convert text to a URL-friendly slug.

    Args:
        text: Text to convert

    Returns:
        dict: Contains 'slug'
    """
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')
    return {"slug": slug}


def scrape_webpage(url: str, include_links: bool = False) -> dict:
    """
    Scrape a webpage and extract clean text content.

    Args:
        url: The URL to scrape
        include_links: Whether to include extracted links

    Returns:
        dict: Contains 'title', 'text', 'links' (if requested), or 'error'
    """
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_parts = []
            self.links = []
            self.title = ""
            self.in_title = False
            self.skip_tags = {"script", "style", "noscript", "svg", "path"}
            self.current_skip = 0

        def handle_starttag(self, tag, attrs):
            if tag in self.skip_tags:
                self.current_skip += 1
            if tag == "title":
                self.in_title = True
            if tag == "a":
                for attr, value in attrs:
                    if attr == "href" and value:
                        self.links.append(value)

        def handle_endtag(self, tag):
            if tag in self.skip_tags:
                self.current_skip -= 1
            if tag == "title":
                self.in_title = False
            if tag in {"p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "li"}:
                self.text_parts.append("\n")

        def handle_data(self, data):
            if self.current_skip > 0:
                return
            text = data.strip()
            if text:
                if self.in_title:
                    self.title = text
                else:
                    self.text_parts.append(text)

    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {"error": "Only HTTP/HTTPS URLs are supported"}

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AI-Company-Agent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")

        extractor = TextExtractor()
        extractor.feed(html)

        text = " ".join(extractor.text_parts)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\n\s*\n', '\n\n', text)

        result = {
            "title": extractor.title,
            "text": text[:50000],  # Limit size
            "text_length": len(text),
        }

        if include_links:
            # Filter and clean links
            clean_links = []
            for link in extractor.links:
                if link.startswith("http"):
                    clean_links.append(link)
                elif link.startswith("/") and not link.startswith("//"):
                    clean_links.append(f"{parsed.scheme}://{parsed.netloc}{link}")
            result["links"] = list(set(clean_links))[:100]  # Dedupe and limit

        return result

    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def extract_html_tables(url: str) -> dict:
    """
    Extract tables from a webpage as structured data.

    Args:
        url: The URL to scrape tables from

    Returns:
        dict: Contains 'tables' list or 'error'
    """
    from html.parser import HTMLParser

    class TableExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.tables = []
            self.current_table = []
            self.current_row = []
            self.current_cell = ""
            self.in_table = False
            self.in_row = False
            self.in_cell = False

        def handle_starttag(self, tag, attrs):
            if tag == "table":
                self.in_table = True
                self.current_table = []
            elif tag == "tr" and self.in_table:
                self.in_row = True
                self.current_row = []
            elif tag in ("td", "th") and self.in_row:
                self.in_cell = True
                self.current_cell = ""

        def handle_endtag(self, tag):
            if tag == "table" and self.in_table:
                if self.current_table:
                    self.tables.append(self.current_table)
                self.in_table = False
            elif tag == "tr" and self.in_row:
                if self.current_row:
                    self.current_table.append(self.current_row)
                self.in_row = False
            elif tag in ("td", "th") and self.in_cell:
                self.current_row.append(self.current_cell.strip())
                self.in_cell = False

        def handle_data(self, data):
            if self.in_cell:
                self.current_cell += data

    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {"error": "Only HTTP/HTTPS URLs are supported"}

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AI-Company-Agent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")

        extractor = TableExtractor()
        extractor.feed(html)

        return {
            "tables": extractor.tables[:20],  # Limit number of tables
            "count": len(extractor.tables),
        }

    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def summarize_stats(numbers: list) -> dict:
    """
    Calculate basic statistics for a list of numbers.

    Args:
        numbers: List of numbers

    Returns:
        dict: Statistics including min, max, mean, median, sum
    """
    if not numbers:
        return {"error": "Empty list provided"}

    try:
        nums = [float(n) for n in numbers]
        sorted_nums = sorted(nums)
        n = len(nums)
        mid = n // 2
        median = (sorted_nums[mid] + sorted_nums[mid - 1]) / 2 if n % 2 == 0 else sorted_nums[mid]

        return {
            "count": n,
            "sum": sum(nums),
            "min": min(nums),
            "max": max(nums),
            "mean": round(sum(nums) / n, 4),
            "median": median,
            "range": max(nums) - min(nums),
        }
    except (TypeError, ValueError) as e:
        return {"error": f"Invalid numbers: {e}"}
