
_BASE_MEDIA_TYPE = "application/sudonters.zootr.seed"
_ANNOTATION_BASE = "etc.sudonters.zootr"


def annotation(s: str) -> str:
    return f"{_ANNOTATION_BASE}.{s}".lower()


def type(s: str) -> str:
    return f"{_BASE_MEDIA_TYPE}.{s}".lower()


def parse_type(s: str) -> str | None:
    if not s.startswith(_BASE_MEDIA_TYPE):
        return None
    return s[len(_BASE_MEDIA_TYPE)+1:]
