# -*- coding: utf-8 -*-

class Technology:
    def __init__(
            self,
            name: str,
            categories,
            url,
            headers,
            cookies,
            html,
            meta,
            scripts,
            js,
            implies,
            excludes,
            icon: str,
            website: str,
            cpe: str,
    ):
        self.name = name
        self.categories = categories
        self.url = url
        self.headers = headers
        self.cookies = cookies
        self.html = html
        self.meta = meta
        self.scripts = scripts
        self.js = js
        self.implies = implies
        self.excludes = excludes
        self.icon = icon
        self.website = website
        self.cpe = cpe

    def __getitem__(self, k):
        return self.__dict__[k]

    def get(self, *args, **kwargs):
        return self.__dict__.get(*args, **kwargs)

    def __repr__(self):
        return repr(self.__dict__)


class Category:
    def __init__(self, id: str, name: str, priority: int):
        self.id = id
        self.name = name
        self.priority = priority


class Pattern:

    def __init__(
            self,
            value: str,
            regex,
            confidence: int,
            version: str,
            key: str
    ):
        self.value = value
        self.regex = regex
        self.confidence = confidence
        self.version = version
        self.key = key

    def __getitem__(self, k):
        return self.__dict__[k]

    def __repr__(self):
        return repr(self.__dict__)


class Imply:
    """Structure to define a technology that is implied by the use of another
    one.

    Attributes:
        name (str): Name of the implied technology.
        confidence (int): Confidence of the implied technology.

    """

    def __init__(self, name: str, confidence: int):
        self.name = name
        self.confidence = confidence


class Exclude:
    """Structure to define a technology that is incompatible with another
    one.

    Attributes:
        name (str): Name of the excluded technology.

    """

    def __init__(self, name: str):
        self.name = name


class PatternMatch:
    """Identifies a match in a technology pattern.

    Attributes:
        technology (Technology): Technology identified by the pattern.
        pattern (Pattern): Pattern that cause the match.
        version (str): Version identified by the pattern in the match.
    """

    def __init__(self, technology: Technology, pattern: Pattern, version: str):
        self.technology = technology
        self.pattern = pattern
        self.version = version

    def __getitem__(self, k):
        return self.__dict__[k]

    def __repr__(self):
        return repr(self.__dict__)

    def __eq__(self, o):
        return (
                self.technology.name == o.technology.name
                and self.pattern.key == self.pattern.key
                and self.pattern.value == self.pattern.value
        )

    def __hash__(self):
        return hash(
            (self.technology.name, self.pattern.key, self.pattern.value)
        )


class TechMatch:
    """Identifies a match in a technology.

    Attributes:
        technology (Technology): Technology identified.
        confidence (int): Confidence in the match, is derivated from all the
            patterns of this technology that matched.
        version (str): Version identified by the patterns.
    """

    def __init__(self, technology: Technology, confidence: int, version: str):
        self.technology = technology
        self.confidence = confidence
        self.version = version

    def __getitem__(self, k):
        return self.__dict__[k]

    def __repr__(self):
        return repr(self.__dict__)

    def __eq__(self, o):
        return self.technology.name == o.technology.name
