from __future__ import annotations

import ast
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
import sys
import tomllib
from typing import Any


PROJECT_IMPORT_ROOTS = {
   'api',
   'conftest',
   'scripts',
   'tests',
   'tools',
}


@dataclass( frozen=True )
class ImportDeclaration:
   group: str
   sort_key: tuple[ str, str ]
   text: str


def find_root() -> Path:
   current = Path( __file__ ).resolve().parent

   while current != current.parent:
      if ( current / 'pyproject.toml' ).exists():
         return current

      current = current.parent

   return Path( __file__ ).resolve().parents[ 2 ]


ROOT = find_root()
SHOULD_FIX = '--fix' in sys.argv


def get_display_path( path: Path ) -> str:
   try:
      return path.relative_to( ROOT ).as_posix()

   except ValueError:
      return path.as_posix()


def load_style_config() -> dict[ str, Any ]:
   pyproject_path = ROOT / 'pyproject.toml'

   if not pyproject_path.exists():
      return {}

   return (
      tomllib.loads( pyproject_path.read_text() )
      .get( 'tool', {} )
      .get( 'tzg_python_style', {} )
   )


def is_excluded_path( path: Path, excluded_patterns: list[ str ] ) -> bool:
   relative_path = path.relative_to( ROOT ).as_posix()

   if any( part in { '.git', '__pycache__', 'node_modules' } for part in path.parts ):
      return True

   for pattern in excluded_patterns:
      if fnmatch( relative_path, pattern ):
         return True

   return False


def get_module_docstring_node( tree: ast.Module ) -> ast.Expr | None:
   if not tree.body:
      return None

   first_node = tree.body[ 0 ]

   if (
         isinstance( first_node, ast.Expr )
         and isinstance( first_node.value, ast.Constant )
         and isinstance( first_node.value.value, str ) ):
      return first_node

   return None


def get_allowed_import_nodes( tree: ast.Module ) -> list[ ast.Import | ast.ImportFrom ]:
   nodes = list( tree.body )
   docstring_node = get_module_docstring_node( tree )

   if docstring_node is not None:
      nodes = nodes[ 1: ]

   imports: list[ ast.Import | ast.ImportFrom ] = []

   for node in nodes:
      if not isinstance( node, ( ast.Import, ast.ImportFrom ) ):
         break

      imports.append( node )

   return imports


def find_inline_import_violations(
      path: Path,
      tree: ast.Module ) -> list[ str ]:
   allowed = {
      id( node )
      for node in get_allowed_import_nodes( tree )
   }
   violations: list[ str ] = []

   for node in ast.walk( tree ):
      if not isinstance( node, ( ast.Import, ast.ImportFrom ) ):
         continue

      if id( node ) in allowed:
         continue

      display_path = get_display_path( path )
      violations.append(
         f'{ display_path }:{ node.lineno }: imports must appear at the top of the file' )

   return violations


def get_import_insert_line( tree: ast.Module ) -> int:
   insert_line = 0

   for node in tree.body:
      if (
            isinstance( node, ast.ImportFrom )
            and node.module == '__future__' ):
         insert_line = node.end_lineno or node.lineno
         continue

      if (
            isinstance( node, ast.Expr )
            and isinstance( node.value, ast.Constant )
            and isinstance( node.value.value, str ) ):
         insert_line = node.end_lineno or node.lineno
         continue

      break

   return insert_line


def hoist_inline_imports( path: Path ) -> bool:
   file_text = path.read_text()

   try:
      tree = ast.parse( file_text )
   except SyntaxError:
      return False

   allowed = {
      id( node )
      for node in get_allowed_import_nodes( tree )
   }
   all_import_nodes: list[ ast.Import | ast.ImportFrom ] = []

   for node in ast.walk( tree ):
      if not isinstance( node, ( ast.Import, ast.ImportFrom ) ):
         continue

      all_import_nodes.append( node )

   inline_imports = [
      node
      for node in all_import_nodes
      if id( node ) not in allowed
   ]

   if not inline_imports:
      return False

   unique_imports: list[ ast.Import | ast.ImportFrom ] = []
   seen_text: set[ str ] = set()

   for node in all_import_nodes:
      text = format_import_node( node )

      if text in seen_text:
         continue

      seen_text.add( text )
      unique_imports.append( node )

   import_line_numbers: set[ int ] = set()

   for node in all_import_nodes:
      end_line = node.end_lineno or node.lineno

      import_line_numbers.update( range( node.lineno, end_line + 1 ) )

   lines = file_text.splitlines()
   kept_lines = [
      line
      for line_number, line in enumerate( lines, start=1 )
      if line_number not in import_line_numbers
   ]
   insert_line = get_import_insert_line( tree )
   kept_insert_index = sum(
      1
      for line_number in range( 1, insert_line + 1 )
      if line_number not in import_line_numbers )
   import_block = build_expected_import_block( unique_imports ).splitlines()
   updated_lines = [
      *kept_lines[ :kept_insert_index ],
      *import_block,
      *kept_lines[ kept_insert_index: ],
   ]

   while (
         kept_insert_index < len( updated_lines )
         and updated_lines[ kept_insert_index ] == ''
         and kept_insert_index > 0
         and updated_lines[ kept_insert_index - 1 ] == '' ):
      del updated_lines[ kept_insert_index ]

   path.write_text(
      '\n'.join( updated_lines )
      + ( '\n' if file_text.endswith( '\n' ) else '' ) )

   return True


