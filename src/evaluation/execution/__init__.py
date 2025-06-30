"""Execution modules for running evaluations locally or remotely."""

from .base import ExecutionMode, Executor
from .local import LocalExecutor
from .remote import RemoteExecutor

__all__ = ["ExecutionMode", "Executor", "LocalExecutor", "RemoteExecutor"]
