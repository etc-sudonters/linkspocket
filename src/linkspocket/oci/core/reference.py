import dataclasses as dc
import re
import typing as T


@dc.dataclass()
class Reference:
    registry: str
    repository: str
    tag: T.Optional[str]
    digest: T.Optional[str] = None

    @staticmethod
    def _unsafe_blank() -> "Reference":
        return Reference("", "", None)

    def __str__(self) -> str:
        str = f"{self.registry}/{self.repository}"

        if self.tag:
            str = f"{str}:{self.tag}"

        if self.digest:
            str = f"{str}@{self.digest}"

        return str


# https://github.com/oras-project/oras-py/blob/07272eafbd06fe325ecdfd4b9db76efc210fe96c/oras/container.py#L11
# honestly, way fucking nicer than stealing it from containers/image
_reference_re = re.compile(
    "(?:(?P<registry>[^/@]+[.:][^/@]*)/)?"
    "(?P<namespace>(?:[^:@/]+/)+)?"
    "(?P<repository>[^:@/]+)"
    "(?::(?P<tag>[^:@]+))?"
    "(?:@(?P<digest>.+))?"
    "$"
)


def parse(s: str) -> T.Optional[Reference]:
    if (m := _reference_re.search(s)) is None:
        return None

    ref = Reference._unsafe_blank()
    items = m.groupdict()
    if (repo := items.get("repository")) is None:
        raise Exception("no repos?")

    # grumble grumble stupid regex I stole...
    if (namespace := items.get("namespace")) is not None:
        repo = f"{namespace}{repo}"

    ref.registry = items.get("registry", "localhost:5000")
    ref.repository = repo
    ref.tag = items.get("tag")
    ref.digest = items.get("digest")
    return ref
