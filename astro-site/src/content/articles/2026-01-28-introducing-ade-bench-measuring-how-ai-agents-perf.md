---
title: "Introducing ADE-bench: measuring how AI agents perform data work"
title_vi: ""
source: "dbt Labs Blog"
url: "https://www.getdbt.com/blog/ade-bench-dbt-data-benchmarking"
topic: "data-platform"
date: "2026-01-28"
excerpt: "As AI coding agents reshape software engineering, a critical question remains unanswered: how well do these tools actually perform analytics and data engineering work?"
excerpt_vi: ""
number: 11
publishDate: "2026-01-28T00:00:00Z"
---

As AI coding agents reshape software engineering, a critical question remains unanswered: how well do these tools actually perform analytics and data engineering work?

While benchmarks like [SWE-bench](https://www.swebench.com/ "SWE-bench") have become standard for measuring coding agent performance in general software development, the data community has lacked a rigorous way to evaluate how models handle the specific challenges of data work.

[ADE-bench](https://github.com/dbt-labs/ade-bench "ADE-bench"), created by Benn Stancil (founder of Mode) in collaboration with dbt Labs, fills this gap. The benchmark evaluates AI agents on real-world analytics and data engineering tasks using actual dbt projects, databases, and the kinds of messy problems data practitioners face daily.

Early results show significant performance differences across models and configurations. In particular, they show how [dbt Fusion](https://www.getdbt.com/product/fusion "dbt Fusion"), in conjunction with the [Model Context Protocol (MCP)](https://docs.getdbt.com/docs/dbt-ai/about-mcp "Model Context Protocol (MCP)"), provides substantial improvements in agent accuracy and efficiency.

Jason Ganz, Director of Developer Experience and AI at dbt Labs, and Stancil [recently held a webinar to discuss](https://www.getdbt.com/resources/webinars/analytics-data-engineer-bench "recently held a webinar to discuss") why data work needs its own benchmark, how ADE-bench works, and what the initial results reveal about the current state of AI agents in analytics engineering.

## Why data work needs its own benchmark

"At the beginning of the year, the question was: are LLMs and agents useful for software engineering?" Ganz explained. "Pretty quickly this year, we’ve passed that. These things are useful. They're very useful. But how exactly they're useful and what exactly they're good at is still something that we don't exactly know."

One thing we *do* know is that benchmarks have become key to measuring coding agent quality. Software engineering has rigorous benchmarks, such as SWE-bench, that every new model release references. These provide rigorous ways to measure how well a model performs specific tasks, allowing teams to evaluate model progress over time.

One of the key philosophies of dbt is that it’s critical to apply [the lessons learned from software engineering to data work](https://www.getdbt.com/resources/the-analytics-development-lifecycle "the lessons learned from software engineering to data work"). However, there are also many ways that data is *not* like software engineering - data-specific workflows, tooling, etc. If coding agents are coming to data work, we need rigorous ways to measure their quality.

"The key thing is we don't know exactly how this is going to go," Ganz said. "We don't know how fast. We don't know what tasks agents are good at. Right now, data teams are kind of operating blind about how good these models are at actually performing the tasks that you all do every single day."

## The reality of data work versus the demo

The gap between how analytics work is often presented and how it actually happens is stark. Every demo follows the same script for analytics projects: you look at a chart, see some numbers, point out a weird blip, write SQL queries, do fancy analysis, pull up tables, find insights, then publish a great report. The business turns around, and everyone's happy.

These demos always feature tight, well-structured problems where everything is neat and clean, with amazing needle-in-the-haystack solutions that solve business problems.

But for most people in data work, this isn't reality.

"Typically, instead of looking at dashboards with this amazing little outlier, you look at very broken-looking dashboards," Stancil explained. "Or dashboards that don't really say anything. Or dashboards where there's just a thing that is broken, and the actual problem you have is your boss reaches out to you and says it's broken, and you have to fix it."

Software engineers can now tackle similar debugging challenges with AI tools. That’s left data engineers and analysts asking, “Can we have one of those, too?”

Several companies are trying to solve this problem. But the real answer to whether these tools can solve data problems is that we don't know.

We're not actually sure whether these things work. Individual companies might have things that work quite well for them, but, broadly, we don't have a clear sense of how well these solutions can solve data problems.

## The gap in existing benchmarks

[When Claude released Opus 4.5](https://www.anthropic.com/news/claude-opus-4-5 "When Claude released Opus 4.5"), their benchmark results included nothing related to data tasks. The same was true for [Gemini](https://gemini.google.com/ "Gemini") 3 and [GPT-5](https://openai.com/index/introducing-gpt-5/ "GPT-5"). Until we have something that helps us understand whether models are good at solving data problems, everyone has to test individually.

Some existing benchmarks attempt to help. [Spider](https://spider2-sql.github.io/ "Spider") is one of the major text-to-SQL benchmarks, featuring problems with basic data sets. They ask simple questions like, "What is the most popular product in California?"

"The work that they have done has been tremendously helpful to figure out how well these things can write SQL," Stancil acknowledged. "But again, this isn't that representative of the types of business problems that most people are trying to solve. In reality, we have projects with hundreds of tables and broken projects."

## How ADE-bench works

[ADE-bench](https://github.com/dbt-labs/ade-bench "ADE-bench") is designed to represent real-world data work with messy projects featuring hundreds of tables, often with multiple tables that could conceivably represent the same entity. This stands in contrast to the tight schemas designed as toy problems for AI.

The benchmark consists of three major components. First, every task has a [dbt project](https://docs.getdbt.com/docs/build/projects "dbt project") complete with [models](https://docs.getdbt.com/docs/build/models "models"), [macros](https://docs.getdbt.com/docs/build/jinja-macros "macros"), and [configuration files](https://docs.getdbt.com/reference/configs-and-properties "configuration files") representative of real-world setups.

Second, there are databases with actual data. Many problems aren't just in the dbt project itself. Sometimes the data itself is broken, or data types don't match. ADE-bench includes [DuckDB](https://duckdb.org/ "DuckDB") databases—essentially collections of [Parquet](https://parquet.apache.org/ "Parquet") files—that provide data to run projects on.

Third, there are the tasks themselves designed to be solved by an agent. These tasks correspond to real-world data problems - some specific, some vague. For example, a task might simply state "it's broken," similar to what an executive might say to a Slack bot.

When you run ADE-bench, the system spins up a [Docker container](https://www.docker.com/resources/what-container/ "Docker container") that creates a sandbox environment with the dbt project, database, and configuration. The task is then presented to the chosen agent, which attempts to solve the problem.

The agent works in the sandbox to figure out what's wrong, using whatever agent/LLM you designate. When it completes, it brings back its solution. ADE-bench then tests whether the solution works using primarily [dbt tests](https://docs.getdbt.com/docs/build/data-tests "dbt tests").

Tests can check if an orders total table has correct metrics, verify that a materialization changed from a table to a view, or compare agent-generated models to answer keys. You can also run scripts before or after the agent runs to inject problems, such as removing commas, deleting intermediate models, or introducing chaos representative of real-world scenarios.

## Performance results across models and configurations

We ran ADE-bench against a wide variety of LLMs, as well as against different combinations of [dbt Core](https://docs.getdbt.com/docs/core/installation-overview "dbt Core"), Core with the [Model Context Protocol (MCP) server](https://docs.getdbt.com/docs/dbt-ai/about-mcp "Model Context Protocol (MCP) server"), and [the dbt Fusion engine](https://www.getdbt.com/product/fusion "the dbt Fusion engine") with the MCP server. ADE-bench assessed both test pass rate, total cost of running the tests, and the total runtime.

The results show that using [OpenAI's Codex](https://openai.com/codex/ "OpenAI's Codex") coding agent with GPT-5.1, the tool passed 56% of the tests, at a cost of around $14.90. But the absolute pass rate isn't the key metric—it's about establishing a baseline for comparison.

"I would not consider the 56 percent here to be meaningful," Stancil said. "The point is a baseline of how well things do relative to one another."

[Claude Sonnet 4.5](https://www.anthropic.com/news/claude-sonnet-4-5 "Claude Sonnet 4.5") performed almost identically to Codex with the exact same pass rate and nearly identical cost. When testing across different database setups, [Snowflake](https://snowflake.com "Snowflake") proved slightly harder than DuckDB, which makes sense because agents don't have direct access to the underlying data and must wait for queries to return.

Using dbt Core with the MCP server improved the pass rate from 50% to 54%. When using dbt Fusion instead of dbt Core, the pass rate went up significantly because Fusion allows agents to interact with data more effectively.

"You can see that in the run times," Stancil noted. "It actually spends a little bit more work doing this, but it actually solves at a higher rate."

Combining Fusion with MCP didn't increase the pass rate further but made the process faster. Fusion provides the biggest gains in pass rates, while MCP provides the biggest gains in efficiency.

Testing different model versions showed clear progression. Claude Haiku 3, an older model, only solved 10 percent of tasks. [Haiku 4.5](https://www.anthropic.com/claude/haiku "Haiku 4.5") had a much higher pass rate but still lower than more expensive models. Opus matched Sonnet 4.5's pass rate, though thinking models tend to spiral and over-solve some problems.

## What's next and how to contribute

[ADE-bench is available as an open-source project on GitHub](https://github.com/dbt-labs/ade-bench "ADE-bench is available as an open-source project on GitHub"), providing a flexible scaffold for adding new tasks, projects, and trying different approaches.

Contributing tasks is one of the most valuable ways to help. More tasks that are representative of real-world problems make the benchmark better. Contributing new projects and databases is also tremendously helpful, though more complex due to permissions and privacy considerations.

The community can also contribute agent configurations. While most people won't build foundational models, adding context within environments can test how well agents solve problems. This might include documentation that guides the agent in thinking about analytics problems, or additional research steps before attempting solutions.

dbt Labs is focused on two key areas: improving the dbt language framework and engine, and building better MCP tooling. The dbt Fusion engine provides a substantial boost in agent accuracy due to its SQL comprehension capabilities. Future improvements include column-level lineage, better schema information, and enhanced type information.

"This is not something that we expect to figure out on our own," Ganz said. "This is something that we expect to figure out in partnership with the teams actually solving this."

For teams interested in deploying agents, ADE-bench lessons can help you understand what you can do to make your agents perform well. For the broader industry, having a shared sense of what models are good at and what they struggle with helps build systems that deploy models safely and securely.

The ADE-bench community meets in [the dbt Slack channel #tools-ade-bench](https://www.getdbt.com/community/join-the-community "the dbt Slack channel #tools-ade-bench"). You can try out the benchmark yourself and contribute to shaping how AI transforms data work over the coming years.

Meanwhile, to see ADE-bench in action and hear answers to pressing questionsasked by other customers, [watch a replay of the webinar](https://www.getdbt.com/resources/webinars/analytics-data-engineer-bench "watch a replay of the webinar").
