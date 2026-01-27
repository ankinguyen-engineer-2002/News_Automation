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
        """Render the daily page content with modern styling."""
        # Group badge mapping
        group_badges = {
            "microsoft": "badge--microsoft",
            "data_platform": "badge--data-platform",
            "analytics_engineering": "badge--analytics",
            "ai_agents": "badge--ai",
            "ai_llm": "badge--ai",
            "automation": "badge--automation",
            "github": "badge--github",
        }
        
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
        
        lines = [
            "---",
            f"title: Daily Intelligence - {date}",
            f"description: {total_items} curated articles for {date}",
            "---",
            "",
            f'<div class="hero-section" style="padding: 2rem;">',
            f'  <div class="status-badge">',
            f'    <span class="status-badge__dot"></span>',
            f'    {total_items} articles curated',
            f'  </div>',
            f'  <h1 class="hero-title" style="font-size: 2.5rem;">Daily Engineering Intelligence</h1>',
            f'  <p class="hero-subtitle" style="font-size: 1.1rem;">{date}</p>',
            f'  <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center; margin-top: 1rem;">',
        ]
        
        # Add group badges
        for group_name in sorted(groups.keys()):
            badge_class = group_badges.get(group_name, "badge--ai")
            icon = group_icons.get(group_name, "📰")
            lines.append(f'    <span class="badge {badge_class}">{icon} {self._format_group_name(group_name)}</span>')
        
        lines.extend([
            f'  </div>',
            f'</div>',
            "",
            '<div class="section-header">',
            '  <span class="section-header__icon">📋</span>',
            '  <span class="section-header__title">Quick Digest</span>',
            '  <span class="section-header__line"></span>',
            '</div>',
            "",
            '<div class="card" style="margin-bottom: 2rem;">',
            "",
            synthesis.digest_md,
            "",
            '</div>',
            "",
            '<div class="section-header">',
            '  <span class="section-header__icon">📰</span>',
            '  <span class="section-header__title">Today\'s Highlights</span>',
            '  <span class="section-header__line"></span>',
            '</div>',
            "",
        ])

        # Add items by group with cards
        for group_name, entries in sorted(groups.items()):
            icon = group_icons.get(group_name, "📰")
            badge_class = group_badges.get(group_name, "badge--ai")
            
            lines.append(f"### {icon} {self._format_group_name(group_name)}")
            lines.append("")
            lines.append('<div class="bento-grid">')

            for entry in entries:
                item = entry["item"]
                article = entry["article"]

                lines.append('<div class="card">')
                lines.append(f'<span class="badge {badge_class}" style="margin-bottom: 0.75rem;">{item.source}</span>')
                lines.append(f'<div class="card__title"><a href="{item.url}" target="_blank">{item.title}</a></div>')

                if entry["has_content"] and article:
                    summary = self._extract_summary(article.extracted_text)
                    lines.append(f'<div class="card__description">{summary}</div>')
                else:
                    lines.append(f'<div class="card__description">{item.snippet}</div>')
                    if not entry["has_content"]:
                        lines.append('<p style="font-size: 0.75rem; color: var(--dei-warning); margin-top: 0.5rem;">⚠️ Full content not available</p>')

                lines.append('</div>')

            lines.append('</div>')
            lines.append("")

        # Add deep analysis section
        lines.extend([
            '<div class="section-header">',
            '  <span class="section-header__icon">🔍</span>',
            '  <span class="section-header__title">Deep Analysis</span>',
            '  <span class="section-header__line"></span>',
            '</div>',
            "",
            '<div class="card card--featured" style="margin-bottom: 2rem;">',
            "",
            synthesis.blog_md,
            "",
            '</div>',
            "",
            '<div class="section-header">',
            '  <span class="section-header__icon">📚</span>',
            '  <span class="section-header__title">Sources</span>',
            '  <span class="section-header__line"></span>',
            '</div>',
            "",
        ])

        # Add sources by group
        for group_name, entries in sorted(groups.items()):
            icon = group_icons.get(group_name, "📰")
            lines.append(f"**{icon} {self._format_group_name(group_name)}**")
            lines.append("")
            for entry in entries:
                item = entry["item"]
                lines.append(f"- [{item.title}]({item.url}) - *{item.source}*")
            lines.append("")

        # Footer
        lines.extend([
            "---",
            "",
            '<div style="text-align: center; padding: 1rem;">',
            '  <a href="../" class="action-btn action-btn--secondary">← Back to Home</a>',
            '  <a href="./" class="action-btn action-btn--secondary">📚 Browse Archive</a>',
            '</div>',
        ])

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

        Note: This is now handled by the static index.md file.
        This method is kept for compatibility but does minimal updates.

        Args:
            latest_date: Date of latest report

        Returns:
            Path to home page
        """
        home_path = self.docs_dir / "index.md"
        
        # Read existing content and update the latest date link
        if home_path.exists():
            content = home_path.read_text(encoding="utf-8")
            # Update the href link to latest report
            content = re.sub(
                r'href="daily/\d{4}-\d{2}-\d{2}/"',
                f'href="daily/{latest_date}/"',
                content
            )
            content = re.sub(
                r'January \d+, \d{4}',
                datetime.strptime(latest_date, "%Y-%m-%d").strftime("%B %d, %Y"),
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
