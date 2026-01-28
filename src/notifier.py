"""Notifier module - Sends notifications via Telegram."""

import logging
import os
from datetime import datetime
from typing import Optional

import requests

from .models import Item, Synthesis

logger = logging.getLogger(__name__)

# Telegram API base URL
TELEGRAM_API_BASE = "https://api.telegram.org/bot"


class TelegramNotifier:
    """Sends notifications via Telegram Bot API."""

    # Topic emoji mapping
    TOPIC_EMOJI = {
        "microsoft": "🔷",
        "data_platform": "📊",
        "analytics_engineering": "📈",
        "ai_agents": "🤖",
        "ai_llm": "🤖",
        "automation": "⚡",
        "github": "🐙",
    }

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token (or from TELEGRAM_BOT_TOKEN env)
            chat_id: Target chat ID (or from TELEGRAM_CHAT_ID env)
        """
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.bot_token and self.chat_id)

        if not self.enabled:
            logger.warning(
                "Telegram notifications disabled: "
                "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set"
            )

    def notify(
        self,
        date: str,
        items: list[Item],
        synthesis: Synthesis,
        page_url: str,
    ) -> bool:
        """
        Send notification about daily report.

        Args:
            date: Report date
            items: Curated items
            synthesis: Synthesized content
            page_url: URL to the daily page

        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            logger.info("Telegram notification skipped (not configured)")
            return False

        try:
            message = self._format_message(date, items, page_url)
            return self._send_message(message)
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            return False

    def _format_message(
        self,
        date: str,
        items: list[Item],
        page_url: str,
    ) -> str:
        """Format the notification message with clean, mobile-friendly layout."""
        # Parse and format date
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d/%m/%Y")
        except:
            formatted_date = date

        # Header
        lines = [
            "━━━━━━━━━━━━━━━━━━━━",
            f"📰 *DAILY INTEL*  •  {self._escape_md(formatted_date)}",
            "━━━━━━━━━━━━━━━━━━━━",
            "",
        ]

        # Group items by topic
        groups: dict[str, list[Item]] = {}
        for item in items:
            groups.setdefault(item.group, []).append(item)

        # Show headlines by topic
        for group_name, group_items in sorted(groups.items()):
            emoji = self.TOPIC_EMOJI.get(group_name, "📌")
            display_name = group_name.replace("_", " ").upper()
            
            lines.append(f"{emoji} *{display_name}*")
            
            # Show top 3 per topic
            for i, item in enumerate(group_items[:3], 1):
                title = self._escape_md(item.title[:55])
                if len(item.title) > 55:
                    title += "\\.\\.\\."
                lines.append(f"  {i}\\. [{title}]({item.url})")
            
            if len(group_items) > 3:
                lines.append(f"  _\\+{len(group_items) - 3} more_")
            
            lines.append("")

        # Footer
        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━",
            f"📖 [Xem đầy đủ tại website]({page_url})",
            "",
            f"📊 *{len(items)}* bài viết  •  *{len(groups)}* chủ đề",
            "━━━━━━━━━━━━━━━━━━━━",
        ])

        return "\n".join(lines)

    def _escape_md(self, text: str) -> str:
        """Escape special characters for Telegram MarkdownV2."""
        if not text:
            return ""
        # MarkdownV2 requires escaping these characters
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', 
                 '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f"\\{char}")
        return text

    def _send_message(self, text: str) -> bool:
        """Send message via Telegram API."""
        url = f"{TELEGRAM_API_BASE}{self.bot_token}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info("Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except requests.RequestException as e:
            logger.error(f"Telegram request failed: {e}")
            return False


def send_notification(
    date: str,
    items: list[Item],
    synthesis: Synthesis,
    page_url: str,
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> bool:
    """
    Convenience function to send Telegram notification.

    Args:
        date: Report date
        items: Curated items
        synthesis: Synthesized content
        page_url: URL to the daily page
        bot_token: Optional bot token override
        chat_id: Optional chat ID override

    Returns:
        True if notification sent
    """
    notifier = TelegramNotifier(bot_token, chat_id)
    return notifier.notify(date, items, synthesis, page_url)
