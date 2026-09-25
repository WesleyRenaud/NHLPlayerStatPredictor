from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.shared.enums.shared_enum_values import SharedEnumValues


def Test_LoadIntegers_TestValidMembers_ExpectSortedDict(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   members = {
      'SECOND': 1,
      'FIRST': 0,
      'LAST': -1,
   }
   file_name = 'sample.json'
   ( tmp_path / file_name ).write_text(
      json.dumps( members ),
      encoding='utf-8' )
   monkeypatch.setattr(
      SharedEnumValues,
      'shared_enums_directory',
      staticmethod( lambda: tmp_path ) )

   loaded = SharedEnumValues.load_integers( file_name )

   assert loaded == dict( sorted( members.items() ) )


def Test_LoadIntegers_TestInvalidValue_ExpectValueError(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   file_name = 'bad-int.json'
   ( tmp_path / file_name ).write_text(
      json.dumps( { 'FIRST': '0' } ),
      encoding='utf-8' )
   monkeypatch.setattr(
      SharedEnumValues,
      'shared_enums_directory',
      staticmethod( lambda: tmp_path ) )

   with pytest.raises( ValueError, match='integer value' ):
      SharedEnumValues.load_integers( file_name )


def Test_LoadIntegers_TestEmptyObject_ExpectValueError(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   file_name = 'empty.json'
   ( tmp_path / file_name ).write_text( '{}\n', encoding='utf-8' )
   monkeypatch.setattr(
      SharedEnumValues,
      'shared_enums_directory',
      staticmethod( lambda: tmp_path ) )

   with pytest.raises( ValueError, match='non-empty object' ):
      SharedEnumValues.load_integers( file_name )


def Test_RepositoryRoot_TestFromModule_ExpectContainsSharedEnums() -> None:
   root = SharedEnumValues.repository_root()

   assert ( root / 'shared' / 'enums' / 'position.json' ).is_file()
   assert SharedEnumValues.shared_enums_directory() == root / 'shared' / 'enums'
