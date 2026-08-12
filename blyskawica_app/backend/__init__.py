from importlib import import_module

__all__ = ["main"]


def __getattr__(name: str):
    if name == "main":
        return import_module(f"{__name__}.main")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
