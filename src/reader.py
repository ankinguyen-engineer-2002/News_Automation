"""Reader module - Extracts full article content from URLs."""

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from .models import Article, Item, ItemStatus

logger = logging.getLogger(__name__)

# User agent for requests
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Request timeout in seconds
REQUEST_TIMEOUT = 30


class Reader:
    """Extracts full article content from URLs."""

    def __init__(self, output_dir: Path, timeout: int = REQUEST_TIMEOUT):
        """
        Initialize the reader.

        Args:
            output_dir: Directory to save extracted articles
            timeout: Request timeout in seconds
        """
        self.output_dir = output_dir
        self.timeout = timeout
        self.articles_dir = output_dir / "articles"
        self.articles_dir.mkdir(parents=True, exist_ok=True)

    def extract_all(self, items: list[Item]) -> list[Article]:
        """
        Extract content from all items.

        Args:
            items: List of items to extract

        Returns:
            List of Article objects with extraction results
        """
        articles: list[Article] = []

        for i, item in enumerate(items, 1):
            logger.info(f"Extracting [{i}/{len(items)}]: {item.title[:50]}...")

            article = self.extract(item)
            articles.append(article)

            # Update item status
            if article.success:
                item.status = ItemStatus.EXTRACTED
            else:
                item.status = ItemStatus.EXTRACT_FAILED

        # Summary
        success_count = sum(1 for a in articles if a.success)
        logger.info(
            f"Extraction complete: {success_count}/{len(articles)} successful"
        )

        return articles

    def extract(self, item: Item) -> Article:
        """
        Extract content from a single item.

        Args:
            item: Item to extract

        Returns:
            Article with extraction results
        """
        article = Article.from_item(item)

        try:
            # Fetch HTML
            html = self._fetch_html(item.url)
            if not html:
                article.error = "Failed to fetch HTML"
                return article

            # Extract main content
            content = self._extract_content(html, item.url)
            if not content:
                article.error = "Failed to extract content"
                return article

            # Convert to markdown
            markdown = self._to_markdown(content)
            if not markdown or len(markdown.strip()) < 100:
                article.error = "Extracted content too short"
                return article

            # Success
            article.extracted_text = markdown
            article.word_count = len(markdown.split())
            article.extracted_at = datetime.now(timezone.utc)
            article.success = True

            # Save to file
            self._save_article(article)

        except Exception as e:
            logger.error(f"Extraction error for {item.url}: {e}")
            article.error = str(e)

        return article

    def _fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL."""
        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=self.timeout,
                allow_redirects=True,
            )
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                logger.warning(f"Non-HTML content type: {content_type}")
                return None

            return response.text

        except requests.RequestException as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None

    def _extract_content(self, html: str, url: str) -> Optional[str]:
        """
        Extract main content from HTML.

        Uses readability-lxml as primary, BeautifulSoup as fallback.
        """
        # Try readability-lxml first
        try:
            from readability import Document

            doc = Document(html)
            content = doc.summary()

            if content and len(content) > 200:
                return content
        except Exception as e:
            logger.warning(f"Readability failed: {e}")

        # Fallback to BeautifulSoup heuristics
        try:
            soup = BeautifulSoup(html, "lxml")

            # Remove unwanted elements
            for tag in soup.find_all(
                ["script", "style", "nav", "header", "footer", "aside", "iframe"]
            ):
                tag.decompose()

            # Try common article containers
            content_selectors = [
                "article",
                '[role="main"]',
                ".post-content",
                ".article-content",
                ".entry-content",
                ".content",
                "main",
                "#content",
            ]

            for selector in content_selectors:
                element = soup.select_one(selector)
                if element and len(element.get_text(strip=True)) > 200:
                    return str(element)

            # Last resort: get body content
            body = soup.find("body")
            if body:
                return str(body)

        except Exception as e:
            logger.error(f"BeautifulSoup fallback failed: {e}")

        return None

    def _to_markdown(self, html: str) -> str:
        """Convert HTML to clean markdown."""
        try:
            # Use markdownify with sensible options
            markdown = md(
                html,
                heading_style="ATX",
                bullets="-",
                strip=["script", "style"],
            )

            # Clean up extra whitespace
            markdown = re.sub(r"\n{3,}", "\n\n", markdown)
            markdown = re.sub(r" +", " ", markdown)
            markdown = markdown.strip()

            return markdown

        except Exception as e:
            logger.error(f"Markdown conversion failed: {e}")
            return ""

    def _save_article(self, article: Article) -> None:
        """Save extracted article to disk."""
        # Save markdown content
        md_path = self.articles_dir / f"{article.slug}.md"
        md_path.write_text(article.extracted_text, encoding="utf-8")

        # Save metadata
        import json

        meta_path = self.articles_dir / f"{article.slug}.meta.json"
        meta = {
            "url": article.url,
            "title": article.title,
            "slug": article.slug,
            "word_count": article.word_count,
            "extracted_at": article.extracted_at.isoformat() if article.extracted_at else None,
            "success": article.success,
            "error": article.error,
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        logger.debug(f"Saved article: {md_path}")
