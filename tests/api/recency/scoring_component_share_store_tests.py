from pathlib import Path

import pytest

from api.paths import Paths
from api.projections.scoring_component_shares import ScoringComponentShares
from api.recency.scoring_component_share_store import ScoringComponentShareStore


def Test_Write_TestShares_ExpectIndependentTypedRoundTrip(
      monkeypatch: pytest.MonkeyPatch,
      tmp_path: Path ) -> None:
   monkeypatch.setattr( Paths, 'PROCESSED_DIR', tmp_path )
   shares = [ ScoringComponentShares( 18, 0.8, 0.7, 0.2, 0.3, 0.0, 0.0 ) ]

   ScoringComponentShareStore.write( shares )

   assert ScoringComponentShareStore.read() == shares
   assert ScoringComponentShareStore.path().parent == tmp_path / Paths.RECENCY
   assert list( ScoringComponentShareStore.path().parent.iterdir() ) == [
      ScoringComponentShareStore.path() ]
