from __future__ import annotations

import pytest

from api.html_string_renderer import HtmlStringRenderer
from api.page_strings import PageStrings


def Test_Render_TestKnownToken_ExpectReplacedValue(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      PageStrings,
      'VALUES',
      { 'page.heading': 'Stub Heading' } )
   rendered = HtmlStringRenderer.render( '<h1>{{ page.heading }}</h1>' )
   assert rendered == '<h1>Stub Heading</h1>'


def Test_Render_TestUnknownToken_ExpectUnchanged() -> None:
   rendered = HtmlStringRenderer.render( '<h1>{{ page.missing }}</h1>' )
   assert rendered == '<h1>{{ page.missing }}</h1>'


def Test_Render_TestHtmlInValue_ExpectEscaped(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   monkeypatch.setattr(
      PageStrings,
      'VALUES',
      { 'page.heading': '<script>' } )
   assert HtmlStringRenderer.render( '{{ page.heading }}' ) == '&lt;script&gt;'
