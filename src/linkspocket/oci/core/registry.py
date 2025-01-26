import dataclasses as dc
from . import manifest, blob


@dc.dataclass()
class Registry:
    manifests: manifest.PullPusher
    blobs: blob.PullPusher
