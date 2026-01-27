# Digest Prompt Template

You are an expert data engineering and AI news analyst. Generate a concise daily digest from the following articles.

## Articles

{% for article in articles %}
### {{ article.title }}
- Source: {{ article.source }}
- Group: {{ article.group }}
- URL: {{ article.url }}

{% if article.extracted %}
{{ article.content[:1500] }}
{% else %}
{{ article.snippet }}
{% endif %}

---
{% endfor %}

## Instructions

Generate a **Quick Digest** section that:

1. Lists 4-6 bullet points summarizing the most important news
2. Groups related items together
3. Uses clear, concise language
4. Includes the source name in parentheses after each point
5. Does NOT include any information not present in the articles above

Format as markdown bullet points. Example:

- **Power BI**: New semantic model features announced for Fabric (Power BI Blog)
- **Databricks**: Unity Catalog enhancements for data governance (Databricks Blog)

Remember: Only include facts that can be directly verified from the article content above. Do not hallucinate or make up details.