def get_import_preamble_nodes( tree: ast.Module ) -> list[ ast.Import | ast.ImportFrom ]:
   return get_allowed_import_nodes( tree )


def format_alias( alias: ast.alias ) -> str:
   if alias.asname:
      return f'{ alias.name } as { alias.asname }'

   return alias.name


def sorted_aliases( aliases: list[ ast.alias ] ) -> list[ ast.alias ]:
   if any( alias.name == '*' for alias in aliases ):
      return aliases

   return sorted(
      aliases,
      key=lambda alias: format_alias( alias ).lower() )


def get_import_module( node: ast.Import | ast.ImportFrom ) -> str:
   if isinstance( node, ast.Import ):
      return node.names[ 0 ].name

   return f'{ "." * node.level }{ node.module or "" }'


def get_import_root( module: str ) -> str:
   if module.startswith( '.' ):
      return ''

   return module.split( '.', 1 )[ 0 ]


def classify_import_group( node: ast.Import | ast.ImportFrom ) -> str:
   module = get_import_module( node )

   if isinstance( node, ast.ImportFrom ) and node.module == '__future__':
      return '0-future'

   if module.startswith( '.' ):
      return '3-project'

   root = get_import_root( module )

   if root in sys.stdlib_module_names:
      return '1-stdlib'

   if root in PROJECT_IMPORT_ROOTS:
      return '3-project'

   return '2-third-party'


def format_import_node( node: ast.Import | ast.ImportFrom ) -> str:
   aliases = sorted_aliases( node.names )
   alias_text = ', '.join( format_alias( alias ) for alias in aliases )

   if isinstance( node, ast.Import ):
      return f'import { alias_text }'

   module = f'{ "." * node.level }{ node.module or "" }'
   return f'from { module } import { alias_text }'


def get_import_sort_key( node: ast.Import | ast.ImportFrom ) -> tuple[ str, str ]:
   module = get_import_module( node ).lstrip( '.' )
   aliases = sorted_aliases( node.names )
   first_alias = format_alias( aliases[ 0 ] ) if aliases else ''

   return (
      module.lower(),
      first_alias.lower() )


def build_import_declaration( node: ast.Import | ast.ImportFrom ) -> ImportDeclaration:
   return ImportDeclaration(
      group=classify_import_group( node ),
      sort_key=get_import_sort_key( node ),
      text=format_import_node( node ) )


def format_import_groups( declarations: list[ ImportDeclaration ] ) -> str:
   grouped: dict[ str, list[ ImportDeclaration ] ] = {}

   for declaration in declarations:
      grouped.setdefault( declaration.group, [] ).append( declaration )

   blocks = []

   for group in sorted( grouped ):
      block = '\n'.join(
         declaration.text
         for declaration in sorted(
            grouped[ group ],
            key=lambda declaration: declaration.sort_key )
      )
      blocks.append( block )

   return '\n\n'.join( blocks )


def build_expected_import_block( import_nodes: list[ ast.Import | ast.ImportFrom ] ) -> str:
   return format_import_groups( [
      build_import_declaration( node )
      for node in import_nodes
   ] )


def get_import_block_line_range(
      import_nodes: list[ ast.Import | ast.ImportFrom ] ) -> tuple[ int, int ]:
   first_line = min( node.lineno for node in import_nodes )
   last_line = max( node.end_lineno or node.lineno for node in import_nodes )

   return first_line, last_line


def check_file( path: Path ) -> list[ str ]:
   file_text = path.read_text()

   try:
      tree = ast.parse( file_text )
   except SyntaxError:
      return []

   if SHOULD_FIX:
      if hoist_inline_imports( path ):
         file_text = path.read_text()
         tree = ast.parse( file_text )

   violations = find_inline_import_violations( path, tree )

   if violations and not SHOULD_FIX:
      return violations

   import_nodes = get_import_preamble_nodes( tree )

   if not import_nodes:
      return violations

   start_line, end_line = get_import_block_line_range( import_nodes )
   lines = file_text.splitlines()
   current_block = '\n'.join( lines[ start_line - 1:end_line ] ).strip()
   expected_block = build_expected_import_block( import_nodes )

   if current_block != expected_block:
      if SHOULD_FIX:
         updated_lines = [
            *lines[ :start_line - 1 ],
            *expected_block.splitlines(),
            *lines[ end_line: ],
         ]
         path.write_text(
            '\n'.join( updated_lines )
            + ( '\n' if file_text.endswith( '\n' ) else '' ) )
      else:
         violations.append(
            f'{ get_display_path( path ) }: imports must be alphabetized and grouped by source' )

   return violations


def main() -> int:
   style_config = load_style_config()
   excluded_patterns = style_config.get( 'exclude', [] )
   violations: list[ str ] = []

   for path in sorted( ROOT.rglob( '*.py' ) ):
      if is_excluded_path( path, excluded_patterns ):
         continue

      violations.extend( check_file( path ) )

   if not violations:
      return 0

   if not SHOULD_FIX:
      print( 'Python import style violations:' )

      for violation in violations:
         print( violation )

      print( '\nRun `python3 tools/lint/pythonImportStyle.py --fix` to update imports.' )
      return 1

   return 0


if __name__ == '__main__':
   sys.exit( main() )
