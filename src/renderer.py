"""Renderer module - Generates MkDocs pages from synthesized content."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Template

from .models import Article, Citation, Item, Synthesis

logger = logging.getLogger(__name__)


class Renderer:
    """Renders MkDocs pages from synthesized content."""

    def __init__(self, docs_dir: Path):
        """
        Initialize renderer.

        Args:
            docs_dir: Path to docs directory (MkDocs source)
        """
        self.docs_dir = docs_dir
        self.daily_dir = docs_dir / "daily"
        self.daily_dir.mkdir(parents=True, exist_ok=True)

    def render_daily_page(
        self,
        date: str,
        items: list[Item],
        articles: list[Article],
        synthesis: Synthesis,
    ) -> Path:
        """
        Render the daily page.

        Args:
            date: Date string (YYYY-MM-DD)
            items: Curated items
            articles: Extracted articles
            synthesis: Synthesized content

        Returns:
            Path to generated page
        """
        page_path = self.daily_dir / f"{date}.md"

        # Build article lookup
        article_map = {a.url: a for a in articles}

        # Group items and citations by group
        groups = self._group_items(items, article_map)

        # Render page content
        content = self._render_daily_content(date, groups, synthesis)

        # Write page
        page_path.write_text(content, encoding="utf-8")
        logger.info(f"Rendered daily page: {page_path}")

        return page_path

    def _group_items(
        self,
        items: list[Item],
        article_map: dict[str, Article],
    ) -> dict[str, list[dict]]:
        """Group items by their group name with article data."""
        groups: dict[str, list[dict]] = {}

        for item in items:
            article = article_map.get(item.url)
            entry = {
                "item": item,
                "article": article,
                "has_content": bool(article and article.success),
            }
            groups.setdefault(item.group, []).append(entry)

        return groups

    def _render_daily_content(
        self,
        date: str,
        groups: dict[str, list[dict]],
        synthesis: Synthesis,
    ) -> str:
        """Render the daily page content."""
        lines = [
            f"# Daily Engineering Intelligence - {date}",
            "",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*",
            "",
            "---",
            "",
            "## 📋 Quick Digest",
            "",
            synthesis.digest_md,
            "",
            "---",
            "",
            "## 📰 Today's Highlights",
            "",
        ]

        # Add items by group
        for group_name, entries in sorted(groups.items()):
            lines.append(f"### {self._format_group_name(group_name)}")
            lines.append("")

            for entry in entries:
                item = entry["item"]
                article = entry["article"]

                lines.append(f"#### [{item.title}]({item.url})")
                lines.append(f"*{item.source}*")
                lines.append("")

                if entry["has_content"] and article:
                    # Show summary from extracted content
                    summary = self._extract_summary(article.extracted_text)
                    lines.append(summary)
                else:
                    # Show snippet only
                    lines.append(f"> {item.snippet}")
                    if not entry["has_content"]:
                        lines.append("")
                        lines.append("*⚠️ Full content not available*")

                lines.append("")

        # Add deep analysis section
        lines.extend([
            "---",
            "",
            "## 🔍 Deep Analysis",
            "",
            synthesis.blog_md,
            "",
            "---",
            "",
            "## 📚 Sources",
            "",
        ])

        # Add sources by group
        for group_name, entries in sorted(groups.items()):
            lines.append(f"### {self._format_group_name(group_name)}")
            lines.append("")
            for entry in entries:
                item = entry["item"]
                lines.append(f"- [{item.title}]({item.url}) - *{item.source}*")
            lines.append("")

        return "\n".join(lines)

    def _format_group_name(self, name: str) -> str:
        """Format group name for display."""
        return name.replace("_", " ").title()

    def _extract_summary(self, text: str, max_length: int = 300) -> str:
        """Extract a summary from extracted text."""
        # Remove markdown headers
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)

        # Get first meaningful paragraph
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for para in paragraphs:
            if len(para) < 50:
                continue
            if para.startswith(("*", "-", "|", "[")):
                continue

            if len(para) > max_length:
                return para[:max_length] + "..."
            return para

        return text[:max_length] + "..." if len(text) > max_length else text

    def update_archive_index(self, dates: list[str]) -> Path:
        """
        Update the archive index page.

        Args:
            dates: List of dates with pages (YYYY-MM-DD)

        Returns:
            Path to index page
        """
        index_path = self.daily_dir / "index.md"

        lines = [
            "# Daily Intelligence Archive",
            "",
            "Browse past daily intelligence reports.",
            "",
            "## Recent Reports",
            "",
        ]

        # Sort dates descending (newest first)
        for date in sorted(dates, reverse=True):
            lines.append(f"- [{date}]({date}.md)")

        lines.append("")

        index_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"Updated archive index: {index_path}")

        return index_path

    def update_home_page(self, latest_date: str) -> Path:
        """
        Update the home page with link to latest.

        Args:
            latest_date: Date of latest report

        Returns:
            Path to home page
        """
        home_path = self.docs_dir / "index.md"

        content = f"""# Daily Engineering Intelligence

Welcome to your daily curated engineering intelligence feed.

## Latest Report

📅 **[{latest_date}](daily/{latest_date}.md)** - View today's report

## Topics Covered

- **Microsoft Data/Analytics**: Power BI, Fabric, Azure Data, Power Platform
- **Data Platform**: Databricks, Snowflake, BigQuery, Lakehouse
- **Analytics Engineering**: dbt, Airflow, Dagster, Prefect
- **AI/LLM/Agents**: Model releases, agent frameworks, MCP ecosystem
- **Automation**: n8n, Temporal, CI/CD

## Browse Archive

📚 [View all daily reports](daily/index.md)

---

*Updated automatically via GitHub Actions*
"""

        home_path.write_text(content, encoding="utf-8")
        logger.info(f"Updated home page: {home_path}")

        return home_path

    def get_existing_dates(self) -> list[str]:
        """Get list of existing daily page dates."""
        dates = []

        for path in self.daily_dir.glob("????-??-??.md"):
            date = path.stem
            if re.match(r"^\d{4}-\d{2}-\d{2}$", date):
                dates.append(date)

        return sorted(dates)
