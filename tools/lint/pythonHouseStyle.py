from __future__ import annotations

import ast
from fnmatch import fnmatch
from io import BytesIO
from pathlib import Path
import sys
import tokenize
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
SKIP_TOKEN_TYPES = {
   tokenize.NL,
   tokenize.NEWLINE,
   tokenize.INDENT,
   tokenize.DEDENT,
   tokenize.COMMENT,
   tokenize.ENCODING
}
OPENERS = {
   '(': ')',
   '[': ']',
   '{': '}'
}
CLOSERS = {
   ')': '(',
   ']': '[',
   '}': '{'
}


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


def get_definition_start_line( node: ast.AST ) -> int:
   if getattr( node, 'decorator_list', None ):
      return min( decorator.lineno for decorator in node.decorator_list )

   return node.lineno


def is_str_object_mapping_annotation( node: ast.expr ) -> bool:
   if not isinstance( node, ast.Subscript ):
      return False

   if not isinstance( node.value, ast.Name ) or node.value.id not in { 'dict', 'Mapping' }:
      return False

   if not isinstance( node.slice, ast.Tuple ) or len( node.slice.elts ) != 2:
      return False

   key_type, value_type = node.slice.elts

   return (
      isinstance( key_type, ast.Name )
      and key_type.id == 'str'
      and isinstance( value_type, ast.Name )
      and value_type.id == 'object' )


def allowed_object_name_nodes( annotation: ast.expr | None ) -> set[ ast.AST ]:
   if annotation is None:
      return set()

   allowed_object_nodes: set[ ast.AST ] = set()

   for node in ast.walk( annotation ):
      if is_str_object_mapping_annotation( node ):
         allowed_object_nodes.add( node.slice.elts[ 1 ] )

   return allowed_object_nodes


def annotation_uses_disallowed_object( annotation: ast.expr | None ) -> bool:
   if annotation is None:
      return False

   allowed_object_nodes = allowed_object_name_nodes( annotation )

   for child in ast.walk( annotation ):
      if isinstance( child, ast.Name ) and child.id == 'object' and child not in allowed_object_nodes:
         return True

   return False


DISALLOWED_HOMOGENEOUS_COLLECTION_NAMES = frozenset( { 'Iterable', 'Sequence' } )


def annotation_type_name( node: ast.expr ) -> str | None:
   if isinstance( node, ast.Name ):
      return node.id

   if isinstance( node, ast.Attribute ):
      return node.attr

   return None


def is_ellipsis_node( node: ast.expr ) -> bool:
   return isinstance( node, ast.Constant ) and node.value is Ellipsis


def is_variadic_tuple_annotation( node: ast.expr ) -> bool:
   if not isinstance( node, ast.Subscript ):
      return False

   if annotation_type_name( node.value ) not in { 'tuple', 'Tuple' }:
      return False

   slice_node = node.slice

   if not isinstance( slice_node, ast.Tuple ) or len( slice_node.elts ) < 2:
      return False

   return is_ellipsis_node( slice_node.elts[ -1 ] )


def disallowed_homogeneous_collection_message( node: ast.expr ) -> str | None:
   if isinstance( node, ast.Subscript ):
      subscript_name = annotation_type_name( node.value )

      if subscript_name in DISALLOWED_HOMOGENEOUS_COLLECTION_NAMES:
         return (
            f'Do not use "{ subscript_name }" for homogeneous collections; '
            'use list[T] instead.' )

      if is_variadic_tuple_annotation( node ):
         return (
            'Do not use "tuple[T, ...]" for homogeneous collections; '
            'use list[T] instead (fixed-arity tuples like tuple[int, int] are allowed).' )

      return None

   type_name = annotation_type_name( node )

   if type_name in DISALLOWED_HOMOGENEOUS_COLLECTION_NAMES:
      return (
         f'Do not use "{ type_name }" for homogeneous collections; '
         'use list[T] instead.' )

   return None


def iter_disallowed_homogeneous_collection_nodes(
      annotation: ast.expr | None ) -> list[ ast.expr ]:
   if annotation is None:
      return []

   subscript_values = {
      child.value
      for child in ast.walk( annotation )
      if isinstance( child, ast.Subscript )
   }
   disallowed_nodes: list[ ast.expr ] = []

   for child in ast.walk( annotation ):
      if not isinstance( child, ast.expr ):
         continue

      if child in subscript_values:
         continue

      if disallowed_homogeneous_collection_message( child ) is not None:
         disallowed_nodes.append( child )

   return disallowed_nodes


