#!/usr/bin/env python3
"""
build_dashboard.py — Convert structured markdown to self-contained HTML dashboards.

Usage:
    python3 build_dashboard.py input.dashboard.md output.html
    python3 build_dashboard.py input.dashboard.md  # outputs to input.html

The markdown file uses YAML frontmatter for config, # headers for sections,
```chart blocks for visualization config, and markdown tables for data.
"""

import sys
import re
import json
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# YAML Parsing — use PyYAML if available, otherwise a robust fallback
# ---------------------------------------------------------------------------

try:
    import yaml as _yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ---------------------------------------------------------------------------
# Markdown Parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Extract YAML frontmatter and body from markdown text."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', text, re.DOTALL)
    if not match:
        return {}, text
    yaml_text, body = match.group(1), match.group(2)
    if HAS_YAML:
        try:
            result = _yaml.safe_load(yaml_text)
            return (result if isinstance(result, dict) else {}), body
        except Exception:
            pass
    return _parse_yaml_fallback(yaml_text), body


def _parse_yaml_fallback(text):
    """Robust recursive YAML parser for when PyYAML is not installed."""
    lines = text.split('\n')
    result, _ = _parse_yaml_block(lines, 0, 0)
    return result


def _parse_yaml_block(lines, start, base_indent):
    """Parse a YAML block (dict) starting from line index `start` at `base_indent`."""
    result = {}
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith('#'):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            break  # Dedented past our block
        stripped = line.strip()

        # List item at this level — caller handles
        if stripped.startswith('- ') and indent == base_indent:
            break

        if ':' not in stripped:
            i += 1
            continue

        colon_idx = stripped.index(':')
        key = stripped[:colon_idx].strip().strip('"').strip("'")
        value = stripped[colon_idx + 1:].strip()
        i += 1

        if value == '' or value == '>' or value == '|' or value == '>-':
            # Look ahead to determine if list, dict, or multiline string
            if i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                next_indent = len(next_line) - len(next_line.lstrip()) if next_stripped else indent + 2

                if next_stripped.startswith('- '):
                    # It's a list
                    lst, i = _parse_yaml_list(lines, i, next_indent)
                    result[key] = lst
                elif next_indent > indent and next_stripped:
                    # It's a nested dict or multiline string
                    if ':' in next_stripped and not next_stripped.startswith('"'):
                        nested, i = _parse_yaml_block(lines, i, next_indent)
                        result[key] = nested
                    else:
                        # Multiline string
                        val_lines = []
                        while i < len(lines) and lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip())) > indent:
                            val_lines.append(lines[i].strip())
                            i += 1
                        result[key] = ' '.join(val_lines)
                else:
                    result[key] = ''
            else:
                result[key] = ''
        elif value.startswith('[') and value.endswith(']'):
            inner = value[1:-1].strip()
            if inner:
                items = _split_yaml_inline(inner)
                result[key] = [_parse_scalar(x.strip()) for x in items]
            else:
                result[key] = []
        elif value.startswith('{') and value.endswith('}'):
            result[key] = _parse_inline_dict(value)
        else:
            result[key] = _parse_scalar(value)

    return result, i


