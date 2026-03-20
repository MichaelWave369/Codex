"""Minimal local fallback implementing subset of Typer API used by CODEX.

This shim supports offline execution in constrained environments.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, get_type_hints


@dataclass
class _Option:
    default: Any
    flags: tuple[str, ...]
    exists: bool = False
    readable: bool = False
    help: str | None = None


def Option(default: Any = None, *flags: str, **kwargs: Any) -> _Option:  # noqa: N802
    """Define a command option placeholder."""
    return _Option(default=default, flags=flags, **kwargs)


def echo(message: str) -> None:
    """Print output line."""
    print(message)


class Typer:
    """Very small command registry compatible with CODEX CLI usage."""

    def __init__(self, help: str | None = None):
        self.help = help
        self._commands: dict[str, Callable[..., Any]] = {}

    def command(self, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a CLI command."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._commands[name] = func
            return func

        return decorator

    def __call__(self) -> None:
        parser = argparse.ArgumentParser(description=self.help)
        subparsers = parser.add_subparsers(dest="command", required=True)

        for name, func in self._commands.items():
            cmd_parser = subparsers.add_parser(name)
            kwargs_map: dict[str, str] = {}
            type_hints = get_type_hints(func)
            for arg_name, default in func.__defaults_map__.items():
                if isinstance(default, _Option):
                    flags = default.flags or (f"--{arg_name.replace('_', '-')}",)
                    arg_kwargs: dict[str, Any] = {}
                    if default.default is ...:
                        arg_kwargs["required"] = True
                    elif isinstance(default.default, bool):
                        arg_kwargs["action"] = "store_true"
                    else:
                        arg_kwargs["default"] = default.default

                    annotation = type_hints.get(arg_name)
                    if annotation is not None and annotation is not bool:
                        arg_kwargs["type"] = annotation
                    if default.help:
                        arg_kwargs["help"] = default.help
                    cmd_parser.add_argument(*flags, dest=arg_name, **arg_kwargs)
                    kwargs_map[arg_name] = arg_name
            cmd_parser.set_defaults(__func__=func, __kwargs_map__=kwargs_map)

        parsed = parser.parse_args()
        func = parsed.__func__
        kwargs = {k: getattr(parsed, v) for k, v in parsed.__kwargs_map__.items()}
        func(**kwargs)


def _extract_defaults(func: Callable[..., Any]) -> dict[str, Any]:
    names = func.__code__.co_varnames[: func.__code__.co_argcount]
    defaults = func.__defaults__ or ()
    start = len(names) - len(defaults)
    mapping = {names[start + i]: defaults[i] for i in range(len(defaults))}
    return mapping


_original_command = Typer.command


def _patched_command(self: Typer, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    decorator = _original_command(self, name)

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        func.__defaults_map__ = _extract_defaults(func)
        return decorator(func)

    return wrapper


Typer.command = _patched_command
