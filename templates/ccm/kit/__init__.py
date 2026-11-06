"""The report kit. One module holds each part of the page.

Every folder the build reads sits beside build.py, so the ZIP unpacks into a
folder a reader can run.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
