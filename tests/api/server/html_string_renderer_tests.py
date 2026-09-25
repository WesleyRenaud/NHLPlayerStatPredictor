from __future__ import annotations

import pytest

from api.server.html_string_renderer import HtmlStringRenderer
from api.server.page_strings import PageStrings


def Test_Render_TestKnownToken_ExpectReplacedValue(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   heading = 'Stub Heading'
   template = '<h1>{{ page.heading }}</h1>'
   monkeypatch.setattr(
      PageStrings,
      'VALUES',
      { 'page.heading': heading } )

   rendered = HtmlStringRenderer.render( template )

   assert rendered == f'<h1>{ heading }</h1>'


def Test_Render_TestUnknownToken_ExpectUnchanged() -> None:
   token = '{{ page.missing }}'
   template = f'<h1>{ token }</h1>'

   rendered = HtmlStringRenderer.render( template )

   assert rendered == template


def Test_Render_TestHtmlInValue_ExpectEscaped(
      monkeypatch: pytest.MonkeyPatch ) -> None:
   heading = '<script>'
   escaped = '&lt;script&gt;'
   template = '{{ page.heading }}'
   monkeypatch.setattr(
      PageStrings,
      'VALUES',
      { 'page.heading': heading } )

   rendered = HtmlStringRenderer.render( template )

   assert rendered == escaped
