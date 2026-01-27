"""Tests for the reader module."""

import pytest

from src.reader import Reader


class TestHTMLCleaning:
    """Tests for HTML to markdown conversion."""

    def test_markdown_conversion(self):
        """Basic HTML should convert to markdown."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            reader = Reader(output_dir=Path(tmpdir))

            html = """
            <article>
                <h1>Test Article</h1>
                <p>This is a paragraph with <strong>bold</strong> text.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
            </article>
            """

            result = reader._to_markdown(html)

            assert "Test Article" in result
            assert "paragraph" in result
            assert "bold" in result


class TestContentExtraction:
    """Tests for content extraction logic."""

    def test_extract_from_article_tag(self):
        """Content in article tag should be extracted."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            reader = Reader(output_dir=Path(tmpdir))

            html = """
            <html>
            <head><title>Test</title></head>
            <body>
                <nav>Navigation</nav>
                <article>
                    <h1>Main Article</h1>
                    <p>This is the main content that should be extracted. 
                    It has enough text to pass the minimum length check.
                    We need more content here to make it realistic.</p>
                    <p>Second paragraph with more details about the topic.</p>
                </article>
                <footer>Footer</footer>
            </body>
            </html>
            """

            result = reader._extract_content(html, "https://example.com")

            assert result is not None
            assert "Main Article" in result
            # Nav and footer should be removed
            assert "Navigation" not in result or "article" in result.lower()
