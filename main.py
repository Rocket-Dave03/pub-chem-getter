#!/usr/bin/env python3

import os
import logging
import time
logger = logging.getLogger(__name__)
if __name__ == "__main__":
    log_level = logging.getLevelNamesMapping()[os.environ["LOG_LEVEL"]] if "LOG_LEVEL" in os.environ else logging.WARN
    logging.basicConfig(level=log_level)

import argparse
import sys
from typing import Any
import pubchempy
import json

from cache_file import CacheFile
from cache_file import Cache

# request
def get(args):
    logger.info(f"get({args})")
    def fil(kv: tuple[str, Any]) -> bool:
        return kv[1] != None

    logger.debug(next(filter(fil, vars(args).items())))
    # raise NotImplementedError

# query compound cache
def query(args):
    logger.info(f"get({args})")
    def fil(kv: tuple[str, Any]) -> bool:
        return kv[1] != None

    id = next(filter(fil, vars(args).items()))
    logger.debug(id)

    with CacheFile("compound_cache.json") as cache:
        try:
            if id[0] == "name":
                comp = pubchempy.get_compounds(id[1],namespace="name")[0]
            elif id[0] == "cid":
                comp = pubchempy.get_compounds(id[1],namespace="cid")[0]
            else:
                raise ValueError(f"args[0] was {args[0]} must be on of ['name', 'cid']")
        except IndexError as e:
            logger.error(f"Failed to get compound from api: {e}")
            return

        c = cache.read() 
        c.add_record(comp.record) # type: ignore
        cache.write(c)

def list(args):
    with CacheFile("compound_cache.json") as cache:
        for record in cache.read().records:
            compound = pubchempy.Compound(record)
            print(f"Compound '{compound.iupac_name}', cid: {compound.cid}")

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commnads")

    list_parser = subparsers.add_parser("list", help="List the contents of the compound cache")
    list_parser.set_defaults(func=list)

    get_parser = subparsers.add_parser("get", help="Request a compound from the api")
    get_parser.set_defaults(func=get)
    get_group = get_parser.add_mutually_exclusive_group(required=True)
    get_group.add_argument("-c", "--cid",  type=int, help="Get compound by cid")
    get_group.add_argument("-n", "--name", type=str, help="Get compound by name")

    query_parser = subparsers.add_parser("query", help="Get cached compound info")
    query_parser.set_defaults(func=query)
    query_group = query_parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("-c", "--cid",  type=int, help="Get compound by cid")
    query_group.add_argument("-n", "--name", type=str, help="Get compound by name")
    query_parser.add_argument("-r","--request", help="Request from api if not in cache")

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    if getattr(args, "func", None):
        args.func(args)
    

if __name__ == "__main__":
    main()
