from __future__ import annotations

from abc import ABC, abstractmethod

from core.step import Step


class Problem(ABC):
    """Base class all visualizable problems must extend."""

    @staticmethod
    @abstractmethod
    def name() -> str:
        """Display name shown in the problem selector."""
        ...

    @staticmethod
    @abstractmethod
    def topic() -> str:
        """Top-level category, e.g. 'Backtracking', 'Graph / DFS'."""
        ...

    @staticmethod
    @abstractmethod
    def subtopic() -> str:
        """Subtopic within the category, e.g. 'Constraint Satisfaction', 'Flood Fill'."""
        ...

    @staticmethod
    @abstractmethod
    def description() -> str:
        """Short description shown in the UI."""
        ...

    @staticmethod
    @abstractmethod
    def source_code() -> str:
        """Algorithm source code displayed in the code panel.

        Line numbers in Step.line_number refer to 1-indexed lines of this string.
        """
        ...

    @staticmethod
    @abstractmethod
    def renderer_type() -> str:
        """Which renderer to use: 'board' or 'array'."""
        ...

    @staticmethod
    @abstractmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        """Run the algorithm and return all visualization steps."""
        ...

    @staticmethod
    def default_params() -> dict[str, object]:
        """Default parameters. Override to add UI-configurable params."""
        return {}

    @staticmethod
    def long_description() -> str:
        """Full problem statement shown in the detail panel. Override per problem."""
        return ""

    @staticmethod
    def theory() -> str:
        """Algorithm theory, complexity, and key insights. Override per problem."""
        return ""
