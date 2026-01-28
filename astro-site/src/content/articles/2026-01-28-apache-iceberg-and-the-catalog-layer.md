---
title: "Apache Iceberg and the catalog layer"
title_vi: ""
source: "dbt Labs Blog"
url: "https://www.getdbt.com/blog/apache-iceberg-and-the-catalog-layer"
topic: "data-platform"
date: "2026-01-28"
excerpt: "In this episode of The Analytics Engineering Podcast, Tristan talks with Russell Spitzer, a PMC member of Apache Iceberg and Apache Polaris and principal engineer at Snowflake. They discuss the..."
excerpt_vi: ""
number: 13
publishDate: "2026-01-28T00:00:00Z"
---

In this episode of The Analytics Engineering Podcast, Tristan talks with Russell Spitzer, a PMC member of Apache Iceberg and Apache Polaris and principal engineer at Snowflake. They discuss the evolution of open table formats and the catalog layer. They dig into how the Apache Software Foundation operates. And they explore where Iceberg and Polaris are headed. If you want to go deep on the tech behind open table formats, this is the conversation for you.

A lot has changed in how data teams work over the past year. We’re collecting input for the [2026 State of Analytics Engineering Report](https://forms.gle/KBU9smukSfiK1g4W7 "2026 State of Analytics Engineering Report") to better understand what’s working, what’s hard, and what’s changing. If you’re in the middle of this work, your perspective would be valuable.

[Take the survey](https://forms.gle/Jc54NuP96qekHU9j7 "Take the survey")

*Please reach out at podcast@dbtlabs.com for questions, comments, and guest suggestions.*

**Listen & subscribe from:**

## Key takeaways

### Tristan Handy: You spend a lot of your time thinking about Iceberg and Polaris. Give the audience background on how you found yourself in this niche of high‑volume analytic data file formats.

**Russell Spitzer:** It’s a bit random. I started at DataStax on Apache Cassandra as a test engineer and quickly got drawn into analytics. I saw big compute clusters and wanted to be involved. A coworker, Piotr, noticed Spark 0.9 and began a Spark–Cassandra connector. That got me into Spark. Over six to seven years I focused on moving data between Cassandra and Spark and into other systems. The interoperability problem across distributed compute frameworks was compelling.

This was pre‑Apache Arrow and pre‑table formats. We were just putting Parquet files everywhere and no one quite knew what they were doing. Pre‑Spark, people explored DSLs like Apache Pig. Eventually the industry converged on SQL for end‑user interfaces.

I later applied to Apple for the Spark team.

### Helping build Apple’s Spark infra, or working directly on Spark?

Apple has an open-source Spark team and a Spark‑as‑infra team. I was trying to join the open source team, pushing Apple’s priorities into the project and supporting Spark as a service. During interviews, Anton—another Iceberg PMC—convinced the hiring manager I should join the data tables team, essentially Apple’s Apache Iceberg team.

They ambitiously planned to replace lots of internal systems with Iceberg. Iceberg existed but was early (Netflix started it around 2018/2019; I joined Apple in 2020). At Apple it was Iceberg all the time; convincing teams to move off older stacks, adopting open‑source‑as‑a‑service to save money, and getting onto ACID‑capable foundations. We were successful.

### Migrations are hard. How did you make it accessible?

We replaced complicated bespoke reliability fixes with Iceberg. In Hive/HDFS, small‑file problems lead teams to write custom compaction and locking. Removing that toil is a big win. For big orgs, migration is a long‑term investment with ongoing engineering cost. For smaller companies, the key is offloading runtime responsibilities—ideally to SaaS—so engineers aren’t in the loop. Open source limits lock‑in so you can move between systems. Most companies are paid to deliver business value, not to build data infra. dbt is a great example of avoiding hand‑rolled pipeline code. Same logic applies to table/file formats.

### Let’s talk Apache governance. What’s a PMC? How do projects run?

Apache projects aren’t owned by one company. Influence is earned by contributing to the community. The PMC governs merges, releases, membership. People move companies; the project stays with them. The goal is to make the project broadly useful. There’s no CEO dictating roadmap and no company can change the license.

Most big projects—Spark, Kafka, Iceberg, Flink—are maintained by employees of companies with vested interests, but governance is consensus‑driven. Vetoes are for technical issues (security, future‑limiting design), not ideology.

### Is Iceberg for the top 20 tech companies or for everyone?

Not everyone needs Iceberg. OLTP belongs elsewhere. But for analytics, we should move past raw Parquet partition trees with folder‑name partitioning. In the Hadoop era, lakes were dumping grounds; schema evolution was painful. Many are still moving from CSV to Parquet. Over time, better encodings and table formats become default.

Decoupling compute and storage changes everything versus co‑located HDFS. Defaults tuned for HDFS (like 128MB Parquet files) don’t always hold for S3. We want elastic storage and compute; no one wants to pay for compute because storage grew.

### Walk us through Iceberg versions.

v1: transactional analytics—ACID commits instead of fragile Hive/HDFS patterns. v2: row‑level operations—logical deletes via delete files so you don’t rewrite 10M‑row data files to remove one row; later compaction physically purges (key for GDPR). v3: expanded types—geospatial and variant for semi‑structured data; Variant was standardized across vendors and Parquet so everyone can write/read consistently.

v4: two thrusts—streaming and AI. Reduce commit latency, make retries faster under contention. Historically writes took 10–20 minutes, so commit latency didn’t matter. For streaming (writes every minute/five), it does. We’re evolving commit and REST catalog protocols so clients can specify intent (add these files, ensure these exist, then delete those) and let the catalog resolve conflicts server‑side.

On AI: Iceberg doesn’t yet serve some vector/image‑heavy patterns well. We’re exploring changes in Iceberg, Parquet, or both, without breaking existing tables.

### Talk about Polaris and the catalog layer.

Polaris is an Apache incubator project (PPMC). Incubation proves we operate like an Apache project (community‑driven, trademarks donated). Iceberg defines the REST catalog spec/client; Polaris implements a catalog that speaks that spec. Many of us work across projects (Parquet, Iceberg, Polaris), which helps align boundaries.

### Horizon, Polaris, external catalogs—what’s the story?

We’re simplifying: Snowflake can act as an Iceberg REST catalog, or you can use an external REST catalog. External can be Polaris (managed by Snowflake or self‑hosted) or another REST implementation. Interoperability means everything talks the same REST.

### What is Polaris trying to be best at?

A broad, interoperable lakehouse catalog. It can act as a generic Spark catalog (HMS replacement) and aims to support multiple table/file formats. Architectural choices differ (KV vs. relational storage, where transactions live, policy enforcement vs. recording, identity integration). Polaris aims for base implementations that are pluggable—e.g., AWS/GCP/Microsoft identity.

### Identity and scope—where does the catalog stop?

There’s a “business catalog” for discovery/listing versus a “system catalog” that must know table layout to govern access. Polaris can vend short‑lived credentials for the exact directory of a table’s files for a load operation; that requires understanding layout. Purely relational metadata often needs to delegate that decision.

### Will identity/grants slow broad adoption?

Possibly. But many once‑complex things become default—compressed files, columnar formats, soon encryption. With collaboration (like Variant), we’ll land broadly accepted patterns.

## Chapters

00:01:30 — Guest welcome and interview start

00:02:00 — Russell’s path: DataStax Cassandra, Spark connector, interoperability

00:05:20 — Joining Apple’s Iceberg team and early Iceberg momentum

00:06:20 — Why migrations resonated: replacing bespoke Hive/HDFS compaction/locking

00:09:10 — Apache governance 101: PMCs, consensus, and corporate influence

00:15:40 — How decisions land without votes; when vetoes apply

00:18:30 — Who needs Iceberg and where it fits

00:22:20 — Lake → lakehouse and warehouse → lakehouse in the cloud era

00:25:20 — Iceberg versions: v1 transactions, v2 row‑level ops (GDPR), v3 types

00:28:10 — Standardizing Variant across vendors and Parquet

00:31:10 — Iceberg v4 goals: streaming commit/retry improvements and AI use cases

00:33:40 — Commit latency and server‑side conflict resolution

00:37:20 — Polaris as an Apache incubating project (PPMC)

00:39:30 — Iceberg REST catalog spec and Polaris implementation

00:42:30 — Clarifying Snowflake Horizon, Polaris, and external REST catalogs

00:45:10 — What Polaris aims to be best at; pluggable identity providers

00:48:00 — Identity scope: business vs. system catalogs and credential vending

00:51:00 — Will identity/grants slow mass adoption?

00:52:50 — Wrap‑up
