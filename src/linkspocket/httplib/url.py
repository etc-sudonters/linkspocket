import typing as T
import urllib.parse as urlparse


class Builder:
    scheme: str
    host: str
    path: str
    params: str
    query: T.Dict[str, T.List[str]]
    fragment: str

    def __init__(self, p: urlparse.ParseResult):
        self.scheme = p.scheme
        self.host = p.netloc
        self.path = p.path
        self.params = p.params
        self.query = urlparse.parse_qs(p.query)
        self.fragment = p.fragment

    def __str__(self) -> str:
        return urlparse.urlunparse(
            (
                self.scheme,
                self.host,
                self.path,
                self.params,
                urlparse.urlencode(self.query, doseq=True),
                self.fragment,
            )
        )

    @staticmethod
    def from_str(url: str) -> 'Builder':
        return Builder(urlparse.urlparse(url))
