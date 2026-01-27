"""Main entry point for the Daily Engineering Intelligence pipeline."""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from .collector import Collector
from .curator import Curator
from .models import DailyRun, ItemStatus
from .notifier import send_notification
from .reader import Reader
from .renderer import Renderer
from .astro_renderer import AstroRenderer
from .synthesizer import Synthesizer, get_adapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Daily Engineering Intelligence Pipeline"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Run date (YYYY-MM-DD), defaults to today",
    )
    parser.add_argument(
        "--adapter",
        type=str,
        default="nollm",
        choices=["nollm", "cli", "gemini"],
        help="LLM adapter to use (default: nollm, use gemini for AI features)",
    )
    parser.add_argument(
        "--site-url",
        type=str,
        default="https://your-username.github.io/News_Automation",
        help="Base URL for the deployed site",
    )
    parser.add_argument(
        "--skip-notify",
        action="store_true",
        help="Skip Telegram notification",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Setup paths
    root_dir = Path(__file__).parent.parent
    config_dir = root_dir / "config"
    prompts_dir = root_dir / "prompts"
    docs_dir = root_dir / "docs"
    data_dir = root_dir / "data"
    daily_data_dir = data_dir / args.date

    # Ensure directories exist
    daily_data_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Initialize run tracking
    run = DailyRun(date=args.date, run_started=datetime.now())

    try:
        # ==========================================
        # Stage 1: Collection
        # ==========================================
        logger.info("=" * 50)
        logger.info("Stage 1: Collecting items")
        logger.info("=" * 50)

        collector = Collector(
            sources_path=config_dir / "sources.yaml",
            state_path=data_dir / "state.json",
        )

        items = collector.collect()
        run.items_discovered = len(items)

        # Save discovered items
        items_path = daily_data_dir / "items.json"
        items_path.write_text(
            json.dumps([item.model_dump() for item in items], indent=2, default=str),
            encoding="utf-8",
        )
        logger.info(f"Saved {len(items)} items to {items_path}")

        if not items:
            logger.warning("No new items discovered, exiting")
            return

        # ==========================================
        # Stage 2: Curation
        # ==========================================
        logger.info("=" * 50)
        logger.info("Stage 2: Curating items")
        logger.info("=" * 50)

        curator = Curator(config_path=config_dir / "curation.yaml")
        selected_items = curator.curate(items)
        run.items_selected = len(selected_items)

        # Mark selected
        for item in selected_items:
            item.status = ItemStatus.SELECTED

        # Save selected items
        selected_path = daily_data_dir / "selected.json"
        selected_path.write_text(
            json.dumps(
                [item.model_dump() for item in selected_items],
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        logger.info(f"Selected {len(selected_items)} items")

        if not selected_items:
            logger.warning("No items selected, exiting")
            return

        # ==========================================
        # Stage 3: Reading/Extraction
        # ==========================================
        logger.info("=" * 50)
        logger.info("Stage 3: Extracting article content")
        logger.info("=" * 50)

        reader = Reader(output_dir=daily_data_dir)
        articles = reader.extract_all(selected_items)

        run.items_extracted = sum(1 for a in articles if a.success)
        run.items_failed = sum(1 for a in articles if not a.success)

        logger.info(
            f"Extracted: {run.items_extracted} success, {run.items_failed} failed"
        )

        # ==========================================
        # Stage 4: Synthesis
        # ==========================================
        logger.info("=" * 50)
        logger.info("Stage 4: Synthesizing content")
        logger.info("=" * 50)

        adapter = get_adapter(args.adapter)
        synthesizer = Synthesizer(adapter=adapter, prompts_dir=prompts_dir)

        synthesis = synthesizer.synthesize(selected_items, articles)

        run.digest_generated = bool(synthesis.digest_md)
        run.blog_generated = bool(synthesis.blog_md)

        # Save synthesis
        digest_path = daily_data_dir / "digest.md"
        digest_path.write_text(synthesis.digest_md, encoding="utf-8")

        blog_path = daily_data_dir / "blog.md"
        blog_path.write_text(synthesis.blog_md, encoding="utf-8")

        logger.info("Synthesis complete")

        # ==========================================
        # Stage 5: Rendering
        # ==========================================
        logger.info("=" * 50)
        logger.info("Stage 5: Rendering MkDocs pages")
        logger.info("=" * 50)

        renderer = Renderer(docs_dir=docs_dir)

        # Render daily page
        renderer.render_daily_page(args.date, selected_items, articles, synthesis)

        # Update archive index
        existing_dates = renderer.get_existing_dates()
        if args.date not in existing_dates:
            existing_dates.append(args.date)
        renderer.update_archive_index(existing_dates)

        # Update home page
        renderer.update_home_page(args.date)

        run.pages_rendered = True
        logger.info("Pages rendered")

        # ==========================================
        # Stage 5b: Rendering Astro content
        # ==========================================
        logger.info("=" * 50)
        logger.info("Stage 5b: Rendering Astro content")
        logger.info("=" * 50)

        astro_dir = root_dir / "astro-site"
        if astro_dir.exists():
            # Use AI for translations if gemini adapter is selected
            use_ai = args.adapter == "gemini"
            astro_renderer = AstroRenderer(astro_dir=astro_dir, use_ai=use_ai)
            astro_renderer.render_articles(args.date, selected_items, articles, synthesis)
            astro_renderer.render_daily_summary(args.date, selected_items)
            logger.info("Astro content rendered")
        else:
            logger.warning("astro-site directory not found, skipping Astro rendering")

        # ==========================================
        # Stage 6: Notification
        # ==========================================
        if not args.skip_notify:
            logger.info("=" * 50)
            logger.info("Stage 6: Sending notification")
            logger.info("=" * 50)

            page_url = f"{args.site_url}/daily/{args.date}/"
            run.notification_sent = send_notification(
                date=args.date,
                items=selected_items,
                synthesis=synthesis,
                page_url=page_url,
            )

        # ==========================================
        # Finalize
        # ==========================================
        # Mark items as processed
        collector.mark_processed(selected_items)
        collector.save_state()

        run.run_completed = datetime.now()

        # Save run log
        run_log_path = daily_data_dir / "run.log"
        run_log_path.write_text(
            json.dumps(run.model_dump(), indent=2, default=str),
            encoding="utf-8",
        )

        logger.info("=" * 50)
        logger.info("Pipeline complete!")
        logger.info(f"  Discovered: {run.items_discovered}")
        logger.info(f"  Selected: {run.items_selected}")
        logger.info(f"  Extracted: {run.items_extracted}")
        logger.info(f"  Failed: {run.items_failed}")
        logger.info(f"  Pages: {run.pages_rendered}")
        logger.info(f"  Notified: {run.notification_sent}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        run.errors.append(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