def _parse_yaml_list(lines, start, base_indent):
    """Parse a YAML list starting from line `start`."""
    result = []
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith('#'):
            i += 1
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        if indent < base_indent:
            break  # Dedented past list

        if not stripped.startswith('- '):
            # Could be continuation of previous dict item
            if indent > base_indent and ':' in stripped:
                # Continuation key: value for last dict item
                if result and isinstance(result[-1], dict):
                    k, v = stripped.split(':', 1)
                    result[-1][k.strip().strip('"').strip("'")] = _parse_scalar(v.strip())
                    i += 1
                    continue
            break

        item_text = stripped[2:].strip()
        item_indent = indent + 2  # Content indent after "- "
        i += 1

        if item_text.startswith('{') and item_text.endswith('}'):
            result.append(_parse_inline_dict(item_text))
        elif ':' in item_text:
            # Dict item — parse first key, then continue gathering at deeper indent
            item = {}
            k, v = item_text.split(':', 1)
            k = k.strip().strip('"').strip("'")
            v = v.strip()
            if v:
                item[k] = _parse_scalar(v)
            else:
                # Nested value
                if i < len(lines):
                    nl = lines[i]
                    ni = len(nl) - len(nl.lstrip()) if nl.strip() else item_indent + 2
                    if ni > item_indent and nl.strip():
                        if nl.strip().startswith('- '):
                            lst, i = _parse_yaml_list(lines, i, ni)
                            item[k] = lst
                        else:
                            nested, i = _parse_yaml_block(lines, i, ni)
                            item[k] = nested
                    else:
                        item[k] = ''

            # Gather remaining keys at item_indent or deeper
            while i < len(lines):
                nl = lines[i]
                ns = nl.strip()
                ni = len(nl) - len(nl.lstrip()) if ns else 0
                if not ns:
                    i += 1
                    continue
                if ni < item_indent:
                    break
                if ns.startswith('- ') and ni <= indent:
                    break  # Next list item at same level
                if ':' in ns and not ns.startswith('- '):
                    k2, v2 = ns.split(':', 1)
                    k2 = k2.strip().strip('"').strip("'")
                    v2 = v2.strip()
                    if v2:
                        item[k2] = _parse_scalar(v2)
                    else:
                        # Nested under this key
                        i += 1
                        if i < len(lines):
                            nnl = lines[i]
                            nni = len(nnl) - len(nnl.lstrip()) if nnl.strip() else ni + 2
                            if nnl.strip().startswith('- '):
                                lst, i = _parse_yaml_list(lines, i, nni)
                                item[k2] = lst
                            elif nni > ni and nnl.strip():
                                nested, i = _parse_yaml_block(lines, i, nni)
                                item[k2] = nested
                            else:
                                item[k2] = ''
                        continue
                    i += 1
                else:
                    break

            result.append(item)
        else:
            result.append(_parse_scalar(item_text))

    return result, i


def _split_yaml_inline(text):
    """Split a YAML inline list/dict respecting quotes."""
    items = []
    current = ''
    depth = 0
    in_quotes = False
    qchar = None
    for ch in text:
        if ch in ('"', "'") and not in_quotes:
            in_quotes = True
            qchar = ch
            current += ch
        elif ch == qchar and in_quotes:
            in_quotes = False
            current += ch
        elif ch in ('{', '[') and not in_quotes:
            depth += 1
            current += ch
        elif ch in ('}', ']') and not in_quotes:
            depth -= 1
            current += ch
        elif ch == ',' and depth == 0 and not in_quotes:
            items.append(current.strip())
            current = ''
        else:
            current += ch
    if current.strip():
        items.append(current.strip())
    return items


def _parse_inline_dict(text):
    """Parse { key: val, key: val } into dict."""
    inner = text.strip('{}').strip()
    result = {}
    for pair in _split_yaml_inline(inner):
        if ':' in pair:
            k, v = pair.split(':', 1)
            result[k.strip().strip('"').strip("'")] = _parse_scalar(v.strip())
    return result


def _parse_scalar(text):
    """Parse a YAML scalar value."""
    if not text:
        return ''
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    if text.lower() in ('true', 'yes'):
        return True
    if text.lower() in ('false', 'no'):
        return False
    if text.lower() in ('null', 'none', '~'):
        return None
    try:
        if '.' in text:
            return float(text)
        return int(text)
    except ValueError:
        pass
    return text


# Legacy aliases for chart/insight/audit block parsing
def split_yaml_list(text):
    return _split_yaml_inline(text)

def parse_inline_dict(text):
    return _parse_inline_dict(text)

def parse_value(text):
    return _parse_scalar(text)


def parse_markdown_table(text):
    """Parse a markdown table into list of dicts."""
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    if len(lines) < 3:
        return []

    # Header row
    headers = [h.strip() for h in lines[0].strip('|').split('|')]
    headers = [h for h in headers if h]

    # Skip separator row (line 1)
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip('|').split('|')]
        cells = [c for c in cells if c is not None]
        if len(cells) >= len(headers):
            row = {}
            for j, header in enumerate(headers):
                val = cells[j].strip() if j < len(cells) else ''
                # Try to parse as number
                try:
                    if '.' in val:
                        row[header] = float(val)
                    else:
                        row[header] = int(val.replace(',', ''))
                except (ValueError, AttributeError):
                    row[header] = val
            rows.append(row)
    return rows


