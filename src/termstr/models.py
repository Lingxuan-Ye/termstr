import copy
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

    _data: Any
    _padding: tuple[int, int]
    style: int
    foreground: Color | None
    background: Color | None

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

    @abstractmethod
    def _data_len(self) -> int:
        """Length with no padding."""
        pass

    def __len__(self) -> int:
        return self._data_len() + self._padding[0] + self._padding[1]

    def len(self) -> int:
        return self.__len__()

    def center(self, width: int) -> Self:
        diff = width - self._data_len()
        if diff > 0:
            front = diff // 2
            back = diff - front
            self._padding = (front, back)
        return self

    def ljust(self, width: int) -> Self:
        diff = width - self._data_len()
        if diff > 0:
            self._padding = (0, diff)
        return self

    def rjust(self, width: int) -> Self:
        diff = width - self._data_len()
        if diff > 0:
            self._padding = (diff, 0)
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

        result.appendleft(" " * self._padding[0])
        result.append(" " * self._padding[1])

        return "".join(result)

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def clone(self) -> Self:
        pass


class Span(AbstractBaseContainer):
    _data: str
    _padding: tuple[int, int]
    style: int
    foreground: Color | None
    background: Color | None

    def __init__(
        self,
        seq: Any,
        style: int = 0b00000000,
        foreground: Color | None = None,
        background: Color | None = None,
    ) -> None:
        """
        If `seq` is a str, it should not contain any ANSI escape sequence,
        otherwise it may not function as expected.
        """
        if isinstance(seq, self.__class__):
            self._data = seq._data
            self._padding = seq._padding
            self.style = style if style != 0b00000000 else seq.style
            self.foreground = foreground if foreground is not None else seq.foreground
            self.background = background if background is not None else seq.background
            return
        if isinstance(seq, Div):
            raise ValueError("cannot convert a `Div` instance to `Span`")
        if not isinstance(seq, str):
            seq = str(seq)
        self._data = seq
        self._padding = (0, 0)
        self.style = style
        self.foreground = foreground
        self.background = background

    def _data_len(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return self._style(self._data)

    def clone(self) -> Self:
        return copy.copy(self)

    def __add__(self, other: Any) -> "Div":
        """
        `Other` can be anything but a `Div` instance.
        Please refer to `Div.__radd__` for adding a `Div` instance.

        If `other` is an instance (actually a reference) of `Self`,
        return will hold a reference to the `other` object.
        For safety concern, `other` should no longer be used.
        """
        div = Div()
        div.append(self)
        if isinstance(other, self.__class__):
            div.append(other)
            return div
        div.append(self.__class__(other))
        return div

    def __radd__(self, other: Any) -> "Div":
        """
        `Other` can be anything but a `Span` or `Div` instance.
        Please refer to `Div.__add__` for reverse adding a `Div` instance.
        """
        div = Div()
        div.append(self.__class__(other))
        div.append(self)
        return div

    def __mul__(self, n: int) -> "Div":
        div = Div()
        for _ in range(n):
            div.append(self.clone())
        return div


class Div(AbstractBaseContainer):
    """
    Container of `Span` instances.

    Any change made will reset the attribute `_padding`,
    therefore `center`, `ljust`, 'rjust' should always
    be the last method(s) to be called, if needed.
    """

    _data: deque[Span]
    _padding: tuple[int, int]
    style: int
    foreground: Color | None
    background: Color | None

    def __init__(
        self,
        style: int = 0b00000000,
        foreground: Color | None = None,
        background: Color | None = None,
    ) -> None:
        self._data = deque()
        self.style = style
        self.foreground = foreground
        self.background = background

    def _data_len(self) -> int:
        length = 0
        for i in self._data:
            length += i.len()
        return length

    def __str__(self) -> str:
        text = "".join(str(i) for i in self._data)
        return self._style(text)

    def __iter__(self) -> Iterator[Span]:
        return (span for span in self._data)

    def clone(self) -> Self:
        return copy.deepcopy(self)

    def append(self, item: Span) -> Self:
        """
        `self`  will hold a reference to the `item` object.
        For safety concern, `item` should no longer be used.
        """
        self._padding = (0, 0)
        self._data.append(item)
        return self

    def appendleft(self, item: Span) -> Self:
        """
        `self`  will hold a reference to the `item` object.
        For safety concern, `item` should no longer be used.
        """
        self._padding = (0, 0)
        self._data.appendleft(item)
        return self

    def insert(self, index, item: Span) -> Self:
        self._padding = (0, 0)
        self._data.insert(index, item)
        return self

    def extend(self, other: Self | Iterable[Span]) -> Self:
        """
        `self`  will hold references to all `Span` instances in `other`.
        For safety concern, `other` should no longer be used.
        """
        self._padding = (0, 0)
        if isinstance(other, self.__class__):
            self._data.append(Span(" " * other._padding[0]))
            self._data.extend(other._data)
            self._data.append(Span(" " * other._padding[1]))
            return self
        self._data.extend(other)
        return self

    def pop(self) -> Span:
        self._padding = (0, 0)
        return self._data.pop()

    def popleft(self) -> Span:
        self._padding = (0, 0)
        return self._data.popleft()

    def remove(self, item) -> Self:
        self._padding = (0, 0)
        self._data.remove(item)
        return self

    def __add__(self, other: Any) -> Self:
        """
        For safety concern, `other` should no longer be used.
        """
        if isinstance(other, self.__class__):
            self.extend(other)
            return self
        self._padding = (0, 0)
        if isinstance(other, Span):
            self.append(other)
            return self
        self.append(Span(other))
        return self

    def __radd__(self, other: Any) -> Self:
        """
        For safety concern, `other` should no longer be used.
        """
        self._padding = (0, 0)
        if isinstance(other, Span):
            self.appendleft(other)
            return self
        self.appendleft(Span(other))
        return self
