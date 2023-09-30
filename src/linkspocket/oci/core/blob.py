# A blob is arbitrary data that is stored in an OCI registry. For container
# images, they are individual unionFS slices and container configuration files.
# Blobs are referenced by Descriptors, which carry the blob's digest, size in
# bytes and content-type.

import io

from . import descriptor
import typing as T


class BlobPusher(T.Protocol):
    def push_blob(self, repository: str, descriptor: descriptor.Descriptor, content: io.BufferedIOBase) -> None:
        ...

class BlobPuller(T.Protocol):
    def pull_blob(self, repository: str, digest: descriptor.Digest) -> io.BufferedReader:
        ...

    def does_blob_exist(self, repository: str, digest: descriptor.Digest) -> bool:
        ...

class BlobPushPuller(BlobPusher, BlobPuller, T.Protocol):
    ... 
