# Chart Catalog — Full Reference

Complete reference for all chart types supported by the md-to-dashboard engine.

## Time Series Charts

### `area`
Filled area chart for time-series data. Primary visualization for trends over time.

**Required:** `x` (date/category column), `y` (numeric column)
**Optional:** `y2` (second y-axis), `moving_average` (integer), `annotations` (list), `color`, `y_format`

```chart
type: area
x: date
y: conversations
y2: users
moving_average: 7
color: primary
y_format: k
annotations:
  - x: "2025-02-24"
    label: "Platform Launch"
```

### `line`
Line chart without area fill. Same options as `area`.

### `sparkline`
Tiny inline chart (200x32px). Use inside KPI cards or stat stacks.
**Required:** `x`, `y`
**Optional:** `color`

## Bar Charts

### `bar`
Vertical bar chart.
**Required:** `x` (category), `y` (value)
**Optional:** `color`, `sort` (asc/desc/none), `limit`, `show_values`, `y_format`

### `horizontal-bar`
Horizontal bar chart with label-track-value layout.
**Required:** `label`, `value`
**Optional:** `color`, `sort`, `limit`, `y_format`

### `stacked-bar`
Stacked vertical bars with multiple series.
**Required:** `x` (category column)
All other numeric columns become stacked series.
**Optional:** `y_keys` (explicit list of columns to stack), `color`

### `metric-row`
Alias for `horizontal-bar`. Renders labeled metric bars.

## Distribution Charts

### `donut`
Ring/donut chart with center total.
**Required:** `label`, `value`
**Optional:** `colors` (list per-segment), `y_format`

### `pie`
Same as donut (renders identically with the donut renderer).

### `treemap`
Area-proportional rectangles. Uses D3.js treemap layout.
**Required:** `label`, `value`
**Optional:** `limit`, `y_format`

### `polar`
Radial/polar chart. Good for cyclic data (hours of day, days of week).
**Required:** `label`, `value`
**Optional:** `color`

## Grid Charts

### `heatmap`
2D grid with color-intensity cells. Uses log-scale color mapping.
**Required:** `x` (column axis), `y` (row axis), `value` (intensity)
Colors gradient: ink (low) → teal (mid) → green (high).

## Comparison Charts

### `comparison`
Side-by-side A vs B comparison blocks.
**Required:** `label`, `a_value`, `b_value`
**Optional:** `a_label`, `b_label`, `y_format`

### `funnel`
Conversion funnel with proportional bars.
**Required:** `label`, `value`
**Optional:** `color`, `y_format`

## Data Display

### `table`
Styled data table with hover rows. Renders all columns from data.
**Optional:** `y_format` (applied to numeric columns)

### `stat`
Big number stat cards in a 2-column grid.
**Required:** `label`, `value`
**Optional:** `y_format`

### `progress`
Progress bar rows with label and fill percentage.
**Required:** `label`, `value`
**Optional:** `max` (column for 100% reference), `color`, `y_format`

## Scatter / Relationship

### `scatter`
Scatter plot with optional bubble sizing.
**Required:** `x`, `y`
**Optional:** `size` (column for circle radius), `color`

## Common Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `color` | string | `primary` | Single color: `primary`, `accent`, `green`, `orange`, `berry`, `mint`, `teal`, `green-dark`, or hex |
| `colors` | list | auto palette | Per-series/segment colors |
| `sort` | string | `none` | `asc`, `desc`, or `none` |
| `limit` | integer | all | Show only top N items |
| `show_values` | boolean | false | Show value labels on chart elements |
| `show_legend` | boolean | auto | Show/hide legend |
| `y_format` | string | `n` | Number format: `n` (comma), `k` (K/M suffix), `pct` (%), `dollar` ($), `raw` (as-is) |
| `moving_average` | integer | none | N-period moving average overlay line |
| `annotations` | list | none | Vertical annotation lines: `{x, label}` |
| `y2` | string | none | Second y-axis column name |
| `x` | string | 1st column | X-axis data column |
| `y` | string | 2nd column | Y-axis data column |
| `label` | string | 1st column | Label column (categorical charts) |
| `value` | string | 2nd column | Value column (categorical charts) |

## Color Palette

The engine auto-cycles through the Boldin palette for multi-series charts:

1. `#04B477` — Green (primary)
2. `#5BD5A5` — Light green
3. `#027C53` — Dark green
4. `#FB5004` — Orange (accent)
5. `#A4E8CE` — Mint
6. `#BC0278` — Berry
7. `#FBBD04` — Yellow
8. `#0D3F4A` — Teal
9. `#79D8B2` — Sage
10. `#8A6800` — Gold

Override per-chart with `color:` (single) or `colors:` (list).
