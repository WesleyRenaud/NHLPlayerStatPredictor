from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class GithubCliResult():
   returncode: int
   stdout: str
   stderr: str
