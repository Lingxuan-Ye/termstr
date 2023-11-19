import sys

from .const import ESCSEQ, Color
from .models import Span


def cprint(
    label: str,
    message: str,
    *,
    label_color: Color,
    label_width: int = 8,
    to_stderr: bool = False,
) -> None:
    clabel = Span(label).set_bold().set_foreground(label_color).rjust(label_width)
    if to_stderr:
        return print(clabel, message, file=sys.stderr)
    print(clabel, message, file=sys.stdout)


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
