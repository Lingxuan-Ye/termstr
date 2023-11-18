from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Iterable, Iterator, Self

from .const import ESCSEQ, Color


class AbstractBaseContainer(ABC):
    """
    Attributes:
        style (int):
            A single-byte integer representing text styles, where
            each bit represents:
                - Bit 7: Bold
                - Bit 6: Dim
                - Bit 5: Italic
                - Bit 4: Underline
                - Bit 3: Blink
                - Bit 2: Reverse
                - Bit 1: Invisible
                - Bit 0: Strikethrough

        foreground (Color | None):
            The foreground color of the text, or None for the default color.

        background (Color | None):
            The background color of the text, or None for the default color.

    For example, if `style` is set to `0b11000000`, it means that the
    bold and dim modes are turned on, while all other style attributes
    are turned off.
    """

    style: int
    foreground: Color | None
    background: Color | None

    data: Any
    padding: tuple[int, int]

    @abstractmethod
    def _len(self) -> int:
        """Length with no padding."""
        pass

    def __len__(self) -> int:
        return self._len() + self.padding[0] + self.padding[1]

    def len(self) -> int:
        return self.__len__()

    def center(self, width: int) -> Self:
        diff = width - self._len()
        if diff > 0:
            front = diff // 2
            back = diff - front
            self.padding = (front, back)
        return self

    def ljust(self, width: int) -> Self:
        diff = width - self._len()
        if diff > 0:
            self.padding = (0, diff)
        return self

    def rjust(self, width: int) -> Self:
        diff = width - self._len()
        if diff > 0:
            self.padding = (diff, 0)
        return self

    def _style(self, text: str) -> str:
        result = deque(text)

        is_bold = False
        if (self.style >> 7) & 1:
            result.appendleft(ESCSEQ["style"]["bold"])
            result.append(ESCSEQ["reset"]["bold/dim"])
            is_bold = True

        if (self.style >> 6) & 1:
            result.appendleft(ESCSEQ["style"]["dim"])
            if not is_bold:
                result.append(ESCSEQ["reset"]["bold/dim"])

        if (self.style >> 5) & 1:
            result.appendleft(ESCSEQ["style"]["italic"])
            result.append(ESCSEQ["reset"]["italic"])

        if (self.style >> 4) & 1:
            result.appendleft(ESCSEQ["style"]["underline"])
            result.append(ESCSEQ["reset"]["underline"])

        if (self.style >> 3) & 1:
            result.appendleft(ESCSEQ["style"]["blink"])
            result.append(ESCSEQ["reset"]["blink"])

        if (self.style >> 2) & 1:
            result.appendleft(ESCSEQ["style"]["reverse"])
            result.append(ESCSEQ["reset"]["reverse"])

        if (self.style >> 1) & 1:
            result.appendleft(ESCSEQ["style"]["invisible"])
            result.append(ESCSEQ["reset"]["invisible"])

        if self.style & 1:
            result.appendleft(ESCSEQ["style"]["strikethrough"])
            result.append(ESCSEQ["reset"]["strikethrough"])

        result.appendleft(" " * self.padding[0])
        result.append(" " * self.padding[1])

        return "".join(result)

    @abstractmethod
    def __str__(self) -> str:
        pass

    def set_bold(self) -> Self:
        self.style |= 0b10000000
        return self

    def unset_bold(self) -> Self:
        self.style &= 0b01111111
        return self

    def set_dim(self) -> Self:
        self.style |= 0b01000000
        return self

    def unset_dim(self) -> Self:
        self.style &= 0b10111111
        return self

    def set_italic(self) -> Self:
        self.style |= 0b00100000
        return self

    def unset_italic(self) -> Self:
        self.style &= 0b11011111
        return self

    def set_underline(self) -> Self:
        self.style |= 0b00010000
        return self

    def unset_underline(self) -> Self:
        self.style &= 0b11101111
        return self

    def set_blink(self) -> Self:
        self.style |= 0b00001000
        return self

    def unset_blink(self) -> Self:
        self.style &= 0b11110111
        return self

    def set_reverse(self) -> Self:
        self.style |= 0b00000100
        return self

    def unset_reverse(self) -> Self:
        self.style &= 0b11111011
        return self

    def set_invisible(self) -> Self:
        self.style |= 0b00000010
        return self

    def unset_invisible(self) -> Self:
        self.style &= 0b11111101
        return self

    def set_strikethrough(self) -> Self:
        self.style |= 0b00000001
        return self

    def unset_strikethrough(self) -> Self:
        self.style &= 0b11111110
        return self

    def set_foreground(self, color: Color) -> Self:
        self.foreground = color
        return self

    def unset_foreground(self) -> Self:
        self.foreground = None
        return self

    def set_background(self, color: Color) -> Self:
        self.background = color
        return self

    def unset_background(self) -> Self:
        self.background = None
        return self


