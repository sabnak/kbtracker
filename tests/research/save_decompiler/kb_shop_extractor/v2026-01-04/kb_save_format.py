"""
King's Bounty Save File Format Definitions using Construct Library

This module defines the binary format structures for King's Bounty shop data
using the Construct library for declarative binary parsing.

Author: Claude (Anthropic)
Date: 2026-01-04
"""

from construct import *


# =============================================================================
# Basic Building Blocks
# =============================================================================

# 32-bit unsigned integer, little-endian (used for lengths and quantities)
Int32ul = Int32ul

# ASCII string with 32-bit length prefix (our main string format)
PascalString32 = PascalString(Int32ul, "ascii")


# =============================================================================
# Item Entry Format
# =============================================================================

# Items have: [length][name][metadata...]
# The metadata contains "slruck" field with quantity info
# For now, we'll just capture the name and explore metadata
ItemEntry = Struct(
	"name" / PascalString32,
	Probe(),  # Debug: see what follows the name
	# TODO: Parse metadata properly once we understand its structure
)


# =============================================================================
# Spell Entry Format
# =============================================================================

# Spells have: [length][name][quantity][metadata...]
# Current hypothesis based on existing parser
SpellEntry = Struct(
	"name" / PascalString32,
	"quantity" / Int32ul,
	Probe(),  # Debug: see what follows quantity
)


# =============================================================================
# Units/Garrison Format (Slash-Separated)
# =============================================================================

# Units and garrison use slash-separated string format:
# "unit_name/quantity/unit_name/quantity/..."
# Wrapped in: [strg marker][length][content string]
SlashSeparatedSection = Struct(
	"strg_marker" / Const(b"strg"),
	"content" / PascalString32,  # The "name/qty/name/qty" string
	Probe(),  # Debug: see what follows
)


# =============================================================================
# Section Definitions
# =============================================================================

# Items Section
# Starts with ".items" marker, followed by multiple ItemEntry structures
ItemsSection = Struct(
	"marker" / Const(b".items"),
	Probe(lookahead=100),  # Debug: see first 100 bytes after marker
	# TODO: How to parse variable number of entries?
	# GreedyRange won't work because we don't know where section ends
	# Need to find proper stop condition
)

# Spells Section
# Starts with ".spells" marker, followed by multiple SpellEntry structures
SpellsSection = Struct(
	"marker" / Const(b".spells"),
	Probe(lookahead=100),  # Debug: see first 100 bytes after marker
	# TODO: Same issue as ItemsSection - need stop condition
)

# Units Section
# Starts with ".shopunits" marker, followed by slash-separated content
UnitsSection = Struct(
	"marker" / Const(b".shopunits"),
	Probe(lookahead=50),  # Debug: see what's after marker
	"data" / SlashSeparatedSection,
)

# Garrison Section
# Starts with ".garrison" marker, followed by slash-separated content
GarrisonSection = Struct(
	"marker" / Const(b".garrison"),
	Probe(lookahead=50),  # Debug: see what's after marker
	"data" / SlashSeparatedSection,
)


# =============================================================================
# Shop Structure
# =============================================================================

# A complete shop has (in order):
# [.garrison section] (optional)
# [.items section]
# [.shopunits section]
# [.spells section]
# [Shop ID UTF-16 LE] "itext_m_<location>_<number>"

# For now, we'll parse sections individually rather than as a complete structure
# because we need to understand boundaries first


# =============================================================================
# Utility Functions
# =============================================================================

def parse_slash_separated(content_string: str) -> list[tuple[str, int]]:
	"""
	Parse slash-separated format: "name/qty/name/qty/..."

	:param content_string:
		The content string from SlashSeparatedSection
	:return:
		List of (name, quantity) tuples
	"""
	parts = content_string.split('/')
	items = []

	i = 0
	while i < len(parts) - 1:
		name = parts[i]
		try:
			quantity = int(parts[i + 1])
			items.append((name, quantity))
			i += 2
		except (ValueError, IndexError):
			i += 1

	return items


def find_section_in_data(data: bytes, shop_pos: int, marker: bytes, max_distance: int = 5000) -> int:
	"""
	Find section marker before shop ID position

	:param data:
		Binary save data
	:param shop_pos:
		Position of shop ID
	:param marker:
		Section marker to find (e.g., b".items")
	:param max_distance:
		Maximum bytes to search backwards
	:return:
		Position of marker, or -1 if not found
	"""
	search_start = max(0, shop_pos - max_distance)
	chunk = data[search_start:shop_pos]
	last_pos = chunk.rfind(marker)

	if last_pos != -1:
		return search_start + last_pos
	return -1


# =============================================================================
# Notes and TODO
# =============================================================================

"""
CURRENT ISSUES TO INVESTIGATE:

1. Section Boundaries:
   - How do we know where one section ends and next begins?
   - Current parser uses "find next marker or shop ID"
   - Can Construct handle this with RepeatUntil?

2. Item Metadata:
   - Items have complex metadata after the name
   - Contains "slruck" field with quantity info
   - Need to parse this properly

3. Spell Metadata:
   - Do spells have metadata after quantity?
   - Are there edge cases we're missing?

4. Invalid Entries:
   - Why are non-spells appearing in spell sections?
   - Are we parsing beyond the actual section?
   - Need to investigate with Probe()

NEXT STEPS:

1. Create explorer script to test these definitions
2. Use Probe() to see actual byte patterns
3. Refine definitions based on what we learn
4. Add proper section boundary detection
"""

