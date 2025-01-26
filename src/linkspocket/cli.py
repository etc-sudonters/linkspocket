import dataclasses as dc
import argparse
import pathlib
import typing as T

from . import progress, streams, console as C
from .oci.core import reference
from .oci.core.registry import Registry


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser("linkspocket")
    cli.add_argument(
        "-R",
        "--ref",
        help="OCI reference, e.g myregistry.tld: 5000/namespace",
        dest="ref",
        required=True,
    )

    cli.add_argument(
        "--http", help="Use plaintext HTTP instead of HTTPS to converse with registry", dest="proto", default="https")

    cli.add_argument(
        "-Q",
        "--stfu",
        help="Don't output to console",
        default=False,
        dest="quiet",
        action="store_true",
    )

    commands = cli.add_subparsers()
    _pushparser(commands)
    _pullparser(commands)
    return cli


class _addcommand(T.Protocol):
    def add_parser(self, name, **kwargs) -> argparse.ArgumentParser:
        ...


def _pushparser(parent: _addcommand):
    description = "Push a generated seed to the registry"
    cmd = parent.add_parser("push", help=description, description=description)
    cmd.add_argument(
        "-d",
        "--seed-dir",
        help="Path to directory containing zootr artifacts",
        required=True,
        type=pathlib.Path,
        dest="src",
    )

    cmd.add_argument(
        "-A",
        "--autotag",
        help="Automatically generate tag from seed hash, cedes to explicit tag in --ref",
        default=False,
        dest="autotag",
        action="store_true",
    )


def _pullparser(parent: _addcommand):
    description = "Pull a generated seed from the registry"
    cmd = parent.add_parser("pull", help=description, description=description)
    cmd.add_argument(
        "-o",
        "--output",
        help="Output directory",
        required=True,
        type=pathlib.Path,
        dest="out",
    )
    cmd.add_argument(
        "-C",
        "--clean",
        help="Ensure output directory is empty before pulling",
        action="store_true",
        default=False,
        dest="clean",
    )


class HasReference(T.Protocol):
    ref: reference.Reference


@dc.dataclass()
class basectx():
    ref: reference.Reference
    quiet: bool
    registry: Registry
    std: C.Std

    def track(self, s: streams.NamedReader, n: float) -> streams.Reader:
        if not self.quiet:
            return progress.track(s, n, self.std.out)
        return s


@dc.dataclass()
class PushCtx(basectx):
    src: pathlib.Path
    autotag: bool


@dc.dataclass()
class PullCtx(basectx):
    out: pathlib.Path
    clean: bool
