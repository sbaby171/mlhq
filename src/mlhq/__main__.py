# Allows: python -m mlhq [--version]
from .core import get_version
import argparse
# src/mlhq/__main__.py
from . import __version__
from .client import Client


# ============================================================================:
def __handle_cli_args():
    parser = argparse.ArgumentParser(prog="mlhq", description="MLHQ sample CLI")
    parser.add_argument("--version", action="store_true", help="print version and exit")
    args = parser.parse_args()
    return args 
# ============================================================================:
def main(args):
    if args.version:
        print(f"mlhq {__version__}")

    print(f"DEBUG: Test-Client: {Client().ping()}")
# ============================================================================:
if __name__ == "__main__":
    args = __handle_cli_args()
    main(args)
