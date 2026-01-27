# News Sources

This page lists the configured news sources for Daily Engineering Intelligence.

## How Sources Work

Sources are configured in `config/sources.yaml`. Each source has:

- **Name**: Display name
- **Type**: `rss`, `api`, or `scrape`
- **URL**: Feed URL or endpoint
- **Tags**: Topic keywords for classification
- **Priority**: 1-10 ranking (higher = more important)

## Current Sources

### Microsoft

| Source | Type | Priority |
|--------|------|----------|
| Power BI Blog | RSS | 1 |
| Microsoft Azure Blog | RSS | 2 |
| Microsoft Data Platform Blog | RSS | 1 |

### Data Platform

| Source | Type | Priority |
|--------|------|----------|
| Databricks Blog | RSS | 1 |
| Snowflake Blog | RSS | 1 |
| dbt Labs Blog | RSS | 1 |

### Analytics Engineering

| Source | Type | Priority |
|--------|------|----------|
| Apache Airflow Blog | RSS | 2 |
| Dagster Blog | RSS | 2 |
| Prefect Blog | RSS | 2 |

### AI / LLM

| Source | Type | Priority |
|--------|------|----------|
| OpenAI Blog | RSS | 1 |
| Anthropic Blog | RSS | 1 |
| Google AI Blog | RSS | 1 |
| Hugging Face Blog | RSS | 2 |

### Automation

| Source | Type | Priority |
|--------|------|----------|
| n8n Blog | RSS | 2 |
| Temporal Blog | RSS | 2 |

### GitHub

| Source | Type | Priority |
|--------|------|----------|
| GitHub Blog | RSS | 2 |
| GitHub Changelog | RSS | 3 |

## Adding New Sources

Edit `config/sources.yaml` to add new sources:

```yaml
groups:
  your_group:
    - name: "Source Name"
      type: rss
      url: "https://example.com/feed.xml"
      tags: [tag1, tag2]
      priority: 1
```
