import dataclasses as dc
import http.client as http
import json
import typing as T
import urllib.request as urlreq

from linkspocket.oci.core import descriptor

from .. import json as ocijson
from ..core import manifest


@dc.dataclass()
class ManifestPusher(manifest.Pusher):
    _registry: str
    _opener: urlreq.OpenerDirector
    _proto: str = "https"

    def push_manifest(
        self, repository: str, reference: str, manifest: manifest.Manifest
    ) -> None:
        serialized = json.dumps(manifest, cls=ocijson.OciEncoder, indent=4)
        encoded_manifest = serialized.encode()

        req = urlreq.Request(
            f"{self._proto}://{self._registry}/v2/{repository}/manifests/{reference}",
            method="PUT",
            data=encoded_manifest,
        )
        req.add_header(
            "Content-Type", "application/vnd.oci.image.manifest.v1+json")

        with self._opener.open(req):
            pass


@dc.dataclass()
class ManifestPuller(manifest.Puller):
    _registry: str
    _opener: urlreq.OpenerDirector
    _proto: str = "https"

    def does_manifest_exist(self, repository: str, reference: str) -> bool:
        req = urlreq.Request(
            f"{self._proto}://{self._registry}/v2/{repository}/manifests/{reference}",
            method="HEAD",
        )

        req.add_header(
            "Content-Type", "application/vnd.oci.image.manifest.v1+json")

        with self._opener.open(req) as rh:
            resp = T.cast(http.HTTPResponse, rh)
            return resp.status == 200

    def pull_manifest(
        self, repository: str, reference: str
    ) -> T.Optional[manifest.Manifest]:
        req = urlreq.Request(
            f"{self._proto}://{self._registry}/v2/{repository}/manifests/{reference}",
            method="GET",
        )

        req.add_header(
            "Accept", "application/vnd.oci.image.manifest.v1+json")

        with self._opener.open(req) as rh:
            resp = T.cast(http.HTTPResponse, rh)
            j = json.load(resp)
            m = manifest.Manifest(
                j.get("artifactType", j.get("mediaType", "")),
                descriptor.load_from(j["config"]),
            )

            for l in j["layers"]:
                m.add_layer(descriptor.load_from(l))

        return m
