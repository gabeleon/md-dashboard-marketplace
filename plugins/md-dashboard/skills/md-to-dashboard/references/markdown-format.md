# Dashboard Markdown Format — Complete Specification

## File Structure

A `.dashboard.md` file has three parts:

```
---
YAML frontmatter (config)
---

# Section headers with chart blocks and data tables
```

## Frontmatter Reference

### Required Fields

```yaml
---
title: "Dashboard Title"        # Main display title
---
```

### Optional Fields

```yaml
subtitle: "Boldin · Report"     # Appears as eyebrow + brand divider
date: "May 2026"                # Shown in hero metadata
status: "Live Data"             # Shows pulsing green dot; omit for no indicator
```

### Theme Override

Default is Boldin brand. Override any color:

```yaml
theme:
  primary: "#04B477"            # Maps to --green (CTA, charts, accents)
  dark: "#10182C"               # Maps to --ink (text, dark backgrounds)
  accent: "#FB5004"             # Maps to --orange (warnings, secondary)
  bg: "#FBF7F0"                 # Maps to --sand (page background)
```

### Hero Section

```yaml
hero:
  description: "Optional lead paragraph text"
  kpis:
    - label: "Total Users"
      value: 24847              # Raw number — auto-formatted
      format: "k"               # n | k | pct | dollar | raw
      delta: 12.3               # +/- percentage change
      auditable: true           # Makes it clickable
      audit_id: "total-users"   # Links to an ```audit block
    - label: "Revenue"
      value: 1250000
      format: "dollar"
      delta: -2.1
```

### Filters

```yaml
filters:
  - id: cohort                  # Unique filter ID
    label: "User Cohort"        # Dropdown label
    key: "cohort"               # Column name in data tables to filter on
    options:
      - { value: "all", label: "All Users", default: true }
      - { value: "paid", label: "Paid Only" }
      - { value: "trial", label: "Trial" }
  - id: period
    label: "Time Period"
    key: "period"
    options:
      - { value: "all_time", label: "All Time", default: true }
      - { value: "last_30", label: "Last 30 Days" }
```

When filters are active, data tables must include the filter `key` column.
Rows where the column matches the selected value (or is empty) are shown.
The value `"all"` shows all rows regardless.

### Footer

```yaml
footer:
  source: "production-vpc-gemini.analytics"
  updated: "2026-05-13 08:00 UTC"
```

## Body Syntax

### Section Headers

Format: `# NUMBER | Title | Kicker`

```markdown
# 01 | Daily Volume | Conversation trends over the study period
```

Renders:
- `01` → section number (mono font, left-aligned)
- `Daily Volume` → section title (large DM Sans heading)
- `Conversation trends...` → kicker text (right-aligned description)

The kicker is optional:
```markdown
# 02 | Usage Patterns
```

### Cards

Cards are created with `## Card: Title` inside a section:

```markdown
# 01 | Revenue | Key financial metrics

## Card: Monthly Revenue
```chart
type: area
x: month
y: revenue
```

| month   | revenue |
|---------|---------|
| 2025-01 | 100000  |
| 2025-02 | 120000  |

## Card: Top Products
```chart
type: horizontal-bar
label: product
value: revenue
sort: desc
limit: 5
```

| product    | revenue |
|------------|---------|
| Premium    | 450000  |
| Basic      | 320000  |
| Enterprise | 180000  |
```

### Card Modifiers

Add HTML comments after the card header:

```markdown
## Card: Summary
<!-- card: dark -->
```

Available modifiers:
- `dark` — Dark background (ink) with white text
- `eggshell` — Light green tinted background
- `span-2` — Full width (spans both grid columns)
- `span-left` — Left-biased 2:1 grid (use with the next card)
- `span-right` — Right-biased 1:2 grid

### Chart Blocks

Fenced code blocks with `chart` language:

````markdown
```chart
type: area
x: date
y: value
color: primary
```
````

Immediately follow with a data table. The table is automatically bound to the chart.

### Insight Blocks

For callout cards with big numbers and narrative text:

````markdown
```insight
style: green
eyebrow: "KEY FINDING"
stat: "+$4,200"
stat_unit: "/year"
title: "AI users see better outcomes"
body: "Users who engage with AI planning tools achieve measurably higher projected retirement income."
```
````

