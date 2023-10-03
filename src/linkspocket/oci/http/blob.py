from os import stat
from ...httplib import url
from ... import streams
import urllib.request as urlreq
import urllib.parse as urlparse
import http.client as http
import typing as T
import dataclasses as dc


from ..core import blob, descriptor


@dc.dataclass()
class BlobPusher(blob.Pusher):
    _registry: str
    _opener: urlreq.OpenerDirector

    _MIN_CHUNK_SIZE = 1024 * 64

    def push_blob(self, repository: str, descriptor: descriptor.Descriptor, content: streams.Reader) -> None:
        req = urlreq.Request(f"http://{self._registry}/v2/{repository}/blobs/uploads/", method="POST")

        with self._opener.open(req) as rh:
            resp = T.cast(http.HTTPResponse, rh)
            location = resp.getheader("location")

        location = self._chunked_upload(T.cast(str, location), descriptor, content)
        self._finalize_upload(location, descriptor)


    def _chunked_upload(self, location: str, descriptor: descriptor.Descriptor, content: streams.Reader) -> str:
        offset = 0

        while offset < descriptor.bytes:
            chunk = content.read(BlobPusher._MIN_CHUNK_SIZE)
            chunk_start = offset
            chunk_end = offset + len(chunk) - 1 # content range is 0 indexed

            b = url.Builder.from_str(location)
            this_url = str(b)

            req = urlreq.Request(
                    this_url,
                    method="PATCH",
                    data=chunk,
                    headers={
                        "Content-Length": str(len(chunk)),
                        "Content-Range": f"{chunk_start}-{chunk_end}",
                        "Content-Type": "application/octet-stream",
                        })

            with self._opener.open(req) as rh:
                resp = T.cast(http.HTTPResponse, rh)
                location = T.cast(str, resp.getheader("location"))

            offset += len(chunk)

        return location

    def _finalize_upload(self, location: str, descriptor: descriptor.Descriptor) -> None:
        builder = url.Builder(urlparse.urlparse(location))
        builder.query["digest"] = [str(descriptor.digest)]
        req = urlreq.Request(str(builder), method="PUT")

        with self._opener.open(req):
            pass

@dc.dataclass()
class BlobPuller(blob.Puller):
    _registry: str
    _opener: urlreq.OpenerDirector

    def does_blob_exist(self, repository: str, digest: descriptor.Digest) -> bool:
        req = urlreq.Request(f"http://{self._registry}/v2/{repository}/blobs/{digest}")

        with self._opener.open(req) as rh:
            resp = T.cast(http.HTTPResponse, rh)
            return resp.status == 200

    def pull_blob(self, repository: str, digest: descriptor.Digest) -> streams.Reader:
        return super().pull_blob(repository, digest)
