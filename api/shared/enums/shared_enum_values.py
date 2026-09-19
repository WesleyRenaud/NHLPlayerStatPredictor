from __future__ import annotations

import json
from pathlib import Path


class SharedEnumValues:
   @staticmethod
   def repository_root() -> Path:
      return Path( __file__ ).resolve().parents[ 3 ]


   @staticmethod
   def shared_enums_directory() -> Path:
      return SharedEnumValues.repository_root() / 'shared' / 'enums'


   @staticmethod
   def load( json_name: str ) -> dict[ str, str ]:
      path = SharedEnumValues.shared_enums_directory() / json_name
      members = json.loads( path.read_text( encoding='utf-8' ) )

      if not isinstance( members, dict ) or not members:
         raise ValueError(
            f'{ path }: expected a non-empty object of MEMBER -> wire value' )

      for key, value in members.items():
         if not isinstance( key, str ) or not key.isidentifier() or not key.isupper():
            raise ValueError(
               f'{ path }: member key must be SCREAMING_SNAKE identifier: '
               f'{ repr( key ) }' )

         if not isinstance( value, str ) or not value:
            raise ValueError(
               f'{ path }: wire value for { key } must be a non-empty string' )

      return dict( sorted( members.items() ) )


   @staticmethod
   def load_object_members(
         json_name: str ) -> dict[ str, dict[ str, object ] ]:
      path = SharedEnumValues.shared_enums_directory() / json_name
      members = json.loads( path.read_text( encoding='utf-8' ) )

      if not isinstance( members, dict ) or not members:
         raise ValueError(
            f'{ path }: expected a non-empty object of MEMBER -> object value' )

      normalized: dict[ str, dict[ str, object ] ] = {}

      for key, value in members.items():
         if not isinstance( key, str ) or not key.isidentifier() or not key.isupper():
            raise ValueError(
               f'{ path }: member key must be SCREAMING_SNAKE identifier: '
               f'{ repr( key ) }' )

         if not isinstance( value, dict ):
            raise ValueError(
               f'{ path }: value for { key } must be an object' )

         kind = value.get( 'kind' )

         if not isinstance( kind, str ) or not kind:
            raise ValueError(
               f'{ path }: kind for { key } must be a non-empty string' )

         normalized[ key ] = dict( value )

      return dict( sorted( normalized.items() ) )


   @staticmethod
   def load_integers( json_name: str ) -> dict[ str, int ]:
      path = SharedEnumValues.shared_enums_directory() / json_name
      members = json.loads( path.read_text( encoding='utf-8' ) )

      if not isinstance( members, dict ) or not members:
         raise ValueError(
            f'{ path }: expected a non-empty object of MEMBER -> integer value' )

      normalized: dict[ str, int ] = {}

      for key, value in members.items():
         if not isinstance( key, str ) or not key.isidentifier() or not key.isupper():
            raise ValueError(
               f'{ path }: member key must be SCREAMING_SNAKE identifier: '
               f'{ repr( key ) }' )

         if isinstance( value, bool ) or not isinstance( value, int ):
            raise ValueError(
               f'{ path }: integer value for { key } must be an int' )

         normalized[ key ] = value

      return dict( sorted( normalized.items() ) )