Styles: `green` (green gradient), `berry` (berry gradient), `sand` (dark gradient), or omit for default dark.

### Audit Blocks

Define clickable methodology modals:

````markdown
```audit
id: "total-users"
title: "How Total Users is Calculated"
methodology: "Count of distinct user_id in analytics.sessions with at least one event in the selected time period."
sql: "SELECT COUNT(DISTINCT user_id) FROM analytics.sessions WHERE timestamp >= @start_date"
confidence: "high"
tables: ["analytics.sessions", "analytics.events"]
```
````

Fields:
- `id` — Unique identifier (referenced by `audit_id` in KPIs)
- `title` — Modal heading
- `methodology` — Plain text explanation
- `sql` — Source query (rendered in dark code block)
- `confidence` — `high`, `med`, or `low` (shows colored badge)
- `tables` — List of tables used

### Standalone Text

Regular paragraphs between section header and cards become section description text:

```markdown
# 03 | Engagement | How users interact with the platform

This section analyzes user engagement patterns across different cohorts and time periods.

## Card: Engagement Metrics
...
```

## Complete Example

```markdown
---
title: "AI Impact Report"
subtitle: "Boldin · Product Analytics"
date: "May 2026"
status: "Live Data"

hero:
  description: "Analyzing how AI features affect user outcomes and engagement."
  kpis:
    - label: "AI Conversations"
      value: 24847
      format: "k"
      delta: 12.3
    - label: "Users Reached"
      value: 8192
      format: "k"
      delta: 8.7
    - label: "Plans Modified"
      value: 3420
      format: "k"
      delta: 15.2
    - label: "Avg Messages"
      value: 6.8
      format: "raw"
      delta: -1.2

filters:
  - id: cohort
    label: "Cohort"
    key: "cohort"
    options:
      - { value: "all", label: "All Users", default: true }
      - { value: "paid", label: "Paid Users" }

footer:
  source: "production-vpc-gemini.analytics"
  updated: "2026-05-13"
---

# 01 | Conversation Volume | Daily trends since launch

## Card: Daily Conversations
<!-- card: span-2 -->

```chart
type: area
x: date
y: conversations
moving_average: 7
annotations:
  - x: "2026-02-24"
    label: "Platform Launch"
```

| date       | conversations | cohort |
|------------|---------------|--------|
| 2026-01-01 | 150           | all    |
| 2026-01-02 | 167           | all    |
| 2026-01-03 | 143           | all    |

# 02 | Intent Distribution | What users ask about

## Card: Primary Intents

```chart
type: donut
label: intent
value: count
```

| intent          | count |
|-----------------|-------|
| Financial Plan  | 5420  |
| Tax Questions   | 3180  |
| Retirement      | 2890  |
| Investment      | 1640  |

## Card: Top Topics

```chart
type: treemap
label: topic
value: count
limit: 8
```

| topic           | count |
|-----------------|-------|
| Retirement Age  | 2340  |
| Social Security | 1890  |
| Tax Brackets    | 1560  |
| 401k Rollover   | 1230  |
| Roth Conversion | 980   |

# 03 | Key Findings | Executive takeaways

```insight
style: green
eyebrow: "PRIMARY FINDING"
stat: "+$4,200"
stat_unit: "/year"
title: "AI users optimize Social Security claiming"
body: "Users who engage with AI planning see measurably higher projected retirement income."
```

```insight
style: sand
eyebrow: "ENGAGEMENT"
stat: "6.8"
stat_unit: "msgs/convo"
title: "Deep engagement drives better outcomes"
body: "Conversations with 5+ messages show 2x higher plan modification rates."
```
```

## Data Table Format

Standard markdown tables with `|` delimiters:

```markdown
| column_a | column_b | column_c |
|----------|----------|----------|
| value1   | 100      | 45.2     |
| value2   | 200      | 67.8     |
```

- Numbers are auto-parsed (integers and floats)
- Commas in numbers are stripped (`1,000` → `1000`)
- Strings remain as-is
- Column names become data keys (use snake_case)
- The separator row (dashes) is required but alignment markers (`:---:`) are ignored
