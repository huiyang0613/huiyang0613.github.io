#!/usr/bin/env python3
"""Build the single-page homepage with Python's standard library only."""
from pathlib import Path
from collections import defaultdict
from string import Template
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]


class _HTMLElement:
    def __init__(self, tag, opening):
        self.tag = tag
        self.opening = opening
        self.children = []
        self.closing = ""

    def raw(self):
        return self.opening + "".join(
            child if isinstance(child, str) else child.raw() for child in self.children
        ) + self.closing


class _HTMLTree(HTMLParser):
    VOID_TAGS = frozenset("area base br col embed hr img input link meta param source track wbr".split())

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.line_offsets = [0] + [match.end() for match in re.finditer("\n", source)]
        self.root = _HTMLElement(None, "")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        element = _HTMLElement(tag, self.get_starttag_text())
        self.stack[-1].children.append(element)
        if tag not in self.VOID_TAGS:
            self.stack.append(element)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(_HTMLElement(tag, self.get_starttag_text()))

    def handle_endtag(self, tag):
        if len(self.stack) == 1 or self.stack[-1].tag != tag:
            raise ValueError(f"Cannot format mismatched closing tag: </{tag}>")
        line, column = self.getpos()
        start = self.line_offsets[line - 1] + column
        self.stack.pop().closing = self.source[start:self.source.index(">", start) + 1]

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def handle_decl(self, decl):
        self.stack[-1].children.append(_HTMLElement(None, f"<!{decl}>"))

    def handle_comment(self, data):
        self.stack[-1].children.append(_HTMLElement(None, f"<!--{data}-->"))

    def handle_pi(self, data):
        self.stack[-1].children.append(_HTMLElement(None, f"<?{data}>"))


def format_html(source):
    """Indent the site's structural HTML without splitting text or inline markup."""
    parser = _HTMLTree(source)
    parser.feed(source)
    parser.close()
    if len(parser.stack) != 1:
        raise ValueError(f"Cannot format unclosed tag: <{parser.stack[-1].tag}>")

    containers = frozenset(
        "html head body header nav main section article aside div ul ol li "
        "figure figcaption footer blockquote form svg symbol defs g button".split()
    )
    blocks = (containers - {"button"}) | frozenset(
        "meta link script style title p h1 h2 h3 h4 h5 h6 pre textarea "
        "img video source path hr".split()
    )

    def render(element, depth):
        prefix = "  " * depth
        if isinstance(element, str):
            return prefix + element if element.strip() else ""
        if (element.tag not in containers or not element.children or
                any(isinstance(child, str) and child.strip() for child in element.children)):
            return prefix + element.raw()

        lines = [prefix + element.opening]
        inline = []

        def flush_inline():
            nodes = [node for node in inline if not isinstance(node, str) or node.strip()]
            if len(nodes) == 1:
                lines.append(render(nodes[0], depth + 1))
            elif nodes:
                # Keep adjacent inline tags adjacent; existing normal-flow spaces stay spaces.
                text = "".join(" " if isinstance(node, str) else node.raw() for node in inline).strip()
                lines.append("  " * (depth + 1) + text)
            inline.clear()

        for child in element.children:
            if isinstance(child, _HTMLElement) and (child.tag in blocks or child.tag is None):
                flush_inline()
                lines.append(render(child, depth + 1))
            else:
                inline.append(child)
        flush_inline()
        if element.closing:
            lines.append(prefix + element.closing)
        return "\n".join(lines)

    return "\n".join(filter(None, (render(child, 0) for child in parser.root.children))) + "\n"


def esc(value):
    return escape(str(value), quote=True)


def link(url, label, css=""):
    if urlparse(url).scheme not in {"https", "http", "mailto"}:
        raise ValueError(f"Unsupported link: {url}")
    extra = ' target="_blank" rel="noopener noreferrer"' if not url.startswith("mailto:") else ""
    class_attr = f' class="{css}"' if css else ""
    return f'<a href="{esc(url)}"{class_attr}{extra}>{label}</a>'


def asset(path):
    if Path(path).is_absolute() or ".." in Path(path).parts or not (ROOT / path).is_file():
        raise ValueError(f"Missing or invalid local asset: {path}")
    return esc(path)



def publications():
    rows = []
    for path in (ROOT / "_publications").glob("*.json"):
        if path.name.startswith("_"):
            continue
        paper = json.loads(path.read_text(encoding="utf-8"))
        for field in ("title", "venue", "authors", "media", "links", "selected"):
            if field not in paper:
                raise ValueError(f"{path.name}: missing {field}")
        if not isinstance(paper["selected"], bool):
            raise ValueError(f"{path.name}: selected must be true or false")
        match = re.match(r"^(\d{4})_(0[1-9]|1[0-2])_", path.name)
        if not match:
            raise ValueError(f"{path.name}: use a YYYY_MM_ prefix for publication filenames")
        paper["_year"] = int(match.group(1))
        paper["_filename"] = path.name
        rows.append(paper)
    return sorted(rows, key=lambda row: row["_filename"], reverse=True)


