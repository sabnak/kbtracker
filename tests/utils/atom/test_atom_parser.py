import pytest
from src.utils import atom
from src.utils.atom.exceptions import AtomSyntaxError


class TestAtomLoads:
	"""
	Tests for atom.loads() function
	"""

	def test_simple_key_value(self):
		"""
		Test basic key=value parsing
		"""
		result = atom.loads("block { key=value }")
		assert result == {"block": {"key": "value"}}

	def test_nested_blocks(self):
		"""
		Test nested block structures
		"""
		content = "main { sub { key=value } }"
		result = atom.loads(content)
		assert result == {"main": {"sub": {"key": "value"}}}

	def test_multiple_top_level_blocks(self):
		"""
		Test multiple blocks at top level
		"""
		content = "block1 { a=1 } block2 { b=2 }"
		result = atom.loads(content)
		assert result == {"block1": {"a": 1}, "block2": {"b": 2}}

	def test_empty_blocks(self):
		"""
		Test empty block parsing
		"""
		result = atom.loads("empty { }")
		assert result == {"empty": {}}

	def test_multiline_structure(self):
		"""
		Test parsing multi-line blocks
		"""
		content = """
		main {
			class=box
			model=test.bms
			nested {
				value=123
			}
		}
		"""
		result = atom.loads(content)
		assert result["main"]["class"] == "box"
		assert result["main"]["model"] == "test.bms"
		assert result["main"]["nested"]["value"] == 123

	def test_empty_string(self):
		"""
		Test parsing empty string
		"""
		result = atom.loads("")
		assert result == {}

	def test_whitespace_only(self):
		"""
		Test parsing whitespace-only input
		"""
		result = atom.loads("   \n\n  \t  ")
		assert result == {}

	def test_comment_only(self):
		"""
		Test parsing file with only comments
		"""
		result = atom.loads("// comment 1\n// comment 2")
		assert result == {}


class TestTypeConversion:
	"""
	Tests for automatic type conversion
	"""

	def test_type_conversion_int(self):
		"""
		Test integer conversion
		"""
		assert atom.loads("block { price=150 }") == {"block": {"price": 150}}

	def test_type_conversion_float(self):
		"""
		Test float conversion
		"""
		assert atom.loads("block { scale=1.5 }") == {"block": {"scale": 1.5}}

	def test_type_conversion_bool_true(self):
		"""
		Test boolean true conversion
		"""
		assert atom.loads("block { flag=true }") == {"block": {"flag": True}}

	def test_type_conversion_bool_false(self):
		"""
		Test boolean false conversion
		"""
		assert atom.loads("block { flag=false }") == {"block": {"flag": False}}

	def test_type_conversion_leading_zero(self):
		"""
		Test that leading zeros are preserved as strings
		"""
		assert atom.loads("block { id=007 }") == {"block": {"id": "007"}}

	def test_type_conversion_single_zero(self):
		"""
		Test that single zero is converted to int
		"""
		assert atom.loads("block { value=0 }") == {"block": {"value": 0}}

	def test_type_conversion_negative_leading_zero(self):
		"""
		Test negative number with leading zero stays as string
		"""
		assert atom.loads("block { val=-007 }") == {"block": {"val": "-007"}}

	def test_type_conversion_disabled(self):
		"""
		Test disabling type conversion
		"""
		result = atom.loads("block { price=150 }", convert_types=False)
		assert result == {"block": {"price": "150"}}

	def test_vector_not_converted(self):
		"""
		Test that vectors remain as strings
		"""
		result = atom.loads("block { trans=0.01/-0.2/-0.4/0 }")
		assert result == {"block": {"trans": "0.01/-0.2/-0.4/0"}}

	def test_file_path_not_converted(self):
		"""
		Test that file paths remain as strings
		"""
		result = atom.loads("block { model=data/items/sword.bms }")
		assert result == {"block": {"model": "data/items/sword.bms"}}


class TestComments:
	"""
	Tests for comment handling
	"""

	def test_line_comments_ignored(self):
		"""
		Test that line comments are removed
		"""
		content = "// comment\nblock { key=value }"
		result = atom.loads(content)
		assert result == {"block": {"key": "value"}}

	def test_inline_comments_stripped(self):
		"""
		Test that inline comments are removed
		"""
		content = "block {\n  key=value // inline comment\n}"
		result = atom.loads(content)
		assert result == {"block": {"key": "value"}}


