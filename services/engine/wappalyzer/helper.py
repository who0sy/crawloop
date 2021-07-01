# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from typing import Any
import re

from wappalyzer.modelcalss import Pattern


def _transform_patterns(
        patterns: Any,
        case_sensitive: bool = False
):
    """Canonicalize the patterns of different sections.
    """

    def to_list(value):
        return value if type(value) is list else [value]

    if not patterns:
        return []

    if type(patterns) is str or type(patterns) is list:
        patterns = {
            "main": patterns
        }

    parsed = {}
    for key in patterns:
        name = key if case_sensitive else key.lower()
        parsed[name] = [
            _parse_pattern(ptrn, key)
            for ptrn in to_list(patterns[key])
        ]

    return parsed["main"] if "main" in parsed else parsed


def _parse_pattern(pattern: str, key: str = ""):
    """Parse the regex pattern and creates a Pattern object.
    It extracts the regex, the version and the confidence values of
    the given string.
    """
    parts = pattern.split("\\;")

    value = parts[0]

    # seems that in js "[^]" is similar to ".", however python
    # re interprets in a diferent way (which leads to an error),
    # so it is better to substitute it
    regex = value.replace("/", "\\/").replace("[^]", ".")

    attrs = {
        "value": value,
        "regex": re.compile(regex, re.I)
    }
    for attr in parts[1:]:
        attr = attr.split(":")
        if len(attr) > 1:
            attrs[attr[0]] = ":".join(attr[1:])

    return Pattern(
        value=attrs["value"],
        regex=attrs["regex"],
        confidence=int(attrs.get("confidence", 100)),
        version=attrs.get("version", ""),
        key=key,
    )


def extract_scripts(html: str):
    soup = BeautifulSoup(html, "html.parser")
    script_tags = soup.findAll("script")

    scripts = []
    for script_tag in script_tags:
        try:
            src = script_tag.attrs["src"]
            if not src.startswith("data:text/javascript;"):
                scripts.append(src)
        except KeyError:
            pass

    return scripts


def extract_metas(html: str):
    soup = BeautifulSoup(html, "html.parser")
    meta_tags = soup.findAll("meta")

    metas = {}
    for meta_tag in meta_tags:
        try:
            key = meta_tag.attrs.get("name", None) \
                  or meta_tag.attrs["property"]
            metas[key.lower()] = [meta_tag.attrs["content"]]
        except KeyError:
            continue

    return metas


def extract_cookies(cookies_list):
    cookies_dict = {}
    for each_cookie in cookies_list:
        cookies_dict.update({each_cookie['name']: each_cookie['value']})
    return cookies_dict


def extract_headers(headers):
    return {
        k.lower(): [v]
        for k, v in headers.items()
    }
