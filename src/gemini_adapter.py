"""Gemini API adapter for LLM synthesis and translation."""

import logging
import os
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from .synthesizer import LLMAdapter
from .models import Article, Item

logger = logging.getLogger(__name__)


class GeminiAdapter(LLMAdapter):
    """
    Adapter using Google Gemini API for content generation.
    
    Features:
    - Article summarization
    - Vietnamese translation
    - Digest generation
    - Blog content generation
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        """
        Initialize Gemini adapter.
        
        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
            model: Model to use (default: gemini-2.0-flash for speed/cost)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        
    @property
    def name(self) -> str:
        return f"gemini:{self.model_name}"
    
    def synthesize(
        self,
        items: list[Item],
        articles: list[Article],
        prompt_template: str,
    ) -> str:
        """Generate synthesized content using Gemini."""
        from jinja2 import Template
        
        # Build context from articles
        context = self._build_context(items, articles)
        
        # Render prompt using Jinja2 (handles {% %} and {{ }} syntax)
        try:
            tmpl = Template(prompt_template)
            prompt = tmpl.render(**context)
        except Exception as e:
            logger.warning(f"Template rendering failed: {e}, using raw prompt")
            prompt = prompt_template
        
        # Add article context to prompt
        full_prompt = f"{prompt}\n\n## Articles to analyze:\n\n{context['article_summaries']}"
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"*Gemini synthesis failed: {e}*"
    
    def translate_to_vietnamese(self, text: str) -> str:
        """Translate text to Vietnamese."""
        prompt = f"""Translate the following English text to Vietnamese. 
Keep technical terms in English where appropriate.
Only output the translation, no explanations.

Text: {text}"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return ""
    
    def summarize_article(self, title: str, content: str, max_words: int = 150) -> str:
        """Generate a concise summary of an article."""
        prompt = f"""Summarize this article in {max_words} words or less.
Focus on key insights and practical takeaways for engineers.
Write in clear, professional English.

Title: {title}

Content:
{content[:5000]}"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return content[:500] + "..."
    
    def generate_article_detail(self, title: str, url: str, content: str) -> dict:
        """
        Generate detailed article content with summary and Vietnamese translation.
        
        Returns:
            dict with keys: summary_en, summary_vi, title_vi
        """
        # Generate English summary
        summary_en = self.summarize_article(title, content)
        
        # Translate to Vietnamese
        title_vi = self.translate_to_vietnamese(title)
        summary_vi = self.translate_to_vietnamese(summary_en)
        
        return {
            "summary_en": summary_en,
            "summary_vi": summary_vi,
            "title_vi": title_vi,
        }
    
    def _build_context(self, items: list[Item], articles: list[Article]) -> dict:
        """Build context for prompt templates."""
        from datetime import datetime
        
        article_map = {a.url: a for a in articles if a.success}
        
        summaries = []
        for item in items:
            article = article_map.get(item.url)
            content = article.extracted_text[:1500] if article else item.snippet
            
            summaries.append(f"""
### {item.title}
Source: {item.source} | Category: {item.group}
URL: {item.url}

{content}
""")
        
        # Get date from first item's published_at or use today's date
        date_str = ""
        if items and items[0].published_at:
            date_str = items[0].published_at.strftime("%Y-%m-%d")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        return {
            "article_summaries": "\n---\n".join(summaries),
            "article_count": len(items),
            "date": date_str,
        }


def get_gemini_adapter(api_key: Optional[str] = None) -> GeminiAdapter:
    """Factory function to get Gemini adapter."""
    return GeminiAdapter(api_key=api_key)
