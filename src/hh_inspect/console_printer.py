from typing import Any, Self


class ConsolePrinter:
    """Singleton to print or not to print output to console depending on the settings."""

    _instance: Self | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:  # noqa: ARG004
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, print_to_console: bool = True) -> None:
        self.print_to_console = print_to_console

    def print(self, *values: object) -> None:
        if self.print_to_console:
            print(*values)  # noqa: T201
