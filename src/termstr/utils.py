from .const import ESCSEQ


def erase_screen() -> None:
    print(ESCSEQ["erase"]["screen"], end="")


def reset_cursor() -> None:
    print(ESCSEQ["reset"]["cursor"], end="")
