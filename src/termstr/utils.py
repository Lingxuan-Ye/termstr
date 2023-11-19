from .const import ESCSEQ
from .models import Span


def erase_screen() -> None:
    print(ESCSEQ["erase"]["screen"], end="")


def reset_cursor() -> None:
    print(ESCSEQ["reset"]["cursor"], end="")


def tstr(seq: str) -> Span:
    """
    `seq` should not contain any ANSI escape sequence,
    otherwise it may not function as expected.
    """
    return Span(seq)
