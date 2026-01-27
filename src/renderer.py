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
        """Render the daily page content - clean and minimal."""
        # Group icons
        group_icons = {
            "microsoft": "🔷",
            "data_platform": "🔶",
            "analytics_engineering": "🟢",
            "ai_agents": "🟣",
            "ai_llm": "🟣",
            "automation": "🔴",
            "github": "⚪",
        }

        total_items = sum(len(entries) for entries in groups.values())
        date_formatted = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
        
        lines = [
            f"# {date_formatted}",
            "",
            f"> **{total_items}** articles curated from **{len(groups)}** categories",
            "",
            "---",
            "",
            "## Overview",
            "",
        ]
        
        # Quick summary - just list categories with counts
        for group_name in sorted(groups.keys()):
            icon = group_icons.get(group_name, "📰")
            count = len(groups[group_name])
            formatted_name = self._format_group_name(group_name)
            lines.append(f"- {icon} **{formatted_name}** — {count} article{'s' if count > 1 else ''}")
        
        lines.extend([
            "",
            "---",
            "",
        ])

        # Articles by category
        for group_name, entries in sorted(groups.items()):
            icon = group_icons.get(group_name, "📰")
            formatted_name = self._format_group_name(group_name)
            
            lines.append(f"## {icon} {formatted_name}")
            lines.append("")

            for entry in entries:
                item = entry["item"]
                article = entry["article"]
                
                # Article title as h3
                lines.append(f"### [{item.title}]({item.url})")
                lines.append(f"*{item.source}*")
                lines.append("")

                # Content - prioritize extracted, fallback to snippet
                if entry["has_content"] and article:
                    summary = self._extract_summary(article.extracted_text, max_length=400)
                    lines.append(f"> {summary}")
                else:
                    lines.append(f"> {item.snippet}")
                
                lines.append("")

        # Sources section at the end
        lines.extend([
            "---",
            "",
            "## 📚 All Sources",
            "",
        ])
        
        for group_name, entries in sorted(groups.items()):
            icon = group_icons.get(group_name, "📰")
            lines.append(f"**{icon} {self._format_group_name(group_name)}**")
            lines.append("")
            for entry in entries:
                item = entry["item"]
                lines.append(f"- [{item.title}]({item.url})")
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
            if para.startswith(("*", "-", "|", "[", "!")):
                continue
            # Clean up the paragraph
            para = para.replace("\n", " ").strip()
            if len(para) > max_length:
                return para[:max_length].rsplit(" ", 1)[0] + "..."
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
            "# Archive",
            "",
            "> Browse past daily intelligence reports",
            "",
            "---",
            "",
        ]

        # Group by month
        current_month = None
        for date in sorted(dates, reverse=True):
            dt = datetime.strptime(date, "%Y-%m-%d")
            month_key = dt.strftime("%B %Y")
            
            if month_key != current_month:
                if current_month is not None:
                    lines.append("")
                lines.append(f"## {month_key}")
                lines.append("")
                current_month = month_key
            
            day_formatted = dt.strftime("%d %a")
            lines.append(f"- [{day_formatted}]({date}.md)")

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
        
        # Read existing content and update the latest date link
        if home_path.exists():
            content = home_path.read_text(encoding="utf-8")
            # Update date references
            content = re.sub(
                r'daily/\d{4}-\d{2}-\d{2}/',
                f'daily/{latest_date}/',
                content
            )
            # Update formatted date
            new_date_formatted = datetime.strptime(latest_date, "%Y-%m-%d").strftime("%B %d, %Y")
            content = re.sub(
                r'[A-Z][a-z]+ \d{1,2}, \d{4}',
                new_date_formatted,
                content
            )
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
