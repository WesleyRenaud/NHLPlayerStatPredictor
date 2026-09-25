from __future__ import annotations


class MixDelta():
   @classmethod
   def resolve( cls, current: float, prior: float, healthy: float ) -> float:
      return current - prior + healthy
