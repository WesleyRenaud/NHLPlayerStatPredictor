from __future__ import annotations

import sys

from .ingest_artifact_puller import IngestArtifactPuller
from .server_runner import ServerRunner
from .shared.enums.position import Position
from .skater_season_finder import SkaterSeasonFinder
from .skater_season_ingester import SkaterSeasonIngester


class AppRunner():
   @classmethod
   def run( cls ) -> None:
      args = sys.argv[ Position.SECOND: ]

      if not args:
         cls.start()
         return

      name = args[ Position.FIRST ]

      if name == cls.run.__name__:
         cls.start()
         return

      method = getattr( cls, name, None )

      if method is None:
         print( 'Usage: python3 -m api [ start | ingest | pull | lookup ]' )
         raise SystemExit( Position.SECOND )

      method()


   @classmethod
   def start( cls ) -> None:
      IngestArtifactPuller.sync()
      ServerRunner.run()


   @classmethod
   def ingest( cls ) -> None:
      SkaterSeasonIngester.main( force=True )


   @classmethod
   def pull( cls ) -> None:
      IngestArtifactPuller.main()


   @classmethod
   def lookup( cls ) -> None:
      query = ' '.join( sys.argv[ Position.THIRD: ] )

      if not query:
         print( 'Usage: python3 -m api lookup "Player Name"' )
         raise SystemExit( Position.SECOND )

      SkaterSeasonFinder.main( query )
