import argparse
import json
import pathlib
import sys
import typing as T
import urllib.request

from linkspocket.zootrlib.manifest import ZootrManifest, zootr_manifest_from_dir

from . import console as C
from . import progress, streams
from .httplib import handlers
from .oci import http as ocihttp
from .oci.core import blob, descriptor, manifest, reference
from .zootrlib import artifacts, seeddetails

_BASE_MEDIA_TYPE = "application/sudonters.zootr.seed"
_ANNOTATION_BASE = "etc.sudonters.zootr"


def _anno_key(s: str) -> str:
    return f"{_ANNOTATION_BASE}.{s}".lower()


def _media_type(s: str) -> str:
    return f"{_BASE_MEDIA_TYPE}.{s}".lower()


def opener_from_cli(_: argparse.Namespace) -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(handlers.DontThrowExceptions())


def main(args: argparse.Namespace) -> int:
    if not args.dir.exists():
        print(f"{args.dir} does not exist", file=sys.stderr)
        return 2

    if not args.dir.is_dir():
        print(f"{args.dir} is not a directory", file=sys.stderr)
        return 3

    if (ref := reference.parse(args.ref)) is None:
        print(f"{args.ref} is not a valid OCI reference")
        return 4

    zm = zootr_manifest_from_dir(args.dir)
    m = _oci_manifest_from_zootr(zm)

    opener = opener_from_cli(args)

    blobs = blob.PullPusher(
        ocihttp.BlobPuller(ref.registry, opener),
        ocihttp.BlobPusher(ref.registry, opener),
    )

    manifests = manifest.PullPusher(
        ocihttp.ManifestPuller(ref.registry, opener),
        ocihttp.ManifestPusher(ref.registry, opener),
    )

    s = streams.string_reader(
        json.dumps(zm.metadata, cls=seeddetails.SeedDetailsEncoder)
    )

    if not args.stfu:
        s = _track(streams.name("Metadata", s), m.config.bytes, sys.stdout)

    blobs.push_blob(
        ref.repository,
        m.config,
        s,
    )

    for (zf, b) in zip(zm.files, m.layers):
        s = zf.open()

        if not args.stfu:
            s = _track(streams.name(zf.kind.name, s), b.bytes, sys.stdout)

        blobs.push_blob(ref.repository, b, s)

    manifests.push_manifest(ref.repository, ref.tag, m)

    return 0


def _oci_manifest_from_zootr(zm: ZootrManifest) -> manifest.Manifest:
    layers = []
    config = descriptor.from_obj(
        zm.metadata, _media_type("config"), cls=seeddetails.SeedDetailsEncoder
    )
    annotations = {}

    for zf in zm.files:
        fh = zf.open()
        d = descriptor.from_stream(
            streams.name(zf.kind.name, T.cast(streams.SeekReader, fh)),
            _media_type(zf.kind.name),
        )
        d.annotations["org.opencontainers.image.title"] = zf.path.name
        layers.append(d)

    return manifest.Manifest(_media_type("generation"), config, layers, annotations)


def _track(s: streams.NamedReader, n: float, w: T.TextIO) -> progress.Reader:
    r = progress.Many(
        [
            progress.Static(f"{C.resetline()} "),
            progress.Spinner(
                [
                    f"{C.fg(70)}◌{C.reset()}",
                    f"{C.fg(76)}◎{C.reset()}",
                    f"{C.fg(82)}◍{C.reset()}",
                    f"{C.fg(156)}●{C.reset()}",
                    f"{C.fg(82)}◍{C.reset()}",
                    f"{C.fg(76)}◎{C.reset()}",
                ]
            ),
            progress.Static(f"{C.reset()} "),
            progress.Bar(filled=f"{C.fg(129)}={C.reset()}", unfilled=" ", total=n),
            progress.Static(" "),
            progress.Percentage(n),
            progress.Static(f" {s.name()}"),
        ]
    )

    r = progress.MinTick(r=r, total=n, min_tick=n * 0.032)
    r = progress.OnFinalTick(
        r=r,
        total=n,
        display=f"{C.resetline()} {C.fg(156)}●{C.reset()} {s.name()}" + "\n",
    )
    return progress.Reader(s, progress.Display(r, w))
