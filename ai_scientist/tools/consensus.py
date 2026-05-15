import json
import os
import re
import time
import warnings
from typing import Dict, List, Optional, Union

import requests

from ai_scientist.tools.base_tool import BaseTool

CONSENSUS_MCP_URL = "https://mcp.consensus.app/mcp"
OPENCODE_AUTH_PATH = os.path.expanduser("~/.local/share/opencode/mcp-auth.json")


def get_access_token() -> Optional[str]:
    try:
        with open(OPENCODE_AUTH_PATH, "r") as f:
            data = json.load(f)
        token_data = data.get("consensus", {}).get("tokens", {})
        return token_data.get("accessToken")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


def _get_headers() -> dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    token = get_access_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _mcp_call(method: str, params: dict = None) -> dict:
    headers = _get_headers()

    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "ai-scientist", "version": "1.0"},
        },
    }
    rsp = requests.post(CONSENSUS_MCP_URL, headers=headers, json=init_payload)
    rsp.raise_for_status()

    requests.post(
        CONSENSUS_MCP_URL,
        headers=headers,
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
    )

    call_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": method,
    }
    if params:
        call_payload["params"] = params

    rsp = requests.post(CONSENSUS_MCP_URL, headers=headers, json=call_payload)
    rsp.raise_for_status()
    return rsp.json()


def _format_authors(authors_raw) -> str:
    if isinstance(authors_raw, str):
        return authors_raw
    if isinstance(authors_raw, list):
        names = []
        for a in authors_raw:
            if isinstance(a, dict):
                names.append(a.get("name", "Unknown"))
            else:
                names.append(str(a))
        return ", ".join(names)
    return str(authors_raw)


def _generate_bibtex(title: str, authors: str, journal: str, year: str) -> str:
    first_author = authors.split(",")[0].strip() if authors else "Unknown"
    last_name = first_author.split()[-1] if first_author.split() else "Unknown"
    cite_key = f"{last_name}{year}".lower()
    cite_key = re.sub(r"[^a-z0-9]", "", cite_key)
    if not cite_key:
        cite_key = f"paper{year}"

    bibtex = (
        f"@article{{{cite_key},\n"
        f"  title={{{title}}},\n"
        f"  author={{{authors}}},\n"
        f"  journal={{{journal}}},\n"
        f"  year={{{year}}}\n"
        f"}}"
    )
    return bibtex


def _parse_papers_from_text(text: str) -> List[dict]:
    papers = []
    pattern = re.compile(
        r"\[\d+\]\s+\[([^\]]+)\]\(([^)]+)\)\s+"
        r"\(([^)]*?)(?:,\s+(\d{4}),\s+(\d+)\s+citations?,\s+(.+?))\)\s*\n+(.*?)(?=\n\[\d+\]|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        title = match.group(1).strip()
        url = match.group(2).strip()
        authors_str = match.group(3).strip()
        year = match.group(4)
        citations = int(match.group(5)) if match.group(5) else 0
        journal = match.group(6).strip() if match.group(6) else ""
        abstract = match.group(7).strip() if match.group(7) else ""

        # Clean abstract - remove leading whitespace
        abstract = re.sub(r"\s+", " ", abstract).strip()

        if authors_str.endswith(" et al."):
            authors_str = authors_str[:-7]

        authors_list = [
            {"name": n.strip()}
            for n in authors_str.split(",")
            if n.strip()
        ]

        paper = {
            "title": title,
            "authors": authors_list,
            "venue": journal,
            "year": int(year) if year else 0,
            "abstract": abstract,
            "citationCount": citations,
            "url": url,
            "citationStyles": {
                "bibtex": _generate_bibtex(title, authors_str, journal, year)
            },
        }
        papers.append(paper)

    return papers





class ConsensusSearchTool(BaseTool):
    def __init__(
        self,
        name: str = "SearchConsensus",
        description: str = (
            "Search for relevant literature using Consensus. "
            "Provide a search query to find relevant papers."
        ),
        max_results: int = 10,
    ):
        parameters = [
            {
                "name": "query",
                "type": "str",
                "description": "The search query to find relevant papers.",
            }
        ]
        super().__init__(name, description, parameters)
        self.max_results = max_results
        self.token = get_access_token()
        if not self.token:
            warnings.warn(
                "No Consensus OAuth token found. "
                "Open opencode and authenticate Consensus MCP first."
            )

    def use_tool(self, query: str) -> Optional[str]:
        papers = search_for_papers(query, result_limit=self.max_results)
        if papers:
            return self._format_papers(papers)
        else:
            return "No papers found."

    def _format_papers(self, papers: List[Dict]) -> str:
        paper_strings = []
        for i, paper in enumerate(papers):
            authors = _format_authors(paper.get("authors", []))
            paper_strings.append(
                f"""{i + 1}: {paper.get("title", "Unknown Title")}. {authors}. {paper.get("venue", "Unknown Venue")}, {paper.get("year", "Unknown Year")}.
Number of citations: {paper.get("citationCount", "N/A")}
Abstract: {paper.get("abstract", "No abstract available.")}"""
            )
        return "\n\n".join(paper_strings)


def search_for_papers(query, result_limit=10) -> Union[None, List[Dict]]:
    if not query:
        return None

    for attempt in range(3):
        try:
            rsp = _mcp_call("tools/call", {
                "name": "search",
                "arguments": {"query": query},
            })
            break
        except requests.exceptions.RequestException as e:
            print(f"Consensus request failed (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                return None

    if "error" in rsp:
        print(f"Consensus API error: {rsp['error']}")
        if isinstance(rsp["error"], dict):
            print(f"  {rsp['error'].get('message', '')}")
        return None

    result = rsp.get("result", {})
    is_error = result.get("isError", False)
    if is_error:
        print(f"Consensus search tool returned error")
        return None

    content = result.get("content", [])
    text_blob = ""
    for item in content:
        if item.get("type") == "text":
            text_blob += item.get("text", "") + "\n"

    papers = _parse_papers_from_text(text_blob)

    papers.sort(key=lambda x: x.get("citationCount", 0), reverse=True)
    papers = papers[:result_limit]

    time.sleep(1.0)

    if not papers:
        return None
    return papers
