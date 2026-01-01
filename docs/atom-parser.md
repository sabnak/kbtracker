# Atom File Parser

Universal parser for King's Bounty `.atom` file format, similar to Python's `json.loads()`.

## Overview

The atom parser (`src.utils.atom`) provides a simple API for parsing King's Bounty's proprietary `.atom` format files into Python dictionaries and lists. It handles automatic type conversion, comment removal, and encoding detection.

## Usage

```python
from src.utils import atom

# Parse atom string
result = atom.loads("main { class=box model=test.bms }")
# Returns: {'main': {'class': 'box', 'model': 'test.bms'}}

# Parse from file object
with open('file.atom', 'r') as f:
    result = atom.load(f)

# Parse file with automatic encoding detection (UTF-16 LE / UTF-8)
result = atom.load_file('tests/game_files/_atom_examples/absorbent_magic.atom')
```

## Features

### Automatic Type Conversion (enabled by default)

```python
result = atom.loads("config { port=8080 debug=true scale=1.5 }")
# port=8080 → int
# debug=true → bool
# scale=1.5 → float
```

**Leading zeros preserved:**
```python
result = atom.loads("item { id=007 }")
# id=007 → "007" (string, not 7)
```

**Disable type conversion:**
```python
result = atom.loads("config { port=8080 }", convert_types=False)
# All values remain as strings
```

### Nested Structures

```python
result = atom.loads("main { infobox { hint=bonus_03_hint } }")
# Returns: {'main': {'infobox': {'hint': 'bonus_03_hint'}}}
```

### Comment Handling

```python
# Line comments
content = "// This is a comment\nmain { class=box }"
result = atom.loads(content)

# Inline comments
content = "main { class=box // inline comment }"
result = atom.loads(content)
```

### Indexed Lists

**Sequential indices (1, 2, 3) → Python list:**
```python
result = atom.loads("items { 1 { a=1 } 2 { a=2 } 3 { a=3 } }")
# Returns: {'items': [{'a': 1}, {'a': 2}, {'a': 3}]}
```

**Duplicate indices → list of duplicates:**
```python
result = atom.loads("attachments { 1 { x=1 } 1 { x=2 } 1 { x=3 } }")
# Returns: {'attachments': [[{'x': 1}, {'x': 2}, {'x': 3}]]}
```

**Non-sequential indices → dict:**
```python
result = atom.loads("levels { 1 { } 5 { } 10 { } }")
# Returns: {'levels': {'1': {}, '5': {}, '10': {}}}
```

### File Encoding

Automatic detection of UTF-16 LE (game default) with fallback to UTF-8:

```python
result = atom.load_file('items.txt')  # Handles both encodings automatically
```

## Type Conversion Rules

| Input | Output | Example |
|-------|--------|---------|
| `true` / `false` | `bool` | `true` → `True` |
| Integer | `int` | `150` → `150` |
| Integer with leading zero | `str` | `007` → `"007"` |
| Float | `float` | `1.5` → `1.5` |
| Slash-separated values | `str` | `0.01/-0.2/-0.4` → `"0.01/-0.2/-0.4"` |
| File paths | `str` | `data/file.bms` → `"data/file.bms"` |
| Other text | `str` | `box` → `"box"` |

## Error Handling

```python
from src.utils.atom import AtomSyntaxError, AtomParseError

try:
    result = atom.loads("block { invalid")
except AtomSyntaxError as e:
    print(f"Syntax error: {e}")
```

## Atom File Format

The atom format is a brace-based hierarchical syntax used throughout King's Bounty game resources:

```
block_name {
    property=value
    property=value

    nested_block {
        key=value
    }

    indexed_collection {
        1 { key=value }
        2 { key=value }
    }
}
```

**Key characteristics:**
- Hierarchical blocks delimited by `{ }`
- Properties in format `key=value`
- Comments prefixed with `//`
- Files typically stored in UTF-16 LE encoding
- Used for items, spells, effects, medals, units, and other game data

## Implementation Details

- **Module location**: `src/utils/atom/`
- **Parser**: Token-based recursive descent parser
- **Performance**: Parses 4.7MB `items.txt` in <1 second
- **Encoding**: UTF-16 LE with UTF-8 fallback
- **Comments**: Line (`//`) and inline comments supported
- **Braces**: Proper nesting validation with error reporting

## Testing

```bash
docker exec kbtracker_app bash -c 'cd /app && pytest tests/utils/atom/test_atom_parser.py -v'
```

All 33 tests passing with comprehensive coverage of:
- Basic parsing
- Type conversion
- Comment handling
- Indexed list detection
- Error handling
- Real-world file parsing

## Related Documentation

- [items.md](items.md) - Item resources that use atom format
- [game-resources.md](game-resources.md) - Overview of game resource formats
