"""Synthesizer module - Generates digest and blog content using LLM adapters."""

import logging
import re
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from jinja2 import Template

from .models import Article, Citation, Item, ItemStatus, Synthesis

logger = logging.getLogger(__name__)


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters."""

    @abstractmethod
    def synthesize(
        self,
        items: list[Item],
        articles: list[Article],
        prompt_template: str,
    ) -> str:
        """
        Generate synthesized content.

        Args:
            items: List of curated items
            articles: List of extracted articles
            prompt_template: Template for the prompt

        Returns:
            Generated content as markdown string
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return adapter name."""
        pass


class NoLLMAdapter(LLMAdapter):
    """
    Rule-based adapter that generates content without LLM.

    Uses templates to create structured output from item data.
    Always available, no API costs.
    """

    @property
    def name(self) -> str:
        return "nollm"

    def synthesize(
        self,
        items: list[Item],
        articles: list[Article],
        prompt_template: str,
    ) -> str:
        """Generate content using templates."""
        # Ignore prompt_template - use built-in templates
        return self._generate_from_template(items, articles)

    def _generate_from_template(
        self,
        items: list[Item],
        articles: list[Article],
    ) -> str:
        """Generate structured content from templates."""
        # Create article lookup
        article_map = {a.url: a for a in articles if a.success}

        # Group items by group
        groups: dict[str, list[Item]] = {}
        for item in items:
            groups.setdefault(item.group, []).append(item)

        lines = []

        for group_name, group_items in sorted(groups.items()):
            lines.append(f"## {self._format_group_name(group_name)}")
            lines.append("")

            for item in group_items:
                article = article_map.get(item.url)

                lines.append(f"### [{item.title}]({item.url})")
                lines.append(f"*Source: {item.source}*")
                lines.append("")

                if item.status == ItemStatus.EXTRACT_FAILED:
                    # Extraction failed - use snippet only
                    lines.append(f"> {item.snippet}")
                    lines.append("")
                    lines.append("*⚠️ Full content extraction failed*")
                elif article and article.extracted_text:
                    # Use first paragraph of extracted content
                    summary = self._extract_summary(article.extracted_text)
                    lines.append(summary)
                else:
                    # Use snippet
                    lines.append(f"> {item.snippet}")

                lines.append("")

        return "\n".join(lines)

    def _format_group_name(self, name: str) -> str:
        """Format group name for display."""
        return name.replace("_", " ").title()

    def _extract_summary(self, text: str, max_length: int = 500) -> str:
        """Extract a summary from extracted text."""
        # Remove markdown headers
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)

        # Get first meaningful paragraph
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for para in paragraphs:
            # Skip very short paragraphs
            if len(para) < 50:
                continue
            # Skip if it looks like navigation/metadata
            if para.startswith(("*", "-", "|", "[")):
                continue

            if len(para) > max_length:
                return para[:max_length] + "..."
            return para

        # Fallback
        return text[:max_length] + "..." if len(text) > max_length else text


class CLIAdapter(LLMAdapter):
    """
    Adapter that invokes an external CLI command for LLM synthesis.

    Supports: Gemini CLI, Claude CLI, Codex CLI, etc.
    """

    def __init__(self, command: Optional[str] = None):
        """
        Initialize CLI adapter.

        Args:
            command: CLI command to invoke (e.g., "gemini", "claude")
                    If None, reads from LLM_CLI_COMMAND env var
        """
        import os

        self.command = command or os.environ.get("LLM_CLI_COMMAND", "gemini")

    @property
    def name(self) -> str:
        return f"cli:{self.command}"

    def synthesize(
        self,
        items: list[Item],
        articles: list[Article],
        prompt_template: str,
    ) -> str:
        """Generate content by invoking CLI."""
        # Prepare input context
        context = self._prepare_context(items, articles)

        # Render prompt
        prompt = self._render_prompt(prompt_template, context)

        # Invoke CLI
        try:
            result = subprocess.run(
                [self.command, prompt],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"CLI error: {result.stderr}")
                return f"*CLI synthesis failed: {result.stderr}*"

            return result.stdout.strip()

        except FileNotFoundError:
            logger.error(f"CLI command not found: {self.command}")
            return f"*CLI command not found: {self.command}*"
        except subprocess.TimeoutExpired:
            logger.error("CLI command timed out")
            return "*CLI synthesis timed out*"
        except Exception as e:
            logger.error(f"CLI error: {e}")
            return f"*CLI synthesis failed: {e}*"

    def _prepare_context(
        self,
        items: list[Item],
        articles: list[Article],
    ) -> dict:
        """Prepare context for prompt template."""
        article_map = {a.url: a for a in articles if a.success}

        article_contents = []
        for item in items:
            article = article_map.get(item.url)
            article_contents.append({
                "title": item.title,
                "url": item.url,
                "source": item.source,
                "group": item.group,
                "snippet": item.snippet,
                "content": article.extracted_text[:2000] if article else "",
                "extracted": bool(article and article.success),
            })

        return {
            "articles": article_contents,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "item_count": len(items),
        }

    def _render_prompt(self, template: str, context: dict) -> str:
        """Render prompt template with context."""
        try:
            tmpl = Template(template)
            return tmpl.render(**context)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            # Return plain template if rendering fails
            return template


class Synthesizer:
    """Main synthesizer that coordinates LLM adapters."""

    def __init__(
        self,
        adapter: LLMAdapter,
        prompts_dir: Path,
    ):
        """
        Initialize synthesizer.

        Args:
            adapter: LLM adapter to use
            prompts_dir: Directory containing prompt templates
        """
        self.adapter = adapter
        self.prompts_dir = prompts_dir

    def synthesize(
        self,
        items: list[Item],
        articles: list[Article],
    ) -> Synthesis:
        """
        Generate digest and blog from items and articles.

        Args:
            items: Curated items
            articles: Extracted articles

        Returns:
            Synthesis object with generated content
        """
        logger.info(f"Synthesizing with adapter: {self.adapter.name}")

        # Load prompts
        digest_prompt = self._load_prompt("digest_prompt.md")
        blog_prompt = self._load_prompt("blog_prompt.md")

        # Generate digest (short summary)
        logger.info("Generating digest...")
        digest_md = self.adapter.synthesize(items, articles, digest_prompt)

        # Generate blog (deep analysis)
        logger.info("Generating blog...")
        blog_md = self.adapter.synthesize(items, articles, blog_prompt)

        # Build citations
        citations = [
            Citation(
                url=item.url,
                title=item.title,
                source=item.source,
                group=item.group,
            )
            for item in items
        ]

        return Synthesis(
            digest_md=digest_md,
            blog_md=blog_md,
            citations=citations,
            generated_at=datetime.now(timezone.utc),
            adapter_used=self.adapter.name,
        )

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt template from file."""
        prompt_path = self.prompts_dir / filename

        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")

        logger.warning(f"Prompt template not found: {prompt_path}")
        return ""


def get_adapter(adapter_name: str) -> LLMAdapter:
    """
    Get an LLM adapter by name.

    Args:
        adapter_name: Name of adapter ("nollm", "cli", "gemini")

    Returns:
        LLM adapter instance
    """
    if adapter_name.lower() == "nollm":
        return NoLLMAdapter()
    elif adapter_name.lower() == "cli":
        return CLIAdapter()
    elif adapter_name.lower() == "gemini":
        try:
            from .gemini_adapter import GeminiAdapter
            return GeminiAdapter()
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini adapter: {e}, using NoLLM")
            return NoLLMAdapter()
    else:
        logger.warning(f"Unknown adapter: {adapter_name}, using NoLLM")
        return NoLLMAdapter()
