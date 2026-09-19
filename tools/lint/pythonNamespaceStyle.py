from __future__ import annotations

import ast
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath
import sys
import tomllib
from typing import Any


def find_root() -> Path:
   current = Path( __file__ ).resolve().parent

   while current != current.parent:
      if ( current / 'pyproject.toml' ).exists():
         return current

      current = current.parent

   return Path( __file__ ).resolve().parents[ 2 ]


ROOT = find_root()


def get_display_path( path: Path ) -> str:
   try:
      return path.relative_to( ROOT ).as_posix()

   except ValueError:
      return path.as_posix()


def load_config() -> dict[ str, Any ]:
   pyproject_path = ROOT / 'pyproject.toml'

   if not pyproject_path.exists():
      return {}

   return (
      tomllib.loads( pyproject_path.read_text() )
      .get( 'tool', {} )
      .get( 'tzg_python_namespace_style', {} )
   )


def snake_to_pascal( stem: str ) -> str:
   return ''.join( word.capitalize() for word in stem.split( '_' ) )


def is_excluded_path( path: Path, patterns: list[ str ] ) -> bool:
   display_path = get_display_path( path )

   for pattern in patterns:
      if PurePosixPath( display_path ).match( pattern ):
         return True

      if fnmatch( display_path, pattern ):
         return True

   return False


def namespace_holder_class_name( path: Path ) -> str | None:
   stem = path.stem

   if stem in { 'paths', 'types', 'constants', 'data' }:
      return snake_to_pascal( stem )

   if stem.endswith( '_routes' ):
      return snake_to_pascal( stem )

   return None


def build_namespace_holder_modules( include: list[ str ] ) -> dict[ str, str ]:
   modules: dict[ str, str ] = {}

   for pattern in include:
      for path in ROOT.glob( pattern ):
         class_name = namespace_holder_class_name( path )

         if class_name == None:
            continue

         modules[ path.stem ] = class_name

   return modules


def is_module_level_reexport( node: ast.AST ) -> bool:
   if not isinstance( node, ast.Assign ):
      return False

   if not isinstance( node.value, ast.Attribute ):
      return False

   if not isinstance( node.value.value, ast.Name ):
      return False

   for target in node.targets:
      if not isinstance( target, ast.Name ):
         continue

      if target.id == node.value.attr:
         return True

   return False


def import_module_stem( module: str | None ) -> str | None:
   if module == None:
      return None

   return module.rsplit( '.', 1 )[ -1 ]


def check_file(
      path: Path,
      namespace_modules: dict[ str, str ] ) -> list[ str ]:
   display_path = get_display_path( path )

   try:
      tree = ast.parse( path.read_text() )
   except SyntaxError as error:
      return [ f'{ display_path }: { error }' ]

   violations: list[ str ] = []

   for node in tree.body:
      if is_module_level_reexport( node ):
         assert isinstance( node, ast.Assign )
         assert isinstance( node.value, ast.Attribute )
         violations.append(
            f'{ display_path }:{ node.lineno }: '
            f'module-level re-export { node.value.attr } = '
            f'{ node.value.value.id }.{ node.value.attr } is not allowed; '
            f'use { node.value.value.id }.{ node.value.attr } at call sites' )
         continue

      if not isinstance( node, ast.ImportFrom ):
         continue

      module_stem = import_module_stem( node.module )
      class_name = namespace_modules.get( module_stem ) if module_stem != None else None

      if class_name == None:
         continue

      for alias in node.names:
         if alias.name == class_name:
            continue

         violations.append(
            f'{ display_path }:{ node.lineno }: '
            f'import { alias.name } from namespace module { module_stem }; '
            f'use { class_name }.{ alias.name } instead' )

   return violations


def main() -> int:
   config = load_config()
   include = config.get( 'include', [ 'api/**/*.py', 'tests/**/*.py' ] )
   excluded_patterns = config.get( 'exclude', [] )
   namespace_modules = build_namespace_holder_modules( include )
   violations: list[ str ] = []

   for pattern in include:
      for path in sorted( ROOT.glob( pattern ) ):
         if is_excluded_path( path, excluded_patterns ):
            continue

         violations.extend( check_file( path, namespace_modules ) )

   if not violations:
      return 0

   for violation in violations:
      print( violation )

   print( f'\nFound { len( violations ) } namespace-style violation(s).' )
   return 1


if __name__ == '__main__':
   sys.exit( main() )
