---
title: "How Sweetgreen transformed unstructured data into conversational analytics with dbt and AI"
title_vi: ""
source: "dbt Labs Blog"
url: "https://www.getdbt.com/blog/sweetgreen-conversational-analytics-dbt-ai"
topic: "data-platform"
date: "2026-01-28"
excerpt: "Data is supposed to settle debates. But at Sweetgreen, a popular restaurant chain, it would sometimes start them. Stakeholders either didn’t have access to the right insights, or they ran into..."
excerpt_vi: ""
number: 9
publishDate: "2026-01-28T00:00:00Z"
---

Data is supposed to settle debates. But at Sweetgreen, a popular restaurant chain, it would sometimes start them. Stakeholders either didn’t have access to the right insights, or they ran into inconsistencies.

As Sweetgreen looked toward self-serve AI-powered analysis, the need for a consistent foundation became a high priority. They underwent a massive data transformation using dbt to standardize the business logic behind its reporting. By redesigning its data models around the core actions of its business, Sweetgreen created a single source of truth with consistent metric definitions, automated tests, and documentation that made data easier to trust and use.

Today, Sweetgreen’s business teams can leverage conversational AI to self-serve data insights by asking questions in plain English and getting consistent, reliable answers. In just one year, trust in the data has grown, and teams are making faster and more confident decisions.

Let’s take a look at how Sweetgreen did it.

### A persistent data bottleneck

Before implementing dbt, Sweetgreen struggled to access consistent insights. Sankalp Vatsh, Analytics Lead at Sweetgreen, explains that the problem was threefold:

- **Multiple sources of truth.** Different ingestion paths and databases often produced different answers for the same metric. “The exact same analytics dashboard might show gross sales as $13 million in one widget and $14 million in another,” says Sankalp. “Instead of understanding what actually drove $14 million in sales that week, the business and data teams would lose days to reconciling numbers.”
- **Bespoke data flows.** Every new business question required building a new script, pipeline, or one-off data flow — turning even simple analysis into a bottleneck. “We never had an enterprise data model before,” says Sankalp. “Whenever someone asked the data team a new question, we would just build a new data workstream.”
- **Manual processes.** The data team relied on Google Sheets that were manually ingested into data pipelines. If a user made a mistake upstream, the error eventually appeared downstream in the dashboards. With no easy way for stakeholders to trace what went wrong, data analysis became a time-consuming search for errors.

![](/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fwl0ndo6t%2Fmain%2Ff88b5751a10d15ca44c4252bf4fd3b94d6f042ae-512x319.png%3Ffit%3Dmax%26auto%3Dformat&w=1080&q=75)

The result was a fragmented data ecosystem that generated inconsistent metrics. And without a clear view into how the business was performing, Sweetgreen couldn’t trust the data — let alone act on it.

“In the restaurant industry, every day matters,” says Sankalp. “If it takes even a few days to gather insights, the week is already over and the opportunity to improve performance is gone.”

### Redesigning data models around the business

To fix their data issues, the team made the bold choice to overhaul Sweetgreen’s data model from the ground up.

“We thought about the core actions of a restaurant: a customer walking in to place an order for a certain product on a certain date,” reflects Sankalp. “That’s what we needed to build the new data model around.”

To create its new enterprise data model, Sweetgreen turned to dbt Labs to turn business logic into reusable, tested, and documented models. With dbt, Sweetgreen established a governed foundation that made everything downstream—from KPIs to semantic models—easier to build and maintain:

- **Fact tables** captured ‌core business events and served as the source of truth for measures (e.g., dollars sold, units sold).
- **Dimension tables** added standardized context and hierarchies (e.g., store → city → region).
- **dbt’s Semantic Layer** built on top of these tables to standardize KPIs and aggregation logic so metrics stayed consistent across dashboards and conversational analytics.

“dbt helped standardize our KPIs so that we can all work from a single source of truth,” says Sankalp. “For the first time, our business users had direct visibility into the data.”

