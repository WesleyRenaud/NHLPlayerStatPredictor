from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import sys


ROOT = Path( __file__ ).resolve().parents[ 1 ]
CATALOG_PATH = ROOT / 'shared' / 'enums' / 'catalog.json'

if str( ROOT ) not in sys.path:
   sys.path.insert( 0, str( ROOT ) )


def load_catalog() -> dict:
   return json.loads( CATALOG_PATH.read_text( encoding='utf-8' ) )


def load_json_members( json_name: str ) -> dict[ str, str | int ]:
   path = ROOT / 'shared' / 'enums' / json_name
   members = json.loads( path.read_text( encoding='utf-8' ) )

   if not isinstance( members, dict ) or not members:
      raise ValueError( f'{ path }: expected a non-empty object' )

   return dict( sorted( members.items() ) )


def python_module_name( relative_path: str ) -> str:
   return relative_path.removesuffix( '.py' ).replace( '/', '.' )


def has_object_values( entry: dict, members: dict ) -> bool:
   if entry.get( 'valueShape' ) == 'object':
      return True

   return all( isinstance( value, dict ) for value in members.values() )


def expected_wire_values( members: dict, object_shape: bool ) -> dict:
   if not object_shape:
      return members

   return {
      name: value[ 'kind' ]
      for name, value in members.items()
   }


def check_python( entry: dict, members: dict, object_shape: bool ) -> list[ str ]:
   violations: list[ str ] = []
   module = importlib.import_module( python_module_name( entry[ 'pythonModule' ] ) )
   enum_cls = getattr( module, entry[ 'pythonClass' ], None )

   if enum_cls is None:
      return [
         f'{ entry[ "pythonModule" ] }: missing { entry[ "pythonClass" ] }'
      ]

   actual = {
      name: member.value
      for name, member in enum_cls.__members__.items()
   }

   if actual != expected_wire_values( members, object_shape ):
      violations.append(
         f'{ entry[ "pythonModule" ] }: { entry[ "pythonClass" ] } does not match '
         f'shared/enums/{ entry[ "json" ] }'
      )

   return violations


def check_javascript( entry: dict, members: dict ) -> list[ str ]:
   violations: list[ str ] = []
   path = ROOT / entry[ 'javascriptModule' ]
   relative = entry[ 'javascriptModule' ]

   if not path.exists():
      return [ f'missing { relative }' ]

   source = path.read_text( encoding='utf-8' )
   json_name = entry[ 'json' ]
   import_pattern = re.compile(
      rf"from\s+['\"][^'\"]*{ re.escape( json_name ) }['\"]\s+with\s*\{{\s*type:\s*['\"]json['\"]\s*\}}"
   )

   if not import_pattern.search( source ):
      violations.append(
         f'{ relative }: must import shared/enums/{ json_name } with type json'
      )

   if f'export class { entry[ "javascriptClass" ] }' not in source:
      violations.append(
         f'{ relative }: missing export class { entry[ "javascriptClass" ] }'
      )

   freeze_assign_pattern = re.compile(
      rf'{ re.escape( entry[ "javascriptClass" ] ) }\s*\[[^\]]+\]\s*=\s*Object\.freeze\('
   )

   if 'Object.assign(' not in source and not freeze_assign_pattern.search( source ):
      violations.append(
         f'{ relative }: must Object.assign shared JSON values onto the class '
         f'(or freeze-assign each member onto it)'
      )

   return violations


def report( violations: list[ str ] ) -> int:
   if not violations:
      return 0

   print( 'Shared enum check failed:' )

   for violation in violations:
      print( f'  { violation }' )

   return 1


def check() -> int:
   catalog = load_catalog()
   violations: list[ str ] = []

   for entry in catalog[ 'enums' ]:
      members = load_json_members( entry[ 'json' ] )
      object_shape = has_object_values( entry, members )
      violations.extend( check_python( entry, members, object_shape ) )
      violations.extend( check_javascript( entry, members ) )

   return report( violations )


def main() -> int:
   parser = argparse.ArgumentParser(
      description=(
         'Verify API/JS shared enums load from shared/enums JSON '
         '(values are not duplicated in generated copies).'
      )
   )
   parser.parse_args()
   return check()


if __name__ == '__main__':
   raise SystemExit( main() )
