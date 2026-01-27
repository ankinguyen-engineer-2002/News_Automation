# Daily Engineering Intelligence

A cloud-only daily news research + deep synthesis pipeline that publishes to GitHub Pages using MkDocs Material, with Telegram notifications.

## Features

- 🔍 **Automated Discovery**: Fetches news from RSS feeds, APIs, and web scraping
- 🎯 **Smart Curation**: Filters and prioritizes content by keywords and groups
- 📖 **Content Extraction**: Extracts full article text using readability algorithms
- 🧠 **AI Synthesis**: Generates daily digests and deep blog posts (pluggable LLM adapters)
- 📄 **Beautiful Output**: MkDocs Material site with dark theme
- 🚀 **Cloud Deployment**: GitHub Actions + GitHub Pages (no local machine needed)
- 📢 **Notifications**: Telegram bot integration

## Quick Start

### Prerequisites

- Python 3.11+
- GitHub account with Pages enabled
- (Optional) Telegram Bot token

### Local Development

```bash
# Clone and install
git clone https://github.com/YOUR_USERNAME/News_Automation.git
cd News_Automation
pip install -r requirements.txt

# Run pipeline
python -m src.main --date $(date +%Y-%m-%d)

# Preview site
mkdocs serve
```

### GitHub Actions Setup

1. Enable GitHub Pages in repository settings (source: GitHub Actions)
2. Add secrets (Settings → Secrets → Actions):
   - `TELEGRAM_BOT_TOKEN` (optional)
   - `TELEGRAM_CHAT_ID` (optional)

The workflow runs daily at 6 AM UTC automatically.

## Configuration

### Adding Sources

Edit `config/sources.yaml`:

```yaml
groups:
  microsoft:
    - name: "Power BI Blog"
      type: rss
      url: "https://powerbi.microsoft.com/en-us/blog/feed/"
      tags: [powerbi, microsoft]
      priority: 1
```

### Curation Rules

Edit `config/curation.yaml`:

```yaml
top_per_group: 5
allowlist:
  - "power bi"
  - "fabric"
  - "dbt"
denylist:
  - "sponsored"
```

### LLM Adapters

- `nollm`: Rule-based templates (default, always free)
- `cli`: External CLI command (Gemini CLI, Claude, Codex)

```bash
# Use NoLLM adapter (default)
python -m src.main --date 2026-01-27 --adapter nollm

# Use CLI adapter
LLM_CLI_COMMAND="gemini" python -m src.main --date 2026-01-27 --adapter cli
```

## Project Structure

```
├── src/                    # Pipeline modules
│   ├── main.py            # Entry point
│   ├── collector.py       # RSS/API fetching
│   ├── curator.py         # Content filtering
│   ├── reader.py          # Article extraction
│   ├── synthesizer.py     # LLM adapters & synthesis
│   ├── renderer.py        # MkDocs page generation
│   ├── notifier.py        # Telegram notifications
│   └── models.py          # Pydantic schemas
├── config/                # Configuration files
├── prompts/               # LLM prompt templates
├── docs/                  # MkDocs source files
├── data/                  # Generated artifacts
└── tests/                 # Unit tests
```

## Topics Covered

- **Microsoft**: Power BI, Fabric, Azure Data, Power Platform
- **Data Platform**: Databricks, Snowflake, BigQuery, Lakehouse
- **Analytics Engineering**: dbt, Airflow, Dagster, Prefect
- **AI/LLM**: Model releases, agent frameworks, MCP ecosystem
- **Automation**: n8n, Temporal, CI/CD
- **GitHub**: Trending repos, releases

## License

MIT
