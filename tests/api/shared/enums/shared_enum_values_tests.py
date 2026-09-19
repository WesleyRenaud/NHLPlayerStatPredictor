from __future__ import annotations

from pathlib import Path

import pytest

from api.shared.enums.shared_enum_values import SharedEnumValues


def Test_LoadIntegers_TestValidMembers_ExpectSortedDict(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   ( tmp_path / 'sample.json' ).write_text(
      '{\n   "SECOND": 1,\n   "FIRST": 0,\n   "LAST": -1\n}\n',
      encoding='utf-8' )
   monkeypatch.setattr(
      SharedEnumValues,
      'shared_enums_directory',
      staticmethod( lambda: tmp_path ) )

   assert SharedEnumValues.load_integers( 'sample.json' ) == {
      'FIRST': 0,
      'LAST': -1,
      'SECOND': 1,
   }


def Test_LoadIntegers_TestInvalidValue_ExpectValueError(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   ( tmp_path / 'bad-int.json' ).write_text(
      '{ "FIRST": "0" }\n',
      encoding='utf-8' )
   monkeypatch.setattr(
      SharedEnumValues,
      'shared_enums_directory',
      staticmethod( lambda: tmp_path ) )

   with pytest.raises( ValueError, match='integer value' ):
      SharedEnumValues.load_integers( 'bad-int.json' )


def Test_LoadIntegers_TestEmptyObject_ExpectValueError(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch ) -> None:
   ( tmp_path / 'empty.json' ).write_text( '{}\n', encoding='utf-8' )
   monkeypatch.setattr(
      SharedEnumValues,
      'shared_enums_directory',
      staticmethod( lambda: tmp_path ) )

   with pytest.raises( ValueError, match='non-empty object' ):
      SharedEnumValues.load_integers( 'empty.json' )


def Test_RepositoryRoot_TestFromModule_ExpectContainsSharedEnums() -> None:
   root = SharedEnumValues.repository_root()

   assert ( root / 'shared' / 'enums' / 'position.json' ).is_file()
   assert SharedEnumValues.shared_enums_directory() == root / 'shared' / 'enums'
