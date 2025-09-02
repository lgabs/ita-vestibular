import re
import json
import requests
from bs4 import BeautifulSoup, NavigableString

URL = "https://www.vestibular.ita.br/estatisticas.htm"


def fetch_sections(url: str) -> dict:
    resp = requests.get(url)
    resp.encoding = "iso-8859-1"
    soup = BeautifulSoup(resp.text, "html.parser")

    sections = {}
    anchors = [
        (a.get("id") or a.get("name"), a)
        for a in soup.find_all("a")
        if (a.get("id") or a.get("name") or "").startswith("dados20")
    ]

    for name, anchor in anchors:
        year = name[-4:]
        node = anchor.next_sibling
        elements = []
        while node and not (
            getattr(node, "name", None) == "a"
            and ((node.get("id") or node.get("name") or "").startswith("dados20"))
        ):
            if not isinstance(node, NavigableString):
                elements.append(node)
            node = node.next_sibling

        data = []
        heading = None
        for el in elements:
            for st in el.find_all("strong"):
                text = st.get_text(" ", strip=True)
                if re.match(r"^\d+\s*-", text):
                    heading = text
            tables = el.find_all("table") if el.name != "table" else [el]
            for table in tables:
                rows = [
                    [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
                    for row in table.find_all("tr")
                ]
                if rows:
                    data.append({"heading": heading, "table": rows})
        sections[year] = data
    return sections


def main():
    sections = fetch_sections(URL)
    with open("estatisticas/estatisticas.json", "w", encoding="utf-8") as fh:
        json.dump(sections, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
