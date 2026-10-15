"""One look and feel for every ``ddspace`` command: headers, bulleted questions, status lines, summaries, tables.

Conventions:
- each command opens with a header line (``ddspace <command>``) and a short subtitle;
- questions are bullets, with the default shown in brackets; Enter keeps it;
- results are lines with a mark: ``✓`` done, ``!`` worth a look, ``✗`` error;
- a command ends with a summary panel (aligned key/value rows) and the next commands to run;
- paths and secondary details are dim; commands are bold cyan.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from rich import box
from rich.console import Console, Group
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

console = Console()
ACCENT = "cyan"
BULLET = f"[{ACCENT}]•[/{ACCENT}]"
MASK = "•"


# ---------------------------------------------------------------- structure


def header(command: str, subtitle: str = "") -> None:
    """Open a command's output: ``ddspace <command>`` and what it does."""
    console.print()
    console.print(Rule(Text.assemble(("ddspace ", "bold"), (command, f"bold {ACCENT}")), align="left",
                       style=ACCENT))
    if subtitle:
        console.print(f"[dim]{subtitle}[/dim]")


def section(title: str) -> None:
    """Start a group of questions or results inside a command."""
    console.print(f"\n[bold]{title}[/bold]")


def command(text: str) -> str:
    """Format a command to run (``ddspace mine``) for display."""
    return f"[bold {ACCENT}]{text}[/bold {ACCENT}]"


def short_path(value: object) -> str:
    """Return a path as the user would type it: relative to the current folder, else with ``~`` for home."""
    p = Path(str(value)).expanduser()
    try:
        rel = p.resolve().relative_to(Path.cwd().resolve())
        return "." if str(rel) == "." else rel.as_posix()
    except (ValueError, OSError):
        pass
    try:
        return "~/" + p.resolve().relative_to(Path.home().resolve()).as_posix()
    except (ValueError, OSError):
        return str(p)


def path(text: object) -> str:
    """Format a file or folder path (or a short note) for display."""
    return f"[dim]{escape(str(text))}[/dim]"


# ---------------------------------------------------------------- status lines


def ok(message: str) -> None:
    """Print a step that succeeded."""
    console.print(f"  [green]✓[/green] {message}")


def warn(message: str) -> None:
    """Print something worth a look; the command continues."""
    console.print(f"  [yellow]![/yellow] {message}")


def note(message: str) -> None:
    """Print neutral information."""
    console.print(f"  [dim]{message}[/dim]")


def error(message: str) -> None:
    """Print an error (the caller exits); the message is plain text, so brackets such as [chat] are kept."""
    console.print(f"[red]✗ Error:[/red] {escape(message)}")


def status(message: str):
    """Return a spinner with a message, for work that takes a moment."""
    return console.status(f"[{ACCENT}]{message}[/{ACCENT}]", spinner="dots")


# ---------------------------------------------------------------- questions (bullets)


def ask_text(question: str, default: Optional[str] = None, choices: Optional[Sequence[str]] = None) -> str:
    """Ask for text; Enter keeps the default."""
    return Prompt.ask(f"  {BULLET} {question}", default=default, choices=list(choices) if choices else None)


def ask_int(question: str, default: int) -> int:
    """Ask for a whole number; re-asks until it is one."""
    return IntPrompt.ask(f"  {BULLET} {question}", default=default)


def ask_yes(question: str, default: bool = True) -> bool:
    """Ask a yes/no question."""
    return Confirm.ask(f"  {BULLET} {question}", default=default)


def mask_secret(value: str, visible: int = 8) -> str:
    """Show the first ``visible`` characters of a secret and mask the rest."""
    return value[:visible] + MASK * max(0, len(value) - visible)


def ask_secret(question: str, visible: int = 8) -> str:
    """Ask for a secret (an API key): the first ``visible`` characters are echoed, the rest masked as typed or pasted.

    Without a terminal (scripts, tests) the line is read as is.
    """
    prompt = f"  {BULLET} {question}: "
    if not sys.stdin.isatty():
        console.print(prompt, end="")
        return sys.stdin.readline().strip()
    console.print(prompt, end="")
    value = _read_masked(visible)
    console.print()
    return value.strip()


def _read_masked(visible: int) -> str:
    chars: List[str] = []

    def echo(ch: str) -> None:
        sys.stdout.write(ch if len(chars) <= visible else MASK)
        sys.stdout.flush()

    def erase() -> None:
        sys.stdout.write("\b \b")
        sys.stdout.flush()

    if os.name == "nt":  # pragma: no cover - Windows console
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                return "".join(chars)
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch == "\x08":
                if chars:
                    chars.pop()
                    erase()
                continue
            chars.append(ch)
            echo(ch)
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch in ("\r", "\n", ""):
                return "".join(chars)
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch in ("\x7f", "\x08"):
                if chars:
                    chars.pop()
                    erase()
                continue
            if ch == "\x1b":  # skip a whole escape sequence (arrow keys, bracketed-paste markers)
                nxt = sys.stdin.read(1)
                if nxt == "[":
                    while not (ch := sys.stdin.read(1)).isalpha() and ch != "~" and ch:
                        pass
                continue
            if ord(ch) < 32:  # other control keys are ignored
                continue
            chars.append(ch)
            echo(ch)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ---------------------------------------------------------------- summaries and tables


def summary(title: str, rows: Iterable[Tuple[str, str]] = (), next_steps: Iterable[Tuple[str, str]] = (),
            text: str = "", style: str = "green") -> None:
    """Close a command with a panel: aligned key/value rows, optional text, and the next commands to run."""
    parts: List[object] = []
    rows = [(k, v) for k, v in rows if v not in (None, "")]
    if rows:
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="dim", no_wrap=True)
        grid.add_column()
        for key, value in rows:
            grid.add_row(key, value)
        parts.append(grid)
    if text:
        parts.append(Text.from_markup(("\n" if parts else "") + text))
    steps = list(next_steps)
    if steps:
        grid = Table.grid(padding=(0, 2))
        grid.add_column(no_wrap=True)
        grid.add_column(style="dim")
        for cmd, why in steps:  # commands in the accent style; plain instructions (e.g. copy files) as text
            grid.add_row(command(cmd) if cmd.startswith(("ddspace", "cd ")) else escape(cmd), why)
        parts.append(Text.from_markup("\n[bold]Next[/bold]"))
        parts.append(grid)
    mark = {"green": "✓ ", "red": "✗ ", "yellow": "! "}.get(style, "")
    console.print(Panel(Group(*parts), title=f"[bold]{mark}{title}[/bold]", title_align="left",
                        border_style=style, box=box.ROUNDED, expand=False, padding=(0, 1)))


def plan(title: str, rows: Iterable[Tuple[str, str]], text: str = "") -> None:
    """Show what a command is about to do (before asking to go ahead)."""
    summary(title, rows, text=text, style=ACCENT)


def table(title: str, columns: Sequence[str], rows: Iterable[Sequence[object]],
          styles: Optional[Sequence[str]] = None, right: Sequence[str] = ()) -> None:
    """Print a table in the house style (``right``: right-aligned columns; ``styles``: one row style each)."""
    t = Table(title=title, title_style="bold", title_justify="left", box=box.SIMPLE_HEAD,
              header_style=f"bold {ACCENT}", pad_edge=False)
    for c in columns:
        t.add_column(c, overflow="fold", justify="right" if c in right else "left")
    styles = list(styles or [])
    for i, r in enumerate(rows):
        t.add_row(*["" if x is None else str(x) for x in r], style=styles[i] if i < len(styles) else None)
    console.print(t)