def report_disallowed_homogeneous_collections(
      violations: list[ tuple[ str, int, int, str ] ],
      path: Path,
      annotation: ast.expr | None ) -> None:
   for node in iter_disallowed_homogeneous_collection_nodes( annotation ):
      message = disallowed_homogeneous_collection_message( node )

      if message is None:
         continue

      add_violation(
         violations,
         path,
         node.lineno or 1,
         ( node.col_offset or 0 ) + 1,
         message )


def check_disallowed_collection_imports(
      path: Path,
      tree: ast.AST ) -> list[ tuple[ str, int, int, str ] ]:
   violations: list[ tuple[ str, int, int, str ] ] = []

   for node in ast.walk( tree ):
      if not isinstance( node, ( ast.Import, ast.ImportFrom ) ):
         continue

      for alias in node.names:
         imported_name = alias.name.rsplit( '.', 1 )[ -1 ]

         if imported_name not in DISALLOWED_HOMOGENEOUS_COLLECTION_NAMES:
            continue

         add_violation(
            violations,
            path,
            node.lineno,
            ( node.col_offset or 0 ) + 1,
            (
               f'Do not import "{ imported_name }" for collection typing; '
               'use list[T] instead.' ) )

   return violations


def check_typing_annotations(
      path: Path,
      file_text: str ) -> list[ tuple[ str, int, int, str ] ]:
   try:
      tree = ast.parse( file_text )
   except SyntaxError:
      return []

   violations: list[ tuple[ str, int, int, str ] ] = []
   violations.extend( check_disallowed_collection_imports( path, tree ) )

   for node in ast.walk( tree ):
      if isinstance( node, ast.AnnAssign ):
         report_disallowed_homogeneous_collections( violations, path, node.annotation )
         continue

      if not isinstance( node, ( ast.FunctionDef, ast.AsyncFunctionDef ) ):
         continue

      all_arguments = [
         *node.args.posonlyargs,
         *node.args.args,
         *node.args.kwonlyargs,
      ]

      for arg in all_arguments:
         if arg.arg in { 'self', 'cls' }:
            continue

         if arg.annotation is None:
            add_violation(
               violations,
               path,
               arg.lineno or node.lineno,
               ( arg.col_offset or 0 ) + 1,
               f'Missing type annotation for argument "{ arg.arg }".' )
            continue

         if annotation_uses_disallowed_object( arg.annotation ):
            add_violation(
               violations,
               path,
               arg.lineno or node.lineno,
               ( arg.col_offset or 0 ) + 1,
               (
                  f'Do not use "object" as a type for "{ arg.arg }"; '
                  'use a concrete type (dict[str, object] is allowed for JSON payloads).' ) )

         report_disallowed_homogeneous_collections( violations, path, arg.annotation )

      if node.args.vararg is not None:
         if node.args.vararg.annotation is None:
            add_violation(
               violations,
               path,
               node.args.vararg.lineno or node.lineno,
               ( node.args.vararg.col_offset or 0 ) + 1,
               f'Missing type annotation for "*{ node.args.vararg.arg }".' )
         else:
            report_disallowed_homogeneous_collections(
               violations,
               path,
               node.args.vararg.annotation )

      if node.args.kwarg is not None:
         if node.args.kwarg.annotation is None:
            add_violation(
               violations,
               path,
               node.args.kwarg.lineno or node.lineno,
               ( node.args.kwarg.col_offset or 0 ) + 1,
               f'Missing type annotation for "**{ node.args.kwarg.arg }".' )
         else:
            report_disallowed_homogeneous_collections(
               violations,
               path,
               node.args.kwarg.annotation )

      if node.name == '__init__':
         if node.returns is None:
            add_violation(
               violations,
               path,
               node.lineno,
               1,
               'Missing return type annotation for "__init__" (use "-> None").' )
         elif annotation_uses_disallowed_object( node.returns ):
            add_violation(
               violations,
               path,
               node.returns.lineno or node.lineno,
               ( node.returns.col_offset or 0 ) + 1,
               (
                  f'Do not use "object" as the return type for "{ node.name }"; '
                  'use a concrete type (dict[str, object] is allowed for JSON payloads).' ) )
         report_disallowed_homogeneous_collections( violations, path, node.returns )
      elif node.returns is None:
         add_violation(
            violations,
            path,
            node.lineno,
            1,
            f'Missing return type annotation for "{ node.name }".' )
      else:
         if annotation_uses_disallowed_object( node.returns ):
            add_violation(
               violations,
               path,
               node.returns.lineno or node.lineno,
               ( node.returns.col_offset or 0 ) + 1,
               (
                  f'Do not use "object" as the return type for "{ node.name }"; '
                  'use a concrete type (dict[str, object] is allowed for JSON payloads).' ) )

         report_disallowed_homogeneous_collections( violations, path, node.returns )

   return violations


