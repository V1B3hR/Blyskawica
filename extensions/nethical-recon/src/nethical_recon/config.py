"""Configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Config:
    """Runtime configuration."""

    verbose: bool = False
