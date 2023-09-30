from ...httplib import url
import io
import urllib.request as urlreq
import urllib.parse as urlparse
import http.client as http
import typing as T


from ..core import blob, descriptor


class BlobPusher(blob.BlobPusher):
    _MIN_CHUNK_SIZE = 1024 * 64

    def __init__(self, registry: str, opener: urlreq.OpenerDirector) -> None:
        self._opener = opener
        self._registry = registry
    

    def push_blob(self, repository: str, descriptor: descriptor.Descriptor, content: io.BufferedIOBase) -> None:
        req = urlreq.Request(f"http://{self._registry}/v2/{repository}/blobs/uploads/", method="POST")

        with self._opener.open(req) as rh:
            resp = T.cast(http.HTTPResponse, rh)
            location = resp.getheader("location")

        location = self._chunked_upload(T.cast(str, location), descriptor, content)
        self._finalize_upload(location, descriptor)


    def _chunked_upload(self, location: str, descriptor: descriptor.Descriptor, content: io.BufferedIOBase) -> str:
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
