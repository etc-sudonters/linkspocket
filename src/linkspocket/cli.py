import argparse
import pathlib

def args() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser("linkspocket")
    cli.add_argument(
        "-r",
        "--rom",
        help="Path to rom, may be relative or absolute path",
        required=True,
        type=pathlib.Path,
        dest="rom",
    )
    cli.add_argument("-t", "--tag", help="Optional name for generated seed", dest="tag")
    cli.add_argument(
        "-R",
        "--registry",
        help="URI of repository to push artifacts to, should not include a protocol",
        default="127.0.0.1:5000",
    )
    return cli

