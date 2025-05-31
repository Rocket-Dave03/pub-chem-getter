import platform
import os
import logging
import time
import json
import zlib
import pubchempy
from typing import BinaryIO, List, Literal, TextIO
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


class Cache:
    def __init__(self) -> None:
        self._records: List[dict] = []

    def add_record(self, record: dict) -> bool:
        cids = [record["id"]["id"]["cid"] for record in self._records]
        id = record["id"]["id"]["cid"]
        if not id in cids:
            self._records.append(record)
            return True
        else:
            logger.info(f"Record for cid {id} alreay exists, skipping.")
            return False
    
    def get_as_compound(self, idx: int):
        return pubchempy.Compound(self._records[idx])

    @property
    def records(self):
        return self._records

    @classmethod
    def from_json(cls, input_json: str):
        records = json.loads(input_json)
        new_instance = cls()
        new_instance._records = records
        return new_instance

        

class CacheFile:
    file_header = b"ZLib Compressed JSON\n"
    def __init__(self, name: str):
        self._file_path = os.path.join(cache_dir, name)
        self._file: BinaryIO | None = None
        self._lock = LockFile(self._file_path)

    def __enter__(self):
        self._lock.__enter__()
        self._file = open(self._file_path, 'r+b') # type: ignore
        return self

    def __exit__(self, type, value, traceback):
        self.close(type, value, traceback)

    def read(self) -> Cache:
        if self._file is None:
            logger.warning(f"Attempted to read config file {self._file_path}, but it hasnt been opened.")
            raise RuntimeError("Can't read unopened file")

        file_content = self._file.read()
        if len(file_content) == 0:
            logger.warning("Cache file empty but exists")
            return Cache()
        data = zlib.decompress(file_content[len(self.file_header):])

        c = Cache.from_json(data.decode("utf-8"))
        return c 

    def write(self, c: Cache):
        if self._file is None:
            logger.warning(f"Attempted to write config file {self._file_path}, but it hasnt been opened.")
            return

        logger.info(f"Writing {len(c.records)} records to {self._file_path}") 
        data = json.dumps(c.records)
        self._file.seek(0)
        self._file.truncate(0)
        self._file.write(self.file_header)
        self._file.write(zlib.compress(data.encode("utf-8")))
        

    def close(self, type = None, value = None, traceback = None):
        if not self._file is None:
            self._file.close()
        self._lock.__exit__(type, value, traceback)

    # TODO: Implement