class TestIndexedLists:
	"""
	Tests for indexed list handling
	"""

	def test_sequential_indices_to_list(self):
		"""
		Test conversion of sequential indices to list
		"""
		content = "items { 1 { a=1 } 2 { a=2 } 3 { a=3 } }"
		result = atom.loads(content)
		assert result["items"] == [{"a": 1}, {"a": 2}, {"a": 3}]

	def test_duplicate_indices_append_to_list(self):
		"""
		Test that duplicate indices append to list
		"""
		content = "attachments { 1 { x=1 } 1 { x=2 } 1 { x=3 } }"
		result = atom.loads(content)
		assert isinstance(result["attachments"], list)
		assert len(result["attachments"]) == 1
		assert isinstance(result["attachments"][0], list)
		assert len(result["attachments"][0]) == 3
		assert result["attachments"][0] == [{"x": 1}, {"x": 2}, {"x": 3}]

	def test_non_sequential_indices_keep_as_dict(self):
		"""
		Test that non-sequential indices stay as dict
		"""
		content = "levels { 1 { } 5 { } 10 { } }"
		result = atom.loads(content)
		assert isinstance(result["levels"], dict)
		assert "1" in result["levels"]
		assert "5" in result["levels"]
		assert "10" in result["levels"]

	def test_non_numeric_keys_keep_as_dict(self):
		"""
		Test that non-numeric keys stay as dict
		"""
		content = "block { key1=val1 key2=val2 }"
		result = atom.loads(content)
		assert result == {"block": {"key1": "val1", "key2": "val2"}}


class TestErrorHandling:
	"""
	Tests for error handling
	"""

	def test_unmatched_opening_brace_raises_error(self):
		"""
		Test syntax error on unmatched opening brace
		"""
		with pytest.raises(AtomSyntaxError):
			atom.loads("block { key=value")

	def test_extra_closing_brace_ignored(self):
		"""
		Test that extra closing braces are handled
		"""
		result = atom.loads("block { key=value }")
		assert result == {"block": {"key": "value"}}


class TestRealWorldFiles:
	"""
	Tests with real game files
	"""

	def test_parse_absorbent_magic(self):
		"""
		Test parsing simple atom file
		"""
		result = atom.load_file("tests/game_files/_atom_examples/absorbent_magic.atom")
		assert "main" in result
		assert result["main"]["class"] == "box"
		assert result["main"]["model"] == "absorbent_magic.bms"

	def test_parse_absorbent_magic_structure(self):
		"""
		Test complete structure of absorbent_magic.atom
		"""
		result = atom.load_file("tests/game_files/_atom_examples/absorbent_magic.atom")
		assert "main" in result
		assert "animations" in result
		assert "editor" in result
		assert "collisions" in result
		assert "attachments" in result

	def test_parse_absorbent_magic_nested_infobox(self):
		"""
		Test nested infobox parsing
		"""
		result = atom.load_file("tests/game_files/_atom_examples/absorbent_magic.atom")
		assert "infobox" in result["main"]
		assert result["main"]["infobox"]["hint"] == "bonus_03_hint"
		assert result["main"]["infobox"]["msgbox"] == "bonus_03_msg"

	def test_parse_absorbent_magic_animations(self):
		"""
		Test animations block parsing
		"""
		result = atom.load_file("tests/game_files/_atom_examples/absorbent_magic.atom")
		animations = result["animations"]
		assert animations["idle"] == "/mo"
		assert animations["click"] == "/mo/r:0:10"

	def test_parse_absorbent_magic_attachments_list(self):
		"""
		Test attachments with duplicate indices become list
		"""
		result = atom.load_file("tests/game_files/_atom_examples/absorbent_magic.atom")
		attachments = result["attachments"]
		assert isinstance(attachments, list)
		assert len(attachments) == 1
		assert isinstance(attachments[0], list)
		assert len(attachments[0]) == 3


class TestAtomLoadFile:
	"""
	Tests for atom.load_file() function
	"""

	def test_load_file_not_found_raises_error(self):
		"""
		Test error on missing file
		"""
		with pytest.raises(FileNotFoundError):
			atom.load_file("nonexistent.txt")

	def test_load_utf8_file(self):
		"""
		Test loading UTF-8 encoded file
		"""
		result = atom.load_file("tests/game_files/_atom_examples/absorbent_magic.atom")
		assert isinstance(result, dict)
		assert len(result) > 0
