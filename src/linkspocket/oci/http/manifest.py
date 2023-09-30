import dataclasses as dc
import json
import urllib.request as urlreq
import io

from ... import serialize
from ..core import manifest


@dc.dataclass()
class ManifestPusher(manifest.ManifestPusher):
    _registry: str
    _opener: urlreq.OpenerDirector

    def push_manifest(
        self, repository: str, reference: str, m: manifest.Manifest
    ) -> None:
        serialized = json.dumps(m, cls=serialize.OciEncoder, indent=4)
        encoded_manifest = serialized.encode()

        req = urlreq.Request(
            f"http://{self._registry}/v2/{repository}/manifests/{reference}",
            method="PUT",
            data=encoded_manifest,
        )
        req.add_header("Content-Type", "application/vnd.oci.image.manifest.v1+json")

        with self._opener.open(req) as rh:
            msg = io.TextIOWrapper(rh)
            for l in msg.readlines():
                print(l)
            print("poop pants")

