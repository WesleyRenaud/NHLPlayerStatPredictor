from __future__ import annotations

import sys

from .ingest.ingest_artifact_puller import IngestArtifactPuller
from .ingest.skater_season_ingester import SkaterSeasonIngester
from .paths import Paths
from .seed.schema_migrator import SchemaMigrator
from .server.server_runner import ServerRunner
from .shared.enums.position import Position
from .skaters.player_status_hydrator import PlayerStatusHydrator
from .skaters.skater_season_finder import SkaterSeasonFinder


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
         print( 'Usage: python3 -m api [ start | ingest | pull | lookup | migrate ]' )
         raise SystemExit( Position.SECOND )

      method()


   @classmethod
   def start( cls ) -> None:
      IngestArtifactPuller.sync()
      SchemaMigrator.migrate( str( Paths.DB_PATH ) )
      PlayerStatusHydrator.hydrate( str( Paths.DB_PATH ) )
      ServerRunner.run()


   @classmethod
   def ingest( cls ) -> None:
      SchemaMigrator.migrate( str( Paths.DB_PATH ) )
      SkaterSeasonIngester.main( force=True )


   @classmethod
   def pull( cls ) -> None:
      IngestArtifactPuller.main()


   @classmethod
   def migrate( cls ) -> None:
      SchemaMigrator.migrate( str( Paths.DB_PATH ) )


   @classmethod
   def lookup( cls ) -> None:
      query = ' '.join( sys.argv[ Position.THIRD: ] )

      if not query:
         print( 'Usage: python3 -m api lookup "Player Name"' )
         raise SystemExit( Position.SECOND )

      SkaterSeasonFinder.main( query )
