# -*- coding: utf-8 -*-

import json
import re
from functools import partial

from wappalyzer.helper import _transform_patterns, extract_scripts, extract_cookies, extract_metas, extract_headers
from wappalyzer.modelcalss import Category, Technology, Imply, Exclude, PatternMatch, TechMatch


class WappalyzerHandler(object):

    def __init__(self, techno_path):
        self.categories, self.technologies = self.parse_file(techno_path)

    @staticmethod
    def parse_file(file_path):
        with open(file_path) as json_file:
            json_dict = json.load(json_file)

        # 解析categories
        categories = {
            id: Category(id=id, name=cat['name'], priority=cat['priority'])
            for id, cat in json_dict['categories'].items()
        }

        # 解析technologies
        technologies = {
            name: Technology(
                name=name,
                categories=[categories[str(c)] for c in techno.get("cats", [])],
                url=_transform_patterns(techno.get("url", None)),
                headers=_transform_patterns(techno.get("headers", None)),
                cookies=_transform_patterns(techno.get("cookies", None)),
                html=_transform_patterns(techno.get("html", None)),
                meta=_transform_patterns(techno.get("meta", None)),
                scripts=_transform_patterns(techno.get("scripts", None)),
                js=_transform_patterns(techno.get("js", None), True),
                implies=[
                    Imply(name=pt.value, confidence=pt.confidence)
                    for pt in _transform_patterns(techno.get("implies", None))
                ],
                excludes=[
                    Exclude(name=pt.value)
                    for pt in _transform_patterns(techno.get("excludes", None))
                ],
                icon=techno.get("icon", ""),
                website=techno.get("website", ""),
                cpe=techno.get("cpe", ""),
            )
            for name, techno in json_dict["technologies"].items()
        }

        return categories, technologies

    def discover_technologies(
            self,
            url: str = "",
            html: str = "",
            cookies=None,
            headers=None
    ):
        try:
            pattern_matches = self.match_all(
                self.technologies,
                url=url,
                html=html,
                scripts=extract_scripts(html),
                cookies=extract_cookies(cookies),
                metas=extract_metas(html),
                headers=extract_headers(headers),
            )
            source_results = self.resolve_techno_matches(self.technologies, pattern_matches)

        except Exception as e:
            source_results = []

        return [{
            'name': each_result.technology.name,
            'categories': [cate.name for cate in each_result.technology.categories],
            'version': each_result.version,
            'confidence': each_result.confidence,
        } for each_result in source_results]

    def match_all(
            self,
            technologies,
            url="",
            html="",
            scripts=None,
            cookies=None,
            metas=None,
            headers=None,
            js_vars=None,
    ):
        def match_parts(techno, funcs):
            for func in funcs:
                yield from func(techno)

        match_funcs = []

        if url:
            match_funcs.append(partial(self.match_url, url=url))

        if headers:
            match_funcs.append(partial(self.match_headers, headers=headers))

        if cookies:
            match_funcs.append(partial(self.match_cookies, cookies=cookies))

        if html:
            match_funcs.append(partial(self.match_html, html=html))

        if metas:
            match_funcs.append(partial(self.match_metas, metas=metas))

        if scripts:
            match_funcs.append(partial(self.match_scripts, scripts=scripts))

        if js_vars:
            match_funcs.append(partial(self.match_js_vars, js_vars=js_vars))

        match_techno = partial(match_parts, funcs=match_funcs)

        for technology in technologies.values():
            yield from match_techno(technology)

    def match_url(self, technology: Technology, url: str):
        return self.match_str(technology, "url", url)

    def match_html(self, technology: Technology, html: str):
        return self.match_str(technology, "html", html)

    def match_scripts(
            self,
            technology: Technology,
            scripts
    ):
        return self.match_list(technology, "scripts", scripts)

    def match_js_vars(
            self,
            technology: Technology,
            js_vars,
    ):
        """Wrapper to search for matches in javascript variables."""
        return self.match_pairs(technology, "js", js_vars)

    def match_cookies(
            self,
            technology: Technology,
            cookies
    ):
        return self.match_pairs(technology, "cookies", cookies)

    def match_metas(
            self,
            technology: Technology,
            metas
    ):
        return self.match_pairs(technology, "meta", metas)

    def match_headers(
            self,
            technology: Technology,
            headers
    ):
        return self.match_pairs(technology, "headers", headers)

    def match_str(
            self,
            tech: Technology,
            field: str,
            value: str
    ):
        """To match attributes against a string, like an URL or HTML content.

        Args:
            tech (Technology): The technology to search matches
            field (str): The field to look for matches. Must be "url" or "html".
            value (str)

        Returns:
            Iterator[PatternMatch]: An iterator with the found matches.

        """
        return self._match_patterns(tech[field], tech, value)

    def match_list(
            self,
            tech: Technology,
            field: str,
            values
    ):
        """To match against a list of string, like some js scripts URIs.

        Args:
            tech (Technology): The technology to search matches
            field (str): The field to look for matches. Must be "scripts".
            values (List[str])

        Returns:
            Iterator[PatternMatch]: An iterator with the found matches.
        """
        for value in values:
            patterns = tech.get(field, [])
            yield from self._match_patterns(patterns, tech, value)

    def match_pairs(
            self,
            tech: Technology,
            field: str,
            pairs
    ):
        """To analyze attributes that are a dict with keys and values.
        Such as headers, cookies and meta tags.

        Args:
            tech (Technology): The technology to search matches
            field (str): The field to look for matches. Must be "cookies"
                "headers" or "meta".
            pairs (Dict[str, List[str]])

        Returns:
            Iterator[PatternMatch]: An iterator with the found matches.

        """

        if field in ["cookies"]:
            pairs_local = {}
            for k in pairs:
                pairs_local[k.lower()] = pairs[k]
        else:
            pairs_local = pairs

        for key in tech[field]:
            # get patterns this way since pairs could be a dict or empty list
            patterns = tech[field][key] or []
            values = pairs_local.get(key, [])

            for value in values:
                yield from self._match_patterns(patterns, tech, value)

    def _match_patterns(
            self,
            patterns,
            technology: Technology,
            value: str
    ):
        """Check the regexes of the patterns against the value"""
        for pattern in patterns:
            if pattern.regex.search(value):
                yield PatternMatch(
                    technology=technology,
                    pattern=pattern,
                    version=self._resolve_version(
                        pattern.version,
                        pattern.regex,
                        value
                    )
                )

    def _resolve_version(
            self,
            version: str,
            regex,
            value: str
    ) -> str:
        """Extracts the version from the match, used the matched group
        indicated by an string with format: "\\1" or
        "\\1?value_1:value_2" (ternary version) in the \\;version field
        of the regex
        """
        if not version:
            return version

        matches = regex.search(value)

        if not matches:
            return version

        resolved = version
        matches = [matches.group()] + list(matches.groups())
        for index, match in enumerate(matches):
            ternary = re.search("\\\\{}\\?([^:]+):(.*)$".format(index), version)

            if ternary:
                ternary = [ternary.group()] + list(ternary.groups())

                if len(ternary) == 3:
                    resolved = version.replace(
                        ternary[0],
                        ternary[1] if match else ternary[2]
                    )

            resolved = resolved.strip().replace(
                "\\{}".format(index),
                match or ""
            )

        return resolved

    def resolve_techno_matches(
            self,
            technologies,
            pattern_matches
    ):
        """Extracts from the pattern matches, the matches in technology and
        resolve the implied and excluded technology.
        """
        pattern_matches = list(set(pattern_matches))
        techno_matches = self.extract_techno_matches(pattern_matches)
        techno_matches = self.resolve_implies(techno_matches, technologies)
        techno_matches = self.resolve_excludes(techno_matches)
        return techno_matches

    def extract_techno_matches(
            self,
            pattern_matches
    ):
        """Extracts the technologies in the matches, adjusting the version
        and confidence, and removing duplicates.
        """
        techno_matches = []
        for pattern_match in pattern_matches:
            if pattern_match not in techno_matches:
                version = ""
                confidence = 0

                for pt_match in pattern_matches:
                    if pt_match != pattern_match:
                        continue

                    confidence = min(100, confidence + pt_match.pattern.confidence)
                    version = pt_match.version \
                        if len(version) < len(pt_match.version) <= 10 \
                        else version

                techno_matches.append(TechMatch(
                    pattern_match.technology,
                    confidence,
                    version
                ))
        return techno_matches

    def resolve_implies(
            self,
            techno_matches,
            technologies,
    ):
        """Generates a list that includes the technology matches and
        the technologies implied by the first ones. Also avoid the duplicates.
        """
        for techno_match in techno_matches:
            self._loop(techno_match, technologies, techno_matches)
        return techno_matches

    def _loop(self, techno_match, technologies, techno_matches):
        for imply in techno_match.technology.implies:
            tech_match_obj = TechMatch(
                technology=technologies[imply.name],
                confidence=min(imply.confidence, techno_match.confidence),
                version=''
            )

            if tech_match_obj not in techno_matches:
                techno_matches.append(tech_match_obj)
                self._loop(tech_match_obj, technologies, techno_matches)

    def _resolve_implies_inner(
            self,
            techno_impls,
            techno_match,
            technologies
    ):
        if techno_match not in techno_impls:
            techno_impls.append(techno_match)
            implies = [
                TechMatch(
                    technology=technologies[imply.name],
                    confidence=min(imply.confidence, techno_match.confidence),
                    version=''
                )
                for imply in techno_match.technology.implies
            ]
            for implied_techno in implies:
                self._resolve_implies_inner(techno_impls, implied_techno, technologies)

    def resolve_excludes(
            self,
            techno_matches,
    ):
        """Generates a list that not includes the technology matches
         that cause conflict with others, by letting only an excludent option.
        """
        # Avoids the destruction of the original list
        techno_matches = techno_matches[:]
        techn_excls = []

        try:
            while True:
                techno_match = techno_matches.pop(0)
                techn_excls.append(techno_match)

                excludes = [ex.name for ex in techno_match.technology.excludes]
                techno_matches = [
                    tm for tm in techno_matches
                    if tm.technology.name not in excludes
                ]

        except IndexError:
            pass

        return techn_excls