def render_paper(paper, person_name):
    authors = []
    for author in paper["authors"]:
        label = esc(author["name"])
        if author["name"].rstrip("*").strip() == person_name:
            label = f"<strong>{label}</strong>"
        if author.get("url"):
            label = link(author["url"], label)
        authors.append(label)
    media = paper["media"]
    if media["type"] == "video":
        visual = (f'<video data-src="{asset(media["src"])}" poster="{asset(media["poster"])}" '
                  f'muted autoplay loop playsinline preload="none" aria-label="Video preview: {esc(paper["title"])}"></video>')
    elif media["type"] == "image":
        if media.get("hover_src"):
            visual = (f'<button class="publication-image-switch" type="button" data-preview-switch '
                      f'data-show-alternate="false" aria-pressed="false" '
                      f'aria-label="Alternate preview: {esc(paper["title"])}">'
                      f'<img class="preview-default" src="{asset(media["src"])}" alt="" loading="lazy" decoding="async" draggable="false">'
                      f'<img class="preview-alternate" src="{asset(media["hover_src"])}" alt="" loading="lazy" decoding="async" draggable="false">'
                      '</button>')
        else:
            visual = f'<img src="{asset(media["src"])}" alt="{esc(paper["title"])} — research overview" loading="lazy" decoding="async">'
    else:
        raise ValueError(f"Unknown media type: {media['type']}")
    links_html = "".join(link(item["url"], esc(item["label"])) for item in paper["links"])
    links_html = f'<div class="publication-links">{links_html}</div>' if links_html else ""
    highlight = f' <span class="publication-highlight">· {esc(paper["highlight"])}</span>' if paper.get("highlight") else ""
    summary = f'<p class="publication-summary">{esc(paper["summary"])}</p>' if paper.get("summary") else ""
    return (f'<article class="publication" data-selected="{str(paper["selected"]).lower()}">'
            f'<div class="publication-media">{visual}</div><div class="publication-info">'
            f'<h4 class="publication-title">{esc(paper["title"])}</h4>'
            f'<p class="publication-authors">{", ".join(authors)}</p>'
            f'<p class="publication-venue">{esc(paper["venue"])}{highlight}</p>'
            f'{links_html}{summary}</div></article>')


def build():
    profile = json.loads((ROOT / "_data/profile.json").read_text(encoding="utf-8"))
    papers = publications()
    grouped = defaultdict(list)
    for paper in papers:
        grouped[paper["_year"]].append(render_paper(paper, profile["name"]))
    publication_html = "\n".join(
        f'<div class="publication-year" data-year="{year}"><h3 class="year-label">{year}</h3>'
        f'<div class="publication-items">{"".join(items)}</div></div>'
        for year, items in grouped.items()
    )
    socials = []
    for index, item in enumerate(profile["socials"]):
        label = (f'<svg class="social-icon" aria-hidden="true"><use href="#icon-{esc(item["icon"])}"></use></svg>'
                 f'<span>{esc(item["label"])}</span>')
        divider = '<span class="social-divider" aria-hidden="true">/</span>' if index < len(profile["socials"]) - 1 else ""
        socials.append(f'<li>{link(item["url"], label)}{divider}</li>')
    experience = []
    for item in profile["experience"]:
        experience.append(
            '<article class="experience-item">'
            f'<div class="institution-logo"><img src="{asset(item["logo"])}" alt="" loading="lazy" decoding="async"></div>'
            '<div class="experience-content"><div class="experience-topline">'
            f'<h3>{link(item["url"], esc(item["institution"]))}</h3>'
            f'<span class="experience-dates">{esc(item["dates"])}</span></div>'
            f'<p class="experience-role">{esc(item["role"])}<span class="experience-location">{esc(item["location"])}</span></p>'
            f'<p class="experience-detail">{esc(item["detail"])}</p>'
            f'<p class="experience-advisors">Advisor{ "s" if " and " in item["advisors"] else ""}: {esc(item["advisors"])}</p>'
            '</div></article>'
        )
    misc = []
    if profile.get("service"):
        misc.append(f'<div><h3>Academic service</h3><p>{esc(profile["service"])}</p></div>')
    interests = "".join(
        f'<p class="additional-interests">{esc(profile[key])}</p>'
        for key in ("interests", "other") if profile.get(key)
    )
    if interests:
        misc.append(f'<div><h3>Beyond research</h3>{interests}</div>')
    equal_contribution = any(
        author["name"].strip().endswith("*")
        for paper in papers for author in paper["authors"]
    )
    content = Template((ROOT / "templates/index.html").read_text(encoding="utf-8")).substitute(
        **{key: esc(profile[key]) for key in ("name", "chinese_name", "role", "institution", "email", "display_email", "description", "service", "interests", "other")},
        portrait=asset(profile["portrait"]),
        icons=(ROOT / "assets/icons.svg").read_text(encoding="utf-8"),
        biography="\n".join(f"<p>{paragraph}</p>" for paragraph in profile["biography"]),
        socials="".join(socials), publications=publication_html,
        experience="\n".join(experience),
        publication_note='<p class="publication-note">* Equal contribution</p>' if equal_contribution else "",
        misc="\n".join(misc)
    )
    (ROOT / "index.html").write_text(format_html(content), encoding="utf-8")
    selected = sum(paper["selected"] for paper in papers)
    print(f"Built and formatted index.html: {len(papers)} visible publications, {selected} selected.")


if __name__ == "__main__":
    build()
