import platform
import os
import logging
import time
from typing import TextIO
logger = logging.getLogger(__name__)

cache_dir_name = "pubchemgetter"
lock_retry_interval = 1.0 # 1 second

match platform.system():
    case "Linux":
        cache_dir = os.path.expanduser(os.path.join("~", ".local", "share", f"{cache_dir_name}"))
    case "Windows":
        cache_dir = os.path.expanduser(os.path.join("~","AppData","Local", f"{cache_dir_name}"))
    case system:
        raise Exception(f"Unsupported platform {system}")

logger.info(f"Using {cache_dir=}")

try:
    os.mkdir(cache_dir)
except FileExistsError:
    pass

class LockFile:
    def __init__(self, path: str) -> None:
        self._path = path+'.lock'
        self._lock: None | TextIO = None

    def __enter__(self):
        logger.debug(f"Attempting to create lockfile {self._path}")
        def try_lock():
            try:
                self._lock = open(self._path, 'x')
                return True
            except FileExistsError:
                return False
        while not try_lock():
            logger.debug(f"Lock {self._path} alreay held, retrying")
            time.sleep(lock_retry_interval)
        logger.debug(f"Aquired lock {self._path}")
        return self._lock

    def __exit__(self, type, value, traceback):
        logger.debug(f"Removing lockfile {self._path}")
        if not self._lock is None:
            self._lock.close()
        os.remove(self._path)


class CacheFile:
    def __init__(self, name: str, opts: str = 'r'):
        self._file_path = os.path.join(cache_dir, name)
        self._opts = opts
        self._lock = LockFile(self._file_path)

    def __enter__(self):
        self._lock.__enter__()
        self._file = open(self._file_path, self._opts)
        return self._file

    def __exit__(self, type, value, traceback):
        self.close(type, value, traceback)

    def close(self, type = None, value = None, traceback = None):
        self._file.close()
        self._lock.__exit__(type, value, traceback)

    # TODO: Implement
