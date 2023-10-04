import argparse
import pathlib


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser("linkspocket")
    cli.add_argument(
        "-d",
        "--seed-dir",
        help="Path to directory containing zootr artifacts",
        required=True,
        type=pathlib.Path,
        dest="dir",
    )
    cli.add_argument(
        "-R",
        "--ref",
        dest="ref",
        required=True,
    )
    cli.add_argument(
        "-Q",
        "--stfu",
        help="For real, shut the fuck up",
        default=False,
        dest="stfu",
        action="store_true",
    )
    return cli
