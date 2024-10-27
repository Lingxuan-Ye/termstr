import sys

from .const import ESCSEQ, Color
from .models import Span


def labeled_print(
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


def error(message: str) -> None:
    labeled_print("error", message, label_color=Color.RED, to_stderr=True)


def warn(message: str) -> None:
    labeled_print("warning", message, label_color=Color.YELLOW, to_stderr=True)


def success(message: str) -> None:
    labeled_print("success", message, label_color=Color.GREEN)


def erase_screen() -> None:
    print(ESCSEQ["erase"]["screen"], end="")


def reset_cursor() -> None:
    print(ESCSEQ["reset"]["cursor"], end="")
