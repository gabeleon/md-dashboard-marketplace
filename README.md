# md-dashboard — Claude Code Plugin Marketplace

Generate production-grade, self-contained HTML dashboards from structured markdown. The LLM writes only markdown with data tables and chart configs — the plugin handles all HTML, CSS, JavaScript, and chart rendering automatically.

## Install

```bash
claude install-marketplace github:gabeleon/md-dashboard-marketplace
claude install md-dashboard@md-dashboard-marketplace
```

## What It Does

Instead of spending thousands of tokens writing HTML/CSS/JS boilerplate for every dashboard, write a `.dashboard.md` file with:

- **YAML frontmatter** for config (title, KPIs, filters, theme)
- **Section headers** (`# 01 | Revenue | Monthly trends`)
- **Chart blocks** (` ```chart ` with type, axes, options)
- **Data tables** (standard markdown tables)

Run one command and get a polished, self-contained HTML dashboard.

## 21 Chart Types

| Category | Types |
|----------|-------|
| **Time Series** | `area`, `line`, `sparkline` |
| **Bar Charts** | `bar`, `horizontal-bar`, `stacked-bar`, `metric-row` |
| **Distribution** | `donut`, `pie`, `treemap`, `polar` |
| **Grid** | `heatmap` |
| **Comparison** | `comparison`, `funnel`, `progress` |
| **Data Display** | `table`, `stat` |
| **Diagrams** | `diagram` / `mermaid` (flowcharts, sequence, etc.) |
| **Special** | `highlight-number` (giant gradient text), `quad` (2x2 thermal grid) |

## Features

- **Interactive tooltips** on all chart types (hover anywhere on area/line charts)
- **Audit modals** — click any number to see methodology, SQL, confidence, filter chain
- **Filters** — dropdown selects that dynamically re-render all charts
- **Mermaid diagrams** — flowcharts, sequence diagrams, architecture diagrams
- **Responsive** — works on desktop and mobile
- **Self-contained** — single HTML file, no backend needed
- **Boldin brand** — built-in design system with themeable CSS variables

## Quick Start

After installing, say: *"Create a dashboard from this data"* or invoke `/md-dashboard:md-to-dashboard`

The skill will guide you to:
1. Write a `.dashboard.md` file
2. Run the build script
3. Open the generated HTML

## Example

```markdown
---
title: "Product Health Dashboard"
subtitle: "Acme SaaS"
date: "May 2026"
status: "Live Data"

hero:
  kpis:
    - label: "MRR"
      value: 2834000
      format: "dollar"
      delta: 14.2
---

# 01 | Revenue Trend | Monthly recurring revenue

## Card: MRR Over Time

` ``chart
type: area
x: month
y: mrr
moving_average: 3
y_format: dollar
` ``

| month   | mrr     |
|---------|---------|
| 2025-06 | 1850000 |
| 2025-07 | 1920000 |
| 2025-08 | 2100000 |
```

## License

MIT
