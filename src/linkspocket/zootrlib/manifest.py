import contextlib
import pathlib
import typing as T
import dataclasses as dc
from .artifacts import ZootrFile, zootr_files_from_dir, FileKind
from .seeddetails import SeedDetails, seeddetails_from_stream


@dc.dataclass()
class ZootrManifest:
    metadata: SeedDetails = dc.field(init=False)
    files: T.List[ZootrFile] = dc.field(init=False, default_factory=list)


def zootr_manifest_from_dir(p: pathlib.Path) -> ZootrManifest:
    m = ZootrManifest()
    for zf in zootr_files_from_dir(p):
        m.files.append(zf)

        if zf.kind == FileKind.Settings:
            with contextlib.closing(zf.open()) as fh:
                m.metadata = seeddetails_from_stream(fh)

    return m