def parse_chart_block(text):
    """Parse a ```chart block into config dict. Supports nested YAML."""
    # Try PyYAML first for full YAML support
    if HAS_YAML:
        try:
            result = _yaml.safe_load(text)
            if isinstance(result, dict):
                return result
        except Exception:
            pass
    # Try the robust fallback parser
    try:
        lines = text.strip().split('\n')
        result, _ = _parse_yaml_block(lines, 0, 0)
        if result:
            return result
    except Exception:
        pass
    # Last resort: flat key-value parsing
    config = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('- '):
            continue
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                config[key] = [parse_value(x.strip()) for x in split_yaml_list(val[1:-1])]
            elif val.startswith('{'):
                config[key] = parse_inline_dict(val)
            elif val:
                config[key] = parse_value(val)
    return config


def parse_insight_block(text):
    """Parse an ```insight block into config dict."""
    return parse_chart_block(text)  # Same format


def parse_audit_block(text):
    """Parse an ```audit block into config dict.

    Supports flat key:value pairs plus nested objects via indentation:
      meta:
        owner: Data Team
        freshness: Daily
      filterChain:
        - step: Source table
          detail: analytics.subscriptions
          count: 142000
        - step: Active only
          count: 89400
          isResult: true
      filters:
        - { label: "Active subs", type: "locked" }
    """
    # Try the full YAML parser first for complex blocks
    if HAS_YAML:
        try:
            result = _yaml.safe_load(text)
            if isinstance(result, dict):
                return result
        except Exception:
            pass
    # Use the fallback YAML block parser
    lines = text.split('\n')
    result, _ = _parse_yaml_block(lines, 0, 0)
    return result if result else parse_chart_block(text)


def parse_body(body_text):
    """Parse the markdown body into sections with cards, charts, and data."""
    sections = []
    audits = {}
    current_section = None
    current_card = None
    lines = body_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Section header: # 01 | Title | Kicker
        section_match = re.match(r'^#\s+(\d+)\s*\|\s*(.+?)\s*\|\s*(.+)$', stripped)
        if section_match:
            current_section = {
                'number': section_match.group(1),
                'title': section_match.group(2).strip(),
                'kicker': section_match.group(3).strip(),
                'cards': [],
                'text': ''
            }
            sections.append(current_section)
            current_card = None
            i += 1
            continue

        # Alt section header: # 01 | Title (no kicker)
        section_match2 = re.match(r'^#\s+(\d+)\s*\|\s*(.+)$', stripped)
        if section_match2 and not section_match:
            current_section = {
                'number': section_match2.group(1),
                'title': section_match2.group(2).strip(),
                'kicker': '',
                'cards': [],
                'text': ''
            }
            sections.append(current_section)
            current_card = None
            i += 1
            continue

        # Card header: ## Card: Title
        card_match = re.match(r'^##\s+Card:\s*(.+)$', stripped)
        if card_match and current_section:
            current_card = {
                'title': card_match.group(1).strip(),
                'modifiers': [],
                'charts': [],
                'insights': [],
                'text': ''
            }
            current_section['cards'].append(current_card)
            i += 1
            continue

        # Card modifier: <!-- card: modifier -->
        mod_match = re.match(r'^<!--\s*card:\s*(.+?)\s*-->', stripped)
        if mod_match and current_card:
            mods = [m.strip() for m in mod_match.group(1).split(',')]
            current_card['modifiers'].extend(mods)
            i += 1
            continue

        # Fenced code blocks
        if stripped.startswith('```chart'):
            block_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                block_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            chart_config = parse_chart_block('\n'.join(block_lines))

            # Look ahead for data table (but NOT section headers which also contain |)
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines) and '|' in lines[i] and not re.match(r'^#\s+\d+\s*\|', lines[i].strip()):
                table_lines = []
                while i < len(lines) and '|' in lines[i] and not re.match(r'^#\s+\d+\s*\|', lines[i].strip()):
                    table_lines.append(lines[i])
                    i += 1
                chart_config['data'] = parse_markdown_table('\n'.join(table_lines))

            target = current_card if current_card else (current_section if current_section else None)
            if target:
                if 'charts' not in target:
                    target['charts'] = []
                target['charts'].append(chart_config)
            continue

        if stripped.startswith('```insight'):
            block_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                block_lines.append(lines[i])
                i += 1
            i += 1
            insight_config = parse_insight_block('\n'.join(block_lines))
            target = current_card if current_card else (current_section if current_section else None)
            if target:
                if 'insights' not in target:
                    target['insights'] = []
                target['insights'].append(insight_config)
            continue

        if stripped.startswith('```audit'):
            block_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                block_lines.append(lines[i])
                i += 1
            i += 1
            audit_config = parse_audit_block('\n'.join(block_lines))
            if 'id' in audit_config:
                audits[audit_config['id']] = audit_config
            continue

        # Diagram / Mermaid blocks
        if stripped.startswith('```diagram') or stripped.startswith('```mermaid'):
            block_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                block_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            diagram_config = {'type': 'diagram', 'code': '\n'.join(block_lines)}
            target = current_card if current_card else (current_section if current_section else None)
            if target:
                if 'charts' not in target:
                    target['charts'] = []
                target['charts'].append(diagram_config)
            continue

        # Standalone data table (outside chart block)
        if stripped.startswith('|') and current_section:
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            data = parse_markdown_table('\n'.join(table_lines))
            # Attach to last chart that has no data, or to section
            target = current_card if current_card else current_section
            if target and target.get('charts'):
                for ch in reversed(target['charts']):
                    if 'data' not in ch or not ch['data']:
                        ch['data'] = data
                        break
            continue

        # Regular text content
        if stripped and current_section:
            if current_card:
                current_card['text'] += stripped + '\n'
            else:
                current_section['text'] += stripped + '\n'

        i += 1

    # Auto-create cards for sections with charts but no explicit cards
    for section in sections:
        if section.get('charts') and not section['cards']:
            auto_card = {
                'title': '',
                'modifiers': ['span-2'],
                'charts': section.pop('charts'),
                'insights': section.pop('insights', []),
                'text': ''
            }
            section['cards'] = [auto_card]

        # Auto-create card for sections with insights but no cards (and no charts)
        if section.get('insights') and not section['cards']:
            auto_card = {
                'title': '',
                'modifiers': ['span-2'],
                'charts': [],
                'insights': section.pop('insights'),
                'text': ''
            }
            section['cards'] = [auto_card]

    return sections, audits


