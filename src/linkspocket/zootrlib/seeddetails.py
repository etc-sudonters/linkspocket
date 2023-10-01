import dataclasses as dc
import io
import json
import typing as T


@dc.dataclass()
class SeedDetails:
    version: str
    hash: T.List[str]
    seed: str
    settings: str
    spoiler: bool

class Encoder(json.JSONEncoder):
    def default(self, o: T.Any) -> T.Any:
        if isinstance(o, SeedDetails):
            return {
                    "version": o.version,
                    "hash": o.hash,
                    "seed": o.seed,
                    "settings": o.settings,
                    "spoiler": o.spoiler,
                    }

        return super().default(o)


def from_stream(s: io.BufferedIOBase) -> SeedDetails:
    return from_dict(json.load(s))


def from_dict(settings: T.Dict[str, T.Any]) -> SeedDetails:
    return SeedDetails(
        version=settings[":version"],
        hash=settings["file_hash"],
        seed=settings[":seed"],
        settings=settings[":settings_string"],
        spoiler=settings[":enable_distribution_file"],
    )