# A blob is arbitrary data that is stored in an OCI registry. For container
# images, they are individual unionFS slices and container configuration files.
# Blobs are referenced by Descriptors, which carry the blob's digest, size in
# bytes and content-type.

import dataclasses as dc
import typing as T

from ... import streams
from . import descriptor


class Pusher(T.Protocol):
    def push_blob(
        self,
        repository: str,
        descriptor: descriptor.Descriptor,
        content: streams.Reader,
    ) -> None:
        ...


class Puller(T.Protocol):
    def pull_blob(self, repository: str, digest: descriptor.Digest) -> streams.MustCloseReader:
        ...

    def does_blob_exist(self, repository: str, digest: descriptor.Digest) -> bool:
        ...


@dc.dataclass()
class PullPusher(Puller, Pusher):
    _pull: Puller
    _push: Pusher

    def push_blob(self, repository: str, descriptor: descriptor.Descriptor, content: streams.Reader) -> None:
        if self.does_blob_exist(repository, descriptor.digest):
            return

        return self._push.push_blob(repository, descriptor, content)

    def does_blob_exist(self, repository: str, digest: descriptor.Digest) -> bool:
        return self._pull.does_blob_exist(repository, digest)

    def pull_blob(self, repository: str, digest: descriptor.Digest) -> streams.MustCloseReader:
        return self._pull.pull_blob(repository, digest)