class Span(AbstractBaseContainer):
    style: int
    foreground: Color | None
    background: Color | None

    data: str
    padding: tuple[int, int]

    def __init__(
        self,
        seq: Any,
        style: int = 0b00000000,
        foreground: Color | None = None,
        background: Color | None = None,
    ) -> None:
        if isinstance(seq, self.__class__):
            self.data = seq.data
            self.style = style if style != 0b00000000 else seq.style
            self.foreground = foreground if foreground is not None else seq.foreground
            self.background = background if background is not None else seq.background
            return
        if not isinstance(seq, str):
            seq = str(seq)
        self.data = seq
        self.style = style
        self.foreground = foreground
        self.background = background

    def _len(self) -> int:
        return len(self.data)

    def __str__(self) -> str:
        return self._style(self.data)

    def __add__(self, other: Any) -> "Div":
        div = Div()
        div.append(self)
        if isinstance(other, self.__class__):
            div.append(other)
        elif isinstance(other, Div):
            div.append(self.__class__(" " * other.padding[0]))
            div.extend(other)
            div.style = other.style
            div.foreground = other.foreground
            div.background = other.background
            div.padding = (0, other.padding[1])
        else:
            div.append(Span(other))
        return div

    def __radd__(self, other: Any) -> "Div":
        div = Div()
        div.append(self)
        if isinstance(other, self.__class__):
            div.appendleft(other)
        elif isinstance(other, Div):
            div.appendleft(self.__class__(" " * other.padding[1]))
            data = other.data.copy()
            data.reverse()
            for item in data:
                div.appendleft(item)
            div.style = other.style
            div.foreground = other.foreground
            div.background = other.background
            div.padding = (other.padding[0], 0)
        else:
            div.appendleft(Span(other))
        return div

    def __mul__(self, n: int) -> "Div":
        div = Div()
        for _ in range(n):
            div.append(self.__class__(self))
        return div


class Div(AbstractBaseContainer):
    style: int
    foreground: Color | None
    background: Color | None

    data: deque[Span]
    padding: tuple[int, int]

    def __init__(
        self,
        style: int = 0b00000000,
        foreground: Color | None = None,
        background: Color | None = None,
    ) -> None:
        self.data = deque()
        self.style = style
        self.foreground = foreground
        self.background = background

    def _len(self) -> int:
        length = 0
        for i in self.data:
            length += i.len()
        return length

    def __str__(self) -> str:
        text = "".join(str(i) for i in self.data)
        return self._style(text)

    def __iter__(self) -> Iterator[Span]:
        return (span for span in self.data)

    def append(self, item: Span) -> Self:
        self.data.append(item)
        return self

    def appendleft(self, item: Span) -> Self:
        self.data.appendleft(item)
        return self

    def insert(self, index, item: Span) -> Self:
        self.data.insert(index, item)
        return self

    def extend(self, other: Self | Iterable[Span]) -> Self:
        if isinstance(other, self.__class__):
            self.data.append(Span(" " * other.padding[0]))
            self.data.extend(other.data)
            self.data.append(Span(" " * other.padding[1]))
            return self
        self.data.extend(other)
        return self

    def copy(self) -> Self:
        copy = self.__class__(self.style, self.foreground, self.background)
        copy.data.extend(self.data.copy())
        return copy

    def pop(self) -> Span:
        return self.data.pop()

    def popleft(self) -> Span:
        return self.data.popleft()

    def remove(self, item) -> Self:
        self.data.remove(item)
        return self
