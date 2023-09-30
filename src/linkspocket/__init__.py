import typing as T
import argparse, json, urllib.request
from . import serialize, cli
from .httplib import handlers
from .oci.core import descriptor, manifest
from .oci import http
import io

def opener_from_cli(_: argparse.Namespace) -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(handlers.DontThrowExceptions())

def main(argv: T.List[str]) -> int:
    args = cli.args().parse_args(argv)

    with open(args.rom, "rb") as fh:
        d = descriptor.from_stream(fh, content_type="application/sudonters.z64")
        d.annotations["org.opencontainers.image.title"] = "rom.z64"
        fh.seek(0, 0)
        c = descriptor.Descriptor.empty("application/sudonters.config")
        m = manifest.Manifest("application/sudonters.zootr.seed", config=c)
        m.add_layer(d)
        opener = opener_from_cli(args)
        blobs = http.BlobPusher(args.registry, opener)
        blobs.push_blob("zootr", d, fh)
        blobs.push_blob("zootr", c, io.BytesIO(b'{}'))
        manifests = http.ManifestPusher(args.registry, opener)
        manifests.push_manifest("zootr", "testrom", m)

    print(json.dumps(m, cls=serialize.OciEncoder, indent=4))
    return 0
