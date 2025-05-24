import platform
import os
import logging
logger = logging.getLogger(__name__)

import filelock 

cache_dir_name = "pubchemgetter"

match platform.system():
    case "Linux" | "Windows":
        cache_dir = os.path.expanduser(os.path.join("~", ".local", "share", f"{cache_dir_name}"))
    case system:
        raise Exception(f"Unsupported platform {system}")

logger.info(f"Using {cache_dir=}")

class CacheFile:
    def __init__(self):
        cache_file_name = "compound_cache.json"
        self._lock = filelock.FileLock(os.path.join(cache_dir, f"{cache_file_name}.lock"))
        self._file = open(os.path.join(cache_dir, cache_file_name), 'w')

    def __enter__(self):
        return self._file
    def __exit__(self, type, value, traceback):
        self._file.close()

