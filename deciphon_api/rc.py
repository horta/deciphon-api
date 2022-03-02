from enum import Enum, IntEnum

from pydantic import BaseModel

__all__ = ["RC"]


class RC(IntEnum):
    OK = 0
    END = 1
    NOTFOUND = 2
    EFAIL = 3
    EIO = 4
    EINVAL = 5
    ENOMEM = 6
    EPARSE = 7


class StrRC(str, Enum):
    OK = "ok"
    END = "end"
    NOTFOUND = "notfound"
    EFAIL = "efail"
    EIO = "eio"
    EINVAL = "einval"
    ENOMEM = "enomem"
    EPARSE = "eparse"