The redesign gave Sweetgreen a true single source of truth for metrics—and, for the first time, business users could see how data flowed from ingestion all the way to the reporting layer. Using dbt’s lineage and documentation, stakeholders could understand where the numbers came from instead of guessing.

The data team also added custom, model-specific quality checks on top of dbt’s built-in tests to catch issues early and prevent bad data from reaching the business. The result was consistent metrics, higher confidence, and more self-serve exploration without needing to loop in the data team.

### Enabling self-service with Claude MCP and the dbt Semantic Layer

Next, Sweetgreen turned to the matter of creating a true AI-powered self-service experience for their business users. The data team had tried multiple business intelligence (BI) tools in the past (like Tableau, PowerBI, or ThoughtSpot) but kept running into a deeper cultural problem.

“People don't want to learn a new tool,” says Sankalp. “People absolutely are very used to talking to people to get answers. Natural-language tools are the way to move forward.”

Sweetgreen chose to use Claude as their AI tool to deliver conversational analytics to their business users. To ensure reliable AI outputs, they leveraged Claude, MCP, and the dbt Semantic Layer so the right domain business users get the right answers without bypassing governance.

In the diagram, the yellow nodes represent the governed semantic metrics, the canonical definitions for KPIs like gross sales, net sales, refunds, and loyalty. These are defined once in the dbt Semantic Layer and composed onto the underlying sales summary model. Because Claude was reading directly from the dbt Semantic Layer (which enforced consistent metric definitions), users received the same accurate, reliable answers grounded in version-controlled, tested metrics, not hallucinations or unverified numbers.

Say that a user wants to know more about Sweetgreen’s recently launched loyalty program. If they ask, “What loyalty analysis can I do?” Claude reviews the available semantic models and provides multiple analyses (e.g., by channel, venue, time, or customer behavior) that stakeholders may not have considered.

“Instead of reaching out to us with questions, people can play around with the data themselves to find answers,” says Sankalp. “It has freed us up from spending so much time just answering questions.”

### Faster insights, greater trust

Sweetgreen rolled this out in phases by domain. The data team started with high-impact areas like sales, built the fact/dimension foundation, and then layered semantic metrics on top.

Each semantic model stayed scoped (e.g., COGS separate from financial metrics) while still using shared definitions and quality checks. As each domain moved over, it eliminated conflicting numbers from different sources because the dbt Semantic Layer became the single, canonical place to get the metric everywhere, including in Claude.

“Data transformation is also about culture change,” says Sankalp. “We started with two or three team champions who would try it out and could show the rest of their team how much faster they were working.”

And the impact showed up immediately in time saved. *“By leveraging AI and the dbt Semantic Layer, self-service analysis has become a 30-minute job, compared to the old process of reaching out to the data team and waiting two weeks for the bandwidth to get an answer,”* says Sankalp. What once required a data-team work order can now be handled directly by business users through AI-powered conversational analytics with Claude and governed semantic metrics.

“Compared with a year ago, we’re delivering faster insights and more consistent metrics for the business,” reflects Sankalp. “In that time, the business has gained a lot of confidence in the data we provide.”

Since launching, the impact has been clear: teams get answers faster, and the data team is no longer the bottleneck. With governed metrics and consistent definitions, stakeholders see the same numbers across tools, with far less inconsistency and confusion. That shift has turned the data team from gatekeepers into enablers, letting business users self-serve insights with confidence.

Next, Sweetgreen plans to migrate the remaining dashboards off the legacy Airflow-based layer onto these dbt models so reporting is consistent end to end—across dashboards, repeatable analytics, and automation.

Today, the conversational experience is limited to Claude Desktop and a small pilot group of ~15–20 users. The team is intentionally starting with just 3–5 semantic models as they scale, staying vigilant about governance so AI responses remain grounded in verified metrics and don’t drift into hallucinations.

“We are no longer the bottlenecks or the sole bearers of all data questions,” concludes Sankalp. “Instead, we have become enablers.”
