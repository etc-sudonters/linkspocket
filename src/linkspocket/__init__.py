import argparse
import dataclasses as dc
import typing as T
import urllib.request

from .errors import *
from . import console as C, cli, commands
from .httplib import handlers
from .oci import http as ocihttp
from .oci.core import blob, manifest, reference
from .oci.core.registry import Registry


def main(args: argparse.Namespace) -> int:
    std = C.newstd()
    try:
        cmd = createargs(args, std)

        if isinstance(cmd, cli.PullCtx):
            return commands.pull(cmd)
        elif isinstance(cmd, cli.PushCtx):
            return commands.push(cmd)

        return 1
    except PocketError as e:
        std.err.write(str(e))
        return 2


class BadReference(PocketError):
    def __init__(self, ref: reference.Reference):
        super().__init__(f"Invalid reference: {ref}")


class UnknownCommand(PocketError):
    def __init__(self):
        super().__init__("Subcommand must be 'pull' or 'push'")


def registry(registry: str, proto: str) -> Registry:
    opener = urllib.request.build_opener(handlers.DontThrowExceptions())
    blobs = blob.PullPusher(
        ocihttp.BlobPuller(registry, opener, proto),
        ocihttp.BlobPusher(registry, opener, proto),
    )

    manifests = manifest.PullPusher(
        ocihttp.ManifestPuller(registry, opener, proto),
        ocihttp.ManifestPusher(registry, opener, proto),
    )

    return Registry(manifests, blobs)


Args = T.Union[cli.PullCtx, cli.PushCtx]


def createargs(args: argparse.Namespace, std: C.Std) -> Args | None:
    if (ref := reference.parse(args.ref)) is None:
        raise BadReference(args.ref)

    proto = "https" if not args.insecure_http else "http"

    if hasattr(args, "src"):
        return cli.PushCtx(
            ref=ref,
            quiet=args.quiet,
            registry=registry(ref.registry, proto),
            std=std,
            src=args.src,
            autotag=args.autotag,
        )
    elif hasattr(args, "out"):
        return cli.PullCtx(
            ref=ref,
            quiet=args.quiet,
            registry=registry(ref.registry, proto),
            std=std,
            out=args.out,
            clean=args.clean,
        )
    return None
