import argparse
import pathlib


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser("linkspocket")
    cli.add_argument("-t", "--tag", help="name for generated seed", dest="tag", required=True)
    cli.add_argument(
        "-R",
        "--registry",
        help="URI of repository to push artifacts to, should not include a protocol",
        default="127.0.0.1:5000",
        dest="registry",
    )
    cli.add_argument(
        "--repository",
        help="Name of OCI repository to push to",
        default="zootr",
        dest="repository",
    )
    cli.add_argument(
        "-d",
        "--seed-dir",
        help="Path to directory containing zootr artifacts",
        required=True,
        type=pathlib.Path,
        dest="dir",
    )
    return cli
