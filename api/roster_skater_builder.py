from __future__ import annotations

from .roster_skater import RosterSkater
from .skater_position import SkaterPosition
from .team import Team
from .types import Types


class RosterSkaterBuilder():
   FORWARD_KEY = 'forwards'
   DEFENSE_KEY = 'defensemen'


   @classmethod
   def build( cls, team: Team, payload: Types.JsonObject ) -> list[ RosterSkater ]:
      rows: list[ RosterSkater ] = []

      for key in ( RosterSkaterBuilder.FORWARD_KEY, RosterSkaterBuilder.DEFENSE_KEY ):
         for raw in cls._group( payload, key ):
            rows.append( cls._skater( team, raw ) )

      return rows


   @classmethod
   def _group( cls, payload: Types.JsonObject, key: str ) -> Types.JsonObjectList:
      raw_rows = payload[ key ]

      if not isinstance( raw_rows, list ):
         raise TypeError( key )

      return [ row for row in raw_rows if isinstance( row, dict ) ]


   @classmethod
   def _skater( cls, team: Team, raw: Types.JsonObject ) -> RosterSkater:
      return RosterSkater(
         player_id=int( raw[ 'id' ] ),
         player_name=cls._player_name( raw ),
         position=SkaterPosition( str( raw[ 'positionCode' ] ) ),
         team=team )


   @classmethod
   def _player_name( cls, raw: Types.JsonObject ) -> str:
      first_name = raw[ 'firstName' ]
      last_name = raw[ 'lastName' ]

      if not isinstance( first_name, dict ) or not isinstance( last_name, dict ):
         raise TypeError( 'localizedName' )

      return f'{ cls._default_text( first_name ) } { cls._default_text( last_name ) }'


   @classmethod
   def _default_text( cls, value: Types.JsonObject ) -> str:
      return str( value[ 'default' ] )
