import argparse
from .guo import run as run_guo
from .bu import run as run_bu

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # guo
    parser_guo = subparsers.add_parser("guo")
    parser_guo.add_argument('-u', '--user', type=str)
    parser_guo.add_argument('-p', '--password', type=str)
    parser_guo.set_defaults(func=run_guo)

    # bu
    parser_guo = subparsers.add_parser("bu")
    parser_guo.add_argument('-u', '--user', type=str)
    parser_guo.add_argument('-p', '--password', type=str)
    parser_guo.set_defaults(func=run_bu)

    args = parser.parse_args()
    args.func(args)