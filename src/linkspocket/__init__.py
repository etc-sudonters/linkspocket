import argparse
import pathlib
import sys
import urllib.request

from .httplib import handlers
from .oci.core import descriptor, manifest
from .oci import http as ocihttp
from . import seed, serialize
import json

_BASE_MEDIA_TYPE = "application/sudonters.zootr.seed"

def opener_from_cli(_: argparse.Namespace) -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(handlers.DontThrowExceptions())


def main(args: argparse.Namespace) -> int:
    if not args.dir.exists():
        print(f"{args.dir} does not exist", file=sys.stderr)
        return 2

    if not args.dir.is_dir():
        print(f"{args.dir} is not a directory", file=sys.stderr)
        return 3

    m = _zootr_manifest_from_dir(args.dir)
    print(json.dumps(m, cls=serialize.OciEncoder, indent=4))

    opener = opener_from_cli(args)
    blobs = ocihttp.BlobPusher(args.registry, opener)
    manifests = ocihttp.ManifestPusher(args.registry, opener)

    for l in m.layers:
        blobs.push_blob(args.repository, l, l.content)

    blobs.push_blob(args.repository, m.config, m.config.content)

    manifests.push_manifest(args.repository, args.tag, m)

    return 0


def _zootr_manifest_from_dir(p: pathlib.Path) -> manifest.Manifest:
    m = manifest.Manifest(
            _BASE_MEDIA_TYPE,
        descriptor.Descriptor.empty(),
    )
    
    for zf in seed.scan_directory(p):
        media_type = f"{_BASE_MEDIA_TYPE}.{zf.kind.name}".lower()

        fh = zf.open()
        d = descriptor.from_stream(fh, media_type)
        d.annotations["org.opencontainers.image.title"] = zf.path.name
        m.add_layer(d)

    return m
