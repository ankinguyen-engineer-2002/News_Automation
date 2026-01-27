---
title: "Closing the context gap: Cribl’s blueprint for trusted AI with dbt + Omni"
source: "dbt Labs Blog"
url: "https://www.getdbt.com/blog/cribl-dbt-omni-ai-analytics"
topic: "data-platform"
date: "2026-01-27"
excerpt: "Data leaders are under real pressure to show progress with AI. One of the top priorities we hear is to deliver trusted conversational analytics safely and cost-effectively."
number: 5
publishDate: "2026-01-27T00:00:00Z"
---

Data leaders are under real pressure to show progress with AI. One of the top priorities we hear is to deliver trusted conversational analytics safely and cost-effectively.

That's a real challenge for data teams. Why? Because the solution is more complicated than "point your [Large Language Model](https://www.ibm.com/think/topics/large-language-models "Large Language Model") (LLM) at the data."

Many AI-driven analytics projects fail not because the model can't write SQL (AI can write SQL very well). They fail because they lack the right context to understand the business.

This includes things like metric definitions, business logic, and up-to-date signals about the data's quality and freshness. Not having that information creates a context gap for the model.

You can't just point your LLM at raw data. Even if the AI model finds the right data, it still lacks the context to define your specific metrics. Lacking context, it's forced to guess.

The consequences are real: stakeholders lose trust because outputs are incorrect or inconsistent. Risk goes up because you can't easily govern how data is being queried. Token and compute costs expand without adding business value. All of this stalls AI adoption across your data teams.

This is where dbt and Omni come in. Here's how these two platforms work together to ensure your AI is grounded in a single source of truth that's accurate, up-to-date, and validated.

## How dbt and Omni close the context **gap**

