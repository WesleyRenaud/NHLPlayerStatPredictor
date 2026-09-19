from __future__ import annotations

import sys

from .position import Position
from .server_runner import ServerRunner
from .skater_season_finder import SkaterSeasonFinder
from .skater_season_ingester import SkaterSeasonIngester


class AppRunner():
   @classmethod
   def run( cls ) -> None:
      args = sys.argv[ Position.SECOND: ]

      if not args:
         cls.start()
         return

      method = getattr( cls, args[ Position.FIRST ], None )

      if method is None or method == cls.run:
         print( 'Usage: python3 -m api [ start | ingest | lookup ]' )
         raise SystemExit( Position.SECOND )

      method()


   @classmethod
   def start( cls ) -> None:
      ServerRunner.run()


   @classmethod
   def ingest( cls ) -> None:
      SkaterSeasonIngester.main()


   @classmethod
   def lookup( cls ) -> None:
      query = ' '.join( sys.argv[ Position.THIRD: ] )

      if not query:
         print( 'Usage: python3 -m api lookup "Player Name"' )
         raise SystemExit( Position.SECOND )

      SkaterSeasonFinder.main( query )