# ---------------------------------------------------------------------------
# HTML Generation
# ---------------------------------------------------------------------------

def build_config(frontmatter, sections, audits):
    """Build the CONFIG JSON that the template engine consumes."""
    total_sections = len(sections)
    config = {
        'meta': {
            'title': frontmatter.get('title', 'Dashboard'),
            'subtitle': frontmatter.get('subtitle', ''),
            'date': frontmatter.get('date', ''),
            'status': frontmatter.get('status', ''),
        },
        'theme': frontmatter.get('theme', {}),
        'hero': frontmatter.get('hero', {}),
        'filters': frontmatter.get('filters', []),
        'sections': [],
        'audits': audits,
        'footer': frontmatter.get('footer', {})
    }

    for section in sections:
        s = {
            'number': section['number'],
            'total': str(total_sections).zfill(2),
            'title': section['title'],
            'kicker': section.get('kicker', ''),
            'text': section.get('text', '').strip(),
            'cards': []
        }
        for card in section.get('cards', []):
            c = {
                'title': card.get('title', ''),
                'modifiers': card.get('modifiers', []),
                'charts': card.get('charts', []),
                'insights': card.get('insights', []),
                'text': card.get('text', '').strip()
            }
            s['cards'].append(c)
        config['sections'].append(s)

    return config


def load_template():
    """Load the dashboard engine HTML template."""
    template_path = Path(__file__).parent.parent / 'assets' / 'dashboard-engine.html'
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)
    return template_path.read_text(encoding='utf-8')


def inject_config(template, config):
    """Inject CONFIG JSON into the template HTML."""
    config_json = json.dumps(config, indent=2, ensure_ascii=False)
    # Replace the placeholder in the template
    return template.replace('/* __CONFIG_PLACEHOLDER__ */', f'const CONFIG = {config_json};', 1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: build_dashboard.py <input.dashboard.md> [output.html]", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.with_suffix('.html')

    # Parse markdown
    text = input_path.read_text(encoding='utf-8')
    frontmatter, body = parse_frontmatter(text)
    sections, audits = parse_body(body)

    # Build config
    config = build_config(frontmatter, sections, audits)

    # Load template and inject
    template = load_template()
    html = inject_config(template, config)

    # Write output
    output_path.write_text(html, encoding='utf-8')
    print(f"Dashboard generated: {output_path}")
    print(f"  Sections: {len(sections)}")
    print(f"  Cards: {sum(len(s.get('cards', [])) for s in sections)}")
    print(f"  Charts: {sum(sum(len(c.get('charts', [])) for c in s.get('cards', [])) for s in sections)}")
    print(f"  Audits: {len(audits)}")
    print(f"  Filters: {len(frontmatter.get('filters', []))}")


if __name__ == '__main__':
    main()