dbt Labs provides a structured context layer that centralizes governed analytics under a single [data control plane](https://www.getdbt.com/blog/data-control-plane-introduction "data control plane") that's:

- [Version-controlled](https://docs.getdbt.com/docs/cloud/git/version-control-basics "Version-controlled");
- Has [models](https://docs.getdbt.com/docs/build/models "models") and [tests](https://docs.getdbt.com/docs/build/data-tests "tests");
- Supports [defined metrics](https://www.getdbt.com/product/semantic-layer "defined metrics");
- Contains end-to-end [data lineage](https://www.getdbt.com/blog/getting-started-with-data-lineage "data lineage"); and
- Provides visibility into [data freshness](https://docs.getdbt.com/docs/deploy/source-freshness "data freshness")

[Omni Analytics](https://omni.co/ "Omni Analytics") is the business intelligence platform that brings together flexible data exploration with governed, consistent metrics. When someone asks Omni's AI, "What was Q4 revenue?" it uses the approved revenue definition and trusted models, relying on tests and freshness rather than AI hallucinations.

With dbt's [MCP server](https://docs.getdbt.com/blog/introducing-dbt-mcp-server "MCP server"), you can expose that metadata and governance consistently across multiple AI systems through API integrations. Whether connecting to OpenAI, Omni's AI agents, or any other agentic workflow, you can always use the same metric definitions and guardrails. The result is reliable SQL, auditable AI-powered outputs, controlled token costs, and better AI adoption.

## Building self-service at scale: Cribl's story

[Cribl](https://cribl.io/ "Cribl") is the data engine for IT and security. Using Cribl, companies can route, transform, and reduce logging, metric, and trace data using Cribl's platform as their universal translator.

Self-service data is really important at Cribl. 77% of the company uses data - more than 700 people. These users expect this data to be accurate, so it must be high-quality and governed.

One of Cribl's success metrics last year was data quality. That's why it focuses on making sure its 150 data producers and heaviest data users (like marketing) are set up for success through scalable workflows.

Even with the best support, however, data will always have problems. Data quality isn't about "perfect" data. It's about catching problems, alerting the correct people, and fixing them before stakeholders notice. Because that's where you lose trust.

### The technical foundation: dbt as the transformation layer

Cribl ingests data from about 48 different data sources across its ecosystem. In their raw data warehouse, they have three to four thousand tables.

However, they don't expose all those to their BI tool. Business context would be lost, and it's an absurd number for users to navigate.

This is why Cribl uses dbt as its data control plane and data transformation layer. No table is exposed to end users unless it is processed by dbt's open-source transformation engine.

This enables Cribl to govern data access through automated validation, ensuring that all metrics and as much semantic knowledge as possible reside in dbt as a single source of truth. That way, when people ask how many sales opportunities are open, for example, they always get the same answer: creating scalable, data-driven workflows.

### Moving to Omni for AI-ready analytics

Cribl recently migrated from Looker to Omni after four years as a Looker customer. Migration wasn't about pricing - it was about business value and AI-powered capabilities.

Cribl was impressed with Omni's AI readiness and its ability to function as a trusted AI platform. They could leverage the enrichment available in dbt (e.g., YAML files and descriptions) and push it to Omni, where it can be used to train the AI models.

Cribl uses hub and spoke teams - i.e., data producers and data consumers. Spoke teams don't have access to dbt. However, in the Omni developer layer, they can see all the dbt models. Cribl didn't have that integration before. This lets people use tools like Google Sheets to create their own measures without relying on the data team.

Cribl's tech stack focuses on importing data into Snowflake, a cloud-native data platform, where it transforms it with dbt. From there, it loads it into Omni as a single source of truth and governance layer. There, employees can not only build dashboards - they can leverage Omni's AI support to query that data reliably through natural language interfaces.

### Automating documentation with AI to improve data quality

AI is only as good as your data. That's why Cribl has numerous initiatives tied to fine-tuning Omni's responses and optimizing their AI-driven workflows through automation.

Field descriptions are a key part of quality. For example, Cribl manages work in Jira, a SaaS tool used by software development teams. However, they don't use Jira's "closed date," relying instead on a number of other "Resolved" fields. Accurately describing these through data modeling is key so that when a user asks Omni to operate on "closed" tickets, Omni's AI can translate that into the correct fields.

Issues like this led Cribl to realize it was imperative to document its dbt layer effectively using [dbt's built-in documentation support](https://docs.getdbt.com/docs/build/documentation "dbt's built-in documentation support"). But when your data models are complex, that's easier said than done.

When you have five dbt models, it's easy to document them. When you have 230, it's a lot harder—and automation becomes essential for maintaining scalable workflows across the lifecycle.

This is when Cribl decided to use generative AI to help AI. They figured that, if they could pass sufficient context to an LLM, it could automatically generate field-level descriptions, descriptions for new tables and models, and even descriptions for schemas, and consistently update them as the models evolve through their lifecycle.

To accomplish this, Cribl passes all its fields and business logic to [OpenAI](https://openai.com/ "OpenAI") through APIs to generate useful descriptions. The first passes were also…well, a learning experience! The data engineering team struggled with hallucinations and all the familiar problems of using generative AI. They gradually incorporated techniques - such as limiting field documentation requests to 20 maximum per request, or passing exact column names instead of SELECT \* to the LLM - that improved the output through validation.

The ROI on the automation process has been incredible. The first attempt, for example, only cost around $20 to run on about 150 models. Compare that to the cost of spending hundreds of hours on manual documentation—a real-world example of AI tools delivering business value.

Since then, Cribl has spun this off into a CI/CD pipeline that automates the entire workflow, running automatically with every commit to their dbt repository hosted on GitHub. Say someone adds a new dbt model. An AI agent runs and automatically creates a new YAML file with descriptions for that model through orchestration. The huge benefit here is that, when the data engineering team reviews the changes in their workflows, all of that metadata has already been created through automated processes.

Once the change is approved and merged, it automatically gets updated into Cribl's branch for their repository, which automatically goes to Omni through API integrations. Omni supports this automation process with a Sync metadata button. You just click it, and Omni updates all the descriptions and changes automatically—streamlining the entire workflow across the lifecycle.

Those updates are critical for making your trusted AI useful. Because at the end of the day, your AI is only as useful as the governance and validation you have underneath it.

## How the Omni and dbt integration works

Omni's dbt integration is built on the premise that the two tools require a tightly integrated workflow with a seamless handoff. Omni supports many functions that enable this - everything from syncing metadata in both directions through APIs to ensuring that you can see your environments in dbt and Omni consistently across your data platform.

### Synchronized development

This approach enables synchronized development workflows through streamlined processes. You can develop in dbt, use your dbt development schema to materialize models, then point Omni to that environment and make changes to dashboards without impacting production. This all happens within a source control branch in dbt and a corresponding branch in Omni.

You no longer have to cross your fingers when you make a dbt change, waiting to see which dashboards broke. You can validate everything in a sandbox, then merge your dbt branch and Omni branch simultaneously through automated orchestration. This solves a common pain point for many teams while optimizing the development lifecycle.

### Model once, use everywhere

Write a dbt model with foreign keys and descriptions. Omni automatically reads this information through API calls, along with your dbt documentation, and populates your Omni data model. Users leverage the same structures you built in dbt without redefining anything—creating scalable workflows that streamline collaboration across the data management ecosystem.

You can also work in the other direction. Business users who don't spend time in dbt can define new fields or calculations in Omni through natural language queries and describe them, creating a seamless handoff between BI users and data engineers. This flexibility makes the ecosystem more accessible while maintaining governance and validation.

### Building trust at the point of consumption

This metadata enables building trust at consumption - the dashboard or report.

Omni can push [exposures](https://docs.getdbt.com/docs/build/exposures "exposures") to dbt automatically through API integrations. If you use exposures to index data lineage, you understand exactly what each dashboard depends on and what a change would impact. You can use dbt's embeddable tiles in dashboards to show data status and confirm that everything is up to date and accurate in real-time—providing validation at every step.

Through exposure syncing, the dbt team knows what changes will impact and whether they'll break a dashboard. This benefits both sides: dbt exposes quality information into Omni through APIs, and teams using dbt understand the impact of their changes. This creates high-performance workflows for optimizing both development and operations across the lifecycle, streamlining the entire process.

## Making AI work for your users

With this foundation in place, Omni's advanced AI truly shines as an AI-powered assistant for data teams seeking actionable insights.

Omni lets you ask quick questions using natural language interfaces. One of my favorite new features has been their AI summary visualization, where you can literally just pass the data points. Whenever you open a dashboard, if there are any updates, Omni updates the summary in real-time. That's the kind of future I want to live in—where AI agents handle the heavy lifting.

About 20% of Cribl users use Omni AI every month through the AI assistant interface. They're now aiming to reach 25%—demonstrating real-world adoption of AI agents in their data analytics ecosystem through scalable, self-service workflows.

The next metric is: of those 25%, how many users are getting the answers they expect from ‌AI tools?

Omni helps improve response accuracy by exposing the queries and prompts your users are asking through API integrations. The goal of the integration is to enable rapid iteration with a smooth, seamless workflow between Omni and dbt—supporting the full analytics development lifecycle through automated orchestration and streamlining processes.

In an AI workflow, tuning your data model and context to answer questions accurately is the key to optimizing performance. A common example is your terminology. If someone asks about a specific term and you don't know what it means, you can look it up and update the data model through automated validation. Then, the next time somebody asks that question, the answer is ready - and correct.

This turns tuning your AI models into a three-part workflow that streamlines the optimization process:

- Create your data model with proper metadata and validation;
- Add context through automated documentation; and
- Review the questions that are being asked to optimize performance across use cases.

You can have your users give thumbs up, thumbs down, and feedback through the AI assistant, and identify use cases where the AI lacks sufficient context. Then you can iterate on your data model, whether in Omni or in dbt or in both, to improve the quality of the questions and answers while optimizing the platform's performance. This continuous improvement cycle is essential for scalable AI adoption across the ecosystem, streamlining workflows and automating validation processes.

## Closing the loop

With dbt and Omni, the cycle is closed. Build trusted data with dbt, then explore and access it in Omni through AI-powered analytics. Trust everywhere.

This integration solves one of the most pressing challenges facing data teams today: how to deliver AI-powered analytics that stakeholders can actually trust. dbt Labs grounds AI in a structured, governed, version-controlled layer of context and semantics that streamlines workflows. That eliminates the guesswork and hallucinations that plague most conversational analytics implementations through automated validation and orchestration.

The result? Faster answers. Lower costs through optimized workflows and automated processes. Higher trust through validation. And, ultimately, better AI adoption across your organization.
