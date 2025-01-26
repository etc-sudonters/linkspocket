import contextlib
import json
import pathlib
import shutil
import typing as T

from linkspocket.oci.core.reference import Reference
from linkspocket.zootrlib.manifest import ZootrManifest, zootr_manifest_from_dir

from . import streams, cli, media, oci
from .oci.core import descriptor, manifest
from .zootrlib import seeddetails
from .errors import PocketError


class UnknownManifest(PocketError):
    def __init__(self, ref: Reference):
        super().__init__(f"Could not find manifest for {ref}")


def pull(ctx: cli.PullCtx) -> int:
    tag = ctx.ref.tag
    if not tag:
        if ctx.ref.digest:
            tag = ctx.ref.digest
        else:
            print(f"{ctx.ref} does not have a tag or a digest attached",
                  file=ctx.std.err)
            return 4

    seeddir = ctx.out.joinpath(tag)
    if ctx.clean:
        shutil.rmtree(seeddir, ignore_errors=True)
    seeddir.mkdir(parents=True)

    ref, manifests, blobs = ctx.ref, ctx.registry.manifests, ctx.registry.blobs
    if (manifest := manifests.pull_manifest(ctx.ref.repository, tag)) is None:
        raise UnknownManifest(ctx.ref)

    _download_layer(ctx,  manifest.config,  blobs.pull_blob(
        ref.repository, manifest.config.digest), seeddir.joinpath(".seeddetails"))

    for layer in manifest.layers:
        if (filename := layer.annotations.get(oci.FILENAME_ANNOTATION, None)) is None:
            ctx.std.err.write(
                f"{layer} does not have filename attached, skipping\n")
            continue

        _download_layer(ctx, layer, blobs.pull_blob(
            ref.repository, layer.digest), seeddir.joinpath(filename))

    return 0


def _download_layer(ctx: cli.PullCtx, descriptor: descriptor.Descriptor,  layer: streams.MustCloseReader, dest: pathlib.Path):
    with contextlib.closing(layer) as lh, dest.open(mode='wb') as fh:
        tracked = ctx.track(streams.name(str(dest.name), lh), descriptor.bytes)
        shutil.copyfileobj(tracked, fh)


def push(args: cli.PushCtx) -> int:
    if not args.src.exists():
        print(f"{args.src} does not exist", file=args.std.err)
        return 2

    if not args.src.is_dir():
        print(f"{args.src} is not a directory", file=args.std.err)
        return 3

    zm = zootr_manifest_from_dir(args.src)

    tag = args.ref.tag

    if tag is None:
        if args.autotag:
            tag = "-".join(zm.metadata.hash).replace(" ", "-").lower()
        else:
            print("No tag provided and autotag is not enabled", file=args.std.err)
            return 4

    args.ref.tag = tag

    if not args.quiet:
        print(f"Pushing {args.ref}", file=args.std.out)

    m = _oci_manifest_from_zootr(zm)

    s = streams.StringReader(json.dumps(
        zm.metadata, cls=seeddetails.SeedDetailsEncoder))

    s = args.track(streams.name("Metadata", s), m.config.bytes)

    blobs, manifests = args.registry.blobs, args.registry.manifests

    blobs.push_blob(
        args.ref.repository,
        m.config,
        s,
    )

    for (zf, b) in zip(zm.files, m.layers):
        s = args.track(streams.name(zf.kind.name, zf.open()), b.bytes)
        blobs.push_blob(args.ref.repository, b, s)

    manifests.push_manifest(args.ref.repository, tag, m)
    return 0


def _oci_manifest_from_zootr(zm: ZootrManifest) -> manifest.Manifest:
    layers = []
    config = descriptor.from_obj(
        zm.metadata, media.type("config"), cls=seeddetails.SeedDetailsEncoder
    )
    annotations = {}

    for zf in zm.files:
        fh = zf.open()
        d = descriptor.from_stream(
            streams.name(zf.kind.name, T.cast(streams.Reader, fh)),
            media.type(zf.kind.name),
        )
        d.annotations[oci.FILENAME_ANNOTATION] = zf.path.name
        layers.append(d)

    return manifest.Manifest(media.type("generation"), config, layers, annotations)
