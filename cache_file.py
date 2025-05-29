import platform
import os
import logging
import time
logger = logging.getLogger(__name__)

cache_dir_name = "pubchemgetter"
lock_retry_interval = 1.0 # 1 second

match platform.system():
    case "Linux" | "Windows":
        cache_dir = os.path.expanduser(os.path.join("~", ".local", "share", f"{cache_dir_name}"))
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
        self._lock = None

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
        os.remove(self._path)


class CacheFile:
    def __init__(self, name: str, opts: str = 'r'):
        file_path = os.path.join(cache_dir, name)
        self._lock = LockFile(file_path)
        self._file = open(file_path, opts)

    def __enter__(self):
        self._lock.__enter__()
        return self._file
    def __exit__(self, type, value, traceback):
        self._file.close()
        self._lock.__exit__(type, value, traceback)

    def close(self):
        self._file.close()

    # TODO: Implement