def check_method_spacing(
      path: Path,
      file_text: str,
      blank_lines_between_methods: int ) -> list[ tuple[ str, int, int, str ] ]:
   try:
      tree = ast.parse( file_text )
   except SyntaxError:
      return []

   lines = file_text.splitlines()
   violations: list[ tuple[ str, int, int, str ] ] = []

   for node in ast.walk( tree ):
      if not isinstance( node, ast.ClassDef ):
         continue

      methods = [
         item
         for item in node.body
         if isinstance( item, ( ast.FunctionDef, ast.AsyncFunctionDef ) )
      ]

      for previous, current in zip( methods, methods[ 1: ] ):
         previous_end_line = previous.end_lineno or previous.lineno
         current_start_line = get_definition_start_line( current )
         blank_line_count = 0

         for line_number in range( previous_end_line + 1, current_start_line ):
            if lines[ line_number - 1 ].strip() == '':
               blank_line_count += 1

         if blank_line_count == blank_lines_between_methods:
            continue

         add_violation(
            violations,
            path,
            current_start_line,
            1,
            (
               f'Expected { blank_lines_between_methods } blank lines between method '
               f'definitions, found { blank_line_count }.'
            )
         )

   return violations


def is_excluded_path( path: Path, excluded_patterns: list[ str ] ) -> bool:
   relative_path = path.relative_to( ROOT ).as_posix()

   if any( part in { '.git', '__pycache__', 'node_modules' } for part in path.parts ):
      return True

   for pattern in excluded_patterns:
      if fnmatch( relative_path, pattern ):
         return True

   return False


def get_significant_token(
      tokens: list[ tokenize.TokenInfo ],
      start_index: int,
      step: int ) -> tokenize.TokenInfo | None:
   index = start_index

   while 0 <= index < len( tokens ):
      token = tokens[ index ]

      if token.type not in SKIP_TOKEN_TYPES:
         return token

      index += step

   return None


def add_violation(
      violations: list[ tuple[ str, int, int, str ] ],
      path: Path,
      line: int,
      column: int,
      message: str ) -> None:
   violations.append( ( get_display_path( path ), line, column, message ) )


def build_char_positions(
      text: str,
      start: tuple[ int, int ] ) -> list[ tuple[ int, int ] ]:
   line, column = start
   positions: list[ tuple[ int, int ] ] = []

   for character in text:
      positions.append( ( line, column ) )

      if character == '\n':
         line += 1
         column = 0

      else:
         column += 1

   return positions


def check_opening_spacing(
      violations: list[ tuple[ str, int, int, str ] ],
      path: Path,
      positions: list[ tuple[ int, int ] ],
      text: str,
      index: int ) -> None:
   if index + 1 >= len( text ):
      return

   next_character = text[ index + 1 ]

   if next_character == OPENERS[ text[ index ] ] or next_character.isspace():
      return

   line, column = positions[ index ]
   add_violation(
      violations,
      path,
      line,
      column + 1,
      f'Missing space after "{ text[ index ] }".'
   )


def check_closing_spacing(
      violations: list[ tuple[ str, int, int, str ] ],
      path: Path,
      positions: list[ tuple[ int, int ] ],
      text: str,
      index: int ) -> None:
   if index == 0:
      return

   previous_character = text[ index - 1 ]

   if previous_character == CLOSERS[ text[ index ] ] or previous_character.isspace():
      return

   line, column = positions[ index ]
   add_violation(
      violations,
      path,
      line,
      column + 1,
      f'Missing space before "{ text[ index ] }".'
   )


def skip_string_literal( text: str, index: int ) -> int:
   quote_character = text[ index ]
   is_triple_quoted = text[ index:index + 3 ] == quote_character * 3

   if is_triple_quoted:
      index += 3

      while index < len( text ):
         if text[ index ] == '\\':
            index += 2
            continue

         if text[ index:index + 3 ] == quote_character * 3:
            return index + 3

         index += 1

      return len( text )

   index += 1

   while index < len( text ):
      if text[ index ] == '\\':
         index += 2
         continue

      if text[ index ] == quote_character:
         return index + 1

      index += 1

   return len( text )


