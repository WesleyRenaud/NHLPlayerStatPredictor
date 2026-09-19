from __future__ import annotations

import ast
from fnmatch import fnmatch
from pathlib import Path
import re
import sys
import tomllib
from typing import Any


FULL_TEST_NAME_RE = re.compile(
   r'^Test_[A-Z][A-Za-z0-9]*_Test[A-Za-z0-9][A-Za-z0-9]*_Expect[A-Za-z0-9][A-Za-z0-9]*$' )
PARAMETRIZED_TEST_NAME_RE = re.compile( r'^Test_[A-Za-z][A-Za-z0-9_]*$' )


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
      .get( 'tzg_python_unit_tests', {} )
   )


def is_excluded_path( path: Path, patterns: list[ str ] ) -> bool:
   display_path = get_display_path( path )

   if any( part in { '.git', '__pycache__', 'node_modules' } for part in path.parts ):
      return True

   for pattern in patterns:
      if fnmatch( display_path, pattern ):
         return True

   return False


def expected_production_file( test_path: Path ) -> Path:
   stem = test_path.name[ : -len( '_tests.py' ) ]
   api_relative_parent = test_path.relative_to( ROOT / 'tests' / 'api' ).parent

   return ROOT / 'api' / api_relative_parent / f'{ stem }.py'


def has_parametrize_decorator( node: ast.FunctionDef ) -> bool:
   for decorator in node.decorator_list:
      if isinstance( decorator, ast.Attribute ) and decorator.attr == 'parametrize':
         return True

      if (
            isinstance( decorator, ast.Call )
            and isinstance( decorator.func, ast.Attribute )
            and decorator.func.attr == 'parametrize' ):
         return True

   return False


def has_fixture_decorator( node: ast.FunctionDef ) -> bool:
   for decorator in node.decorator_list:
      if isinstance( decorator, ast.Attribute ) and decorator.attr == 'fixture':
         return True

      if (
            isinstance( decorator, ast.Call )
            and isinstance( decorator.func, ast.Attribute )
            and decorator.func.attr == 'fixture' ):
         return True

   return False


def is_test_setup_definition( node: ast.AST ) -> bool:
   if isinstance( node, ast.FunctionDef ):
      if node.name.startswith( 'Test_' ):
         return False

      if node.name.startswith( '_' ):
         return True

      return has_fixture_decorator( node )

   if isinstance( node, ( ast.ClassDef, ast.Assign, ast.AnnAssign ) ):
      return True

   return False


def check_test_file_names( test_paths: list[ Path ] ) -> list[ str ]:
   violations: list[ str ] = []
   production_to_tests: dict[ str, list[ str ] ] = {}

   for test_path in test_paths:
      display_path = get_display_path( test_path )

      if not display_path.startswith( 'tests/api/' ):
         continue

      if test_path.name in ( 'conftest.py', '__init__.py' ):
         continue

      if not test_path.name.endswith( '_tests.py' ):
         violations.append(
            f'{ display_path }: test files must end with _tests.py' )
         continue

      production_file = expected_production_file( test_path )
      production_display_path = get_display_path( production_file )

      if not production_file.exists():
         violations.append(
            f'{ display_path }: expected production file '
            f'{ production_display_path }' )
         continue

      production_to_tests.setdefault(
         production_display_path,
         [] ).append( display_path )

   for production_display_path, test_display_paths in production_to_tests.items():
      if len( test_display_paths ) > 1:
         violations.append(
            f'{ production_display_path }: multiple test files found: '
            f'{ ", ".join( sorted( test_display_paths ) ) }' )

   return violations


def check_test_function_names( test_path: Path ) -> list[ str ]:
   display_path = get_display_path( test_path )
   violations: list[ str ] = []

   try:
      tree = ast.parse( test_path.read_text() )
   except SyntaxError as error:
      return [ f'{ display_path }: { error }' ]

   for node in tree.body:
      if not isinstance( node, ast.FunctionDef ) or not node.name.startswith( 'Test_' ):
         continue

      if FULL_TEST_NAME_RE.match( node.name ):
         continue

      if (
            has_parametrize_decorator( node )
            and PARAMETRIZED_TEST_NAME_RE.match( node.name ) ):
         continue

      violations.append(
         f'{ display_path }:{ node.lineno }: { node.name } must match '
         'Test_[Method]_Test[Scenario]_Expect[Outcome] '
         '(parametrized tests may use Test_[Method] only)' )

   return violations


def check_helper_grouping( test_path: Path ) -> list[ str ]:
   display_path = get_display_path( test_path )
   violations: list[ str ] = []

   try:
      tree = ast.parse( test_path.read_text() )
   except SyntaxError as error:
      return [ f'{ display_path }: { error }' ]

   seen_test = False

   for node in tree.body:
      if isinstance( node, ast.FunctionDef ) and node.name.startswith( 'Test_' ):
         seen_test = True
         continue

      if not seen_test:
         continue

      if isinstance( node, ast.FunctionDef ) and is_test_setup_definition( node ):
         kind = 'fixture' if has_fixture_decorator( node ) else 'helper'

         violations.append(
            f'{ display_path }:{ node.lineno }: { kind } { node.name } '
            'must appear before all Test_ functions' )

   return violations


def iter_test_files( include: list[ str ] ) -> list[ Path ]:
   paths: set[ Path ] = set()

   for pattern in include:
      paths.update( ROOT.glob( pattern ) )

   return sorted( paths )


def main() -> int:
   config = load_config()
   include = config.get( 'include', [ 'tests/api/**/*.py' ] )
   exclude = config.get( 'exclude', [ 'tests/api/api_test_support/**' ] )
   test_paths = [
      path
      for path in iter_test_files( include )
      if not is_excluded_path( path, exclude )
   ]
   violations: list[ str ] = []

   violations.extend( check_test_file_names( test_paths ) )

   for path in test_paths:
      violations.extend( check_test_function_names( path ) )
      violations.extend( check_helper_grouping( path ) )

   if not violations:
      return 0

   for violation in violations:
      print( violation )

   print( f'\nFound { len( violations ) } unit-test style violation(s).' )
   return 1


if __name__ == '__main__':
   sys.exit( main() )
