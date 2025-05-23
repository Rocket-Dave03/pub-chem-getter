#!/usr/bin/env python3

import argparse
import os
from typing import Any
import logging
logger = logging.getLogger(__name__)

def get(args):
    logger.info(f"get({args})")
    def fil(kv: tuple[str, Any]) -> bool:
        return kv[1] != None

    logger.debug(next(filter(fil, vars(args).items())))

def query(args):
    logger.info(f"get({args})")
    def fil(kv: tuple[str, Any]) -> bool:
        return kv[1] != None

    id = next(filter(fil, vars(args).items()))
    logger.debug(id)

    raise NotImplementedError

def list(args):
    print(f"list({args})")

    raise NotImplementedError

def main():
    log_level = logging.getLevelNamesMapping()[os.environ["LOG_LEVEL"]] if "LOG_LEVEL" in os.environ else logging.WARN
    logging.basicConfig(level=log_level)
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commnads")

    list_parser = subparsers.add_parser("list", help="List the contents of the compound cache")
    list_parser.set_defaults(func=list)

    get_parser = subparsers.add_parser("get", help="Request a compound from the api")
    get_parser.set_defaults(func=get)
    get_group = get_parser.add_mutually_exclusive_group()
    get_group.add_argument("-c", "--cid",  type=int, help="Get compound by cid")
    get_group.add_argument("-n", "--name", type=str, help="Get compound by name")

    query_parser = subparsers.add_parser("query", help="Get cached compound info")
    query_parser.set_defaults(func=query)
    query_group = query_parser.add_mutually_exclusive_group()
    query_group.add_argument("-c", "--cid",  type=int, help="Get compound by cid")
    query_group.add_argument("-n", "--name", type=str, help="Get compound by name")

    args = parser.parse_args()
    if getattr(args, "func", None):
        args.func(args)
    

if __name__ == "__main__":
    main()