def is_f_string_token( token_string: str ) -> bool:
   prefix = []
   index = 0

   while index < len( token_string ) and token_string[ index ].isalpha():
      prefix.append( token_string[ index ] )
      index += 1

   return 'f' in ''.join( prefix ).lower()


def check_f_string_field(
      violations: list[ tuple[ str, int, int, str ] ],
      path: Path,
      positions: list[ tuple[ int, int ] ],
      text: str,
      start_index: int ) -> int:
   stack = [ '{' ]
   index = start_index

   while index < len( text ):
      character = text[ index ]

      if character in { "'", '"' }:
         index = skip_string_literal( text, index )
         continue

      if character in OPENERS:
         check_opening_spacing( violations, path, positions, text, index )
         stack.append( character )
         index += 1
         continue

      if character in CLOSERS:
         check_closing_spacing( violations, path, positions, text, index )

         if stack and stack[ -1 ] == CLOSERS[ character ]:
            stack.pop()
            index += 1

            if not stack:
               return index

            continue

      index += 1

   return index


def check_f_string_token(
      path: Path,
      token: tokenize.TokenInfo ) -> list[ tuple[ str, int, int, str ] ]:
   if token.type != tokenize.STRING or not is_f_string_token( token.string ):
      return []

   positions = build_char_positions( token.string, token.start )
   violations: list[ tuple[ str, int, int, str ] ] = []
   index = 0

   while index < len( token.string ):
      if token.string[ index ] != '{':
         index += 1
         continue

      if index + 1 < len( token.string ) and token.string[ index + 1 ] == '{':
         index += 2
         continue

      check_opening_spacing( violations, path, positions, token.string, index )
      index = check_f_string_field( violations, path, positions, token.string, index + 1 )

   return violations


def check_file(
      path: Path,
      blank_lines_between_methods: int,
      enforce_typing: bool ) -> list[ tuple[ str, int, int, str ] ]:
   file_text = path.read_text()
   tokens = [
      token
      for token in tokenize.tokenize( BytesIO( file_text.encode() ).readline )
      if token.type != tokenize.ENDMARKER
   ]
   violations = check_method_spacing( path, file_text, blank_lines_between_methods )

   if enforce_typing:
      violations.extend( check_typing_annotations( path, file_text ) )

   for index, token in enumerate( tokens ):
      if token.type == tokenize.STRING:
         violations.extend( check_f_string_token( path, token ) )
         continue

      if token.type != tokenize.OP:
         continue

      if token.string in OPENERS:
         next_token = get_significant_token( tokens, index + 1, 1 )

         if next_token == None:
            continue

         if next_token.type == tokenize.OP and next_token.string == OPENERS[ token.string ]:
            continue

         if next_token.start[ 0 ] == token.end[ 0 ] and next_token.start[ 1 ] == token.end[ 1 ]:
            add_violation(
               violations,
               path,
               token.start[ 0 ],
               token.start[ 1 ] + 1,
               f'Missing space after "{ token.string }".'
            )

      elif token.string in CLOSERS:
         previous_token = get_significant_token( tokens, index - 1, -1 )

         if previous_token == None:
            continue

         if previous_token.type == tokenize.OP and previous_token.string == CLOSERS[ token.string ]:
            continue

         if previous_token.end[ 0 ] == token.start[ 0 ] and previous_token.end[ 1 ] == token.start[ 1 ]:
            add_violation(
               violations,
               path,
               token.start[ 0 ],
               token.start[ 1 ] + 1,
               f'Missing space before "{ token.string }".'
            )

   return violations


def main() -> int:
   style_config = load_style_config()
   excluded_patterns = style_config.get( 'exclude', [] )
   blank_lines_between_methods = style_config.get( 'blank_lines_between_methods', 2 )
   enforce_typing = style_config.get( 'enforce_typing', True )
   violations: list[ tuple[ str, int, int, str ] ] = []

   for path in sorted( ROOT.rglob( '*.py' ) ):
      if is_excluded_path( path, excluded_patterns ):
         continue

      violations.extend(
         check_file(
            path,
            blank_lines_between_methods,
            enforce_typing ) )

   if not violations:
      return 0

   for path, line, column, message in violations:
      print( f'{ path }:{ line }:{ column }: { message }' )

   print( f'\nFound { len( violations ) } Python house-style violation(s).' )

   return 1


if __name__ == '__main__':
   sys.exit( main() )
