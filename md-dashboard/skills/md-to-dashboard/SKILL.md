---
name: md-to-dashboard
description: >-
  This skill should be used when the user asks to "create a dashboard",
  "build a report", "generate an HTML dashboard", "visualize data",
  "make a data report", "turn this into a dashboard", "create a visualization",
  "build a chart", "make an interactive report", "visualize these results",
  "generate a report from this data", or mentions "md-to-dashboard",
  "markdown dashboard", "dashboard from data". Converts structured markdown
  with YAML frontmatter, chart blocks, and data tables into self-contained,
  production-grade HTML dashboards. The LLM writes only markdown — zero
  HTML authoring required.
version: 0.1.0
---

# Markdown-to-Dashboard

Generate self-contained, production-grade HTML dashboards from structured markdown.
The LLM writes **only markdown** — the build script handles all HTML, CSS, JS, and chart rendering.

## Why This Skill Exists

Writing HTML dashboards wastes 90%+ of tokens on boilerplate CSS, chart rendering JS,
and layout code. This skill inverts the process: provide data and config in markdown,
run one script, get a polished dashboard.

## Workflow

1. **Gather requirements** — Understand the data, audience, and story
2. **Write the dashboard markdown** — Create a `.dashboard.md` file using the format below
3. **Run the build script** — Execute `python3 ${SKILL_DIR}/scripts/build_dashboard.py <input.dashboard.md> <output.html>`
4. **Review and iterate** — Open the HTML, adjust the markdown, rebuild

`${SKILL_DIR}` refers to the directory containing this SKILL.md file.

## Dashboard Markdown Format

The markdown file has three parts: **YAML frontmatter** (config), **section headers** (structure), and **data tables + chart blocks** (content).

### Frontmatter (YAML)

```yaml
---
title: "Dashboard Title"
subtitle: "Boldin · Report Type"
date: "May 2026"
status: "Live Data"          # Shows pulsing green dot; omit for static

hero:
  kpis:
    - label: "Total Users"
      value: 24847            # Raw number — auto-formatted
      format: "k"             # n = comma, k = K/M suffix, pct = %, dollar = $
      delta: 12.3             # Percentage change (positive = green, negative = orange)

footer:
  source: "production-vpc-gemini.analytics"
  updated: "2026-05-13 08:00 UTC"
---
```

For the complete frontmatter reference including filters, theme overrides, and hero options, see `references/markdown-format.md`.

### Sections

Section headers use the format: `# NUMBER | Title | Kicker text`

```markdown
# 01 | Daily Volume | Conversation trends over the study period
```

This renders as a numbered section header with title and right-aligned description.

### Cards Within Sections

Use `## Card: Title` to create cards within a section. Cards auto-arrange in a grid.
Add card modifiers with `<!-- card: modifier -->`:

```markdown
## Card: Primary Intents
<!-- card: dark -->
```

Modifiers: `dark`, `eggshell`, `span-2` (full width), `span-left` (2fr 1fr), `span-right` (1fr 2fr)

### Chart Blocks

Define charts with fenced code blocks using the `chart` language:

````markdown
```chart
type: area
x: date
y: conversations
y2: users
moving_average: 7
annotations:
  - x: "2025-02-24"
    label: "Platform Launch"
```
````

Immediately follow with a markdown data table:

```markdown
| date       | conversations | users |
|------------|---------------|-------|
| 2025-01-01 | 150           | 89    |
| 2025-01-02 | 167           | 95    |
```

### Insight Blocks

For callout/insight cards with big numbers:

````markdown
```insight
style: green
eyebrow: "AI USERS · IMPACT"
stat: "+$4,200"
stat_unit: "/year"
title: "Annual benefit from AI optimization"
body: "Users who engage with AI see measurably better outcomes."
```
````

### Audit Blocks (Clickable Methodology)

Make any number auditable by adding an audit block:

````markdown
```audit
id: "total-users"
title: "Total Users"
methodology: "Count of distinct user_id with at least one session in the period."
sql: "SELECT COUNT(DISTINCT user_id) FROM analytics.sessions WHERE ..."
confidence: "high"
tables: ["analytics.sessions"]
```
````

Reference audits in KPIs or text with `[auditable:total-users]`.

## Supported Chart Types

| Type | Description | Required Fields |
|------|-------------|----------------|
| `area` | Time-series area chart | `x`, `y` |
| `line` | Line chart | `x`, `y` |
| `bar` | Vertical bar chart | `x`, `y` |
| `horizontal-bar` | Horizontal bar chart | `label`, `value` |
| `stacked-bar` | Stacked bar chart | `x`, `y` (multiple y columns) |
| `donut` | Donut/ring chart | `label`, `value` |
| `pie` | Pie chart | `label`, `value` |
| `heatmap` | 2D grid heatmap | `x`, `y`, `value` |
| `treemap` | Area-proportional rectangles | `label`, `value` |
| `scatter` | Scatter/bubble plot | `x`, `y`, optional `size` |
| `sparkline` | Inline mini chart | `x`, `y` |
| `table` | Styled data table | Any columns |
| `stat` | Big number stat cards | `label`, `value` |
| `progress` | Progress/bar fills | `label`, `value`, `max` |
| `comparison` | Side-by-side A vs B | `label`, `a_value`, `b_value` |
| `funnel` | Conversion funnel | `label`, `value` |
| `polar` | Radial/polar chart | `label`, `value` |
| `metric-row` | Labeled metric bars | `label`, `value`, optional `max` |

For full chart options (color, sort, limit, moving_average, annotations, y_format, etc.) and the complete color palette, see `references/chart-catalog.md`.

## Additional Resources

### Reference Files

For detailed chart configuration and advanced patterns:
- **`references/chart-catalog.md`** — Full chart type reference with all options and visual descriptions
- **`references/markdown-format.md`** — Complete markdown format specification with examples

### Build Script

- **`scripts/build_dashboard.py`** — The markdown-to-HTML converter. Run with:
  ```bash
  python3 ${SKILL_DIR}/scripts/build_dashboard.py input.dashboard.md output.html
  ```

### Template Engine

- **`assets/dashboard-engine.html`** — The HTML rendering engine template with full Boldin design system, chart renderers, filter system, and audit modals. Do not modify this file; the build script injects data automatically.

## Key Design Decisions

- **Self-contained output**: Every HTML file includes all CSS, JS, and data inline. No external dependencies except Google Fonts CDN and D3.js CDN.
- **Boldin brand default**: Uses Boldin design tokens (colors, typography, spacing). Override via `theme:` in frontmatter.
- **DOMParser-safe**: All HTML/SVG injection uses DOMParser — no innerHTML assignments.
- **Responsive**: All dashboards include mobile breakpoints at 1200px and 720px.
- **Auditable**: Any number can be made clickable to reveal methodology, SQL, and confidence level.

## Common Patterns

### Simple Report (no filters)
Write sections with charts and data tables. Good for weekly reports, one-time analyses.

### Filterable Dashboard
Add `filters:` to frontmatter. Include the filter key column in data tables.
The build script generates JavaScript that re-renders all charts when filters change.

### Comparison Dashboard (A vs B)
Use `comparison` chart type with `a_label`, `b_label` in the chart block.
Good for AI vs Non-AI, Test vs Control, Before vs After analyses.

### Executive Summary
Use insight blocks for the key takeaways, stat charts for KPIs, and minimal chart sections for supporting evidence.
