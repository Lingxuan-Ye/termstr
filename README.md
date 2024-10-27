# termstr

[![PyPI - Version](https://img.shields.io/pypi/v/termstr.svg)](https://pypi.org/project/termstr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/termstr.svg)](https://pypi.org/project/termstr)

`termstr` elevates terminal output with customizable color, style, and alignment options for text.

-----

**Table of Contents**

- [termstr](#termstr)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [License](#license)

## Installation

```console
pip install termstr
```

## Quick Start

```python
from termstr import Color, Div, Span

hello = Span("Hello").set_foreground(Color.BLUE).set_italic()
print(hello)

world = Span("World").set_foreground(Color.GREEN).set_underline()
print(world)

hello_world = Div().set_background(Color.MAGENTA).set_bold()
hello_world += hello + ", " + world + "!"
print(hello_world)
```

![Output](https://raw.githubusercontent.com/Lingxuan-Ye/termstr/main/assets/001.png)

## License

`termstr` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
