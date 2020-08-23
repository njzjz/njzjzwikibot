import argparse
from .guo import run as run_guo

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_guo = subparsers.add_parser("guo")
    parser_guo.add_argument('-u', '--user', type=str)
    parser_guo.add_argument('-p', '--password', type=str)
    parser_guo.set_defaults(func=run_guo)

    args = parser.parse_args()
    args.func(args)