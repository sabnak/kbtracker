from pathlib import Path
import struct

from dependency_injector.wiring import inject, Provide

from src.core.Container import Container
from src.utils.parsers.save_data.DataFileType import DataFileType
from src.utils.parsers.save_data.IHeroSaveParser import IHeroSaveParser
from src.utils.parsers.save_data.ISaveFileDecompressor import ISaveFileDecompressor


class HeroSaveParser(IHeroSaveParser):

	@inject
	def __init__(
		self,
		decompressor: ISaveFileDecompressor = Provide[Container.save_file_decompressor]
	):
		"""
		Initialize hero save parser

		:param decompressor:
			Save file decompressor
		"""
		self._decompressor = decompressor

	def parse(self, save_path: Path) -> dict[str, str]:
		"""
		Extract hero names from save file

		Extracts hero name(s) from the info file using structured field access.
		The info file contains explicit 'name' and 'nickname' fields with
		UTF-16LE encoded hero names.

		:param save_path:
			Path to save file (directory or .sav archive)
		:return:
			Dictionary with first_name and second_name
		:raises ValueError:
			If save file is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		info_data = self._decompressor.decompress(save_path, DataFileType.INFO)
		first_name, second_name = self._extract_hero_names_from_info(info_data)

		return {
			'first_name': first_name,
			'second_name': second_name
		}

	def _extract_hero_names_from_info(self, info_data: bytes) -> tuple[str, str]:
		"""
		Extract hero names from info file data

		Info file format:
		- [field_name_length: uint32] [field_name: ASCII] [value_length: uint32] [value: UTF-16LE]
		- Hero first name: 'name' field
		- Hero second name: 'nickname' field (optional)

		:param info_data:
			Raw info file bytes
		:return:
			Tuple of (first_name, second_name)
		"""
		# Extract first name from 'name' field
		first_name = self._extract_field_value(info_data, b'name')

		# Extract second name from 'nickname' field (optional)
		second_name = self._extract_field_value(info_data, b'nickname', start_after=b'name')

		return first_name, second_name

	def _extract_field_value(
		self,
		data: bytes,
		field_marker: bytes,
		start_after: bytes | None = None
	) -> str:
		"""
		Extract UTF-16LE string value for a field in info file

		:param data:
			Info file binary data
		:param field_marker:
			Field name to search for (e.g., b'name', b'nickname')
		:param start_after:
			Optional marker to start search after (e.g., search for nickname after name)
		:return:
			Decoded UTF-16LE string or empty string if not found
		"""
		# Find starting position
		start_pos = 0
		if start_after:
			after_pos = data.find(start_after)
			if after_pos != -1:
				start_pos = after_pos + len(start_after)

		# Find field marker
		field_pos = data.find(field_marker, start_pos)
		if field_pos == -1:
			return ""

		# Read character count (uint32 LE) after field marker
		value_length_pos = field_pos + len(field_marker)
		if value_length_pos + 4 > len(data):
			return ""

		char_count = struct.unpack("<I", data[value_length_pos:value_length_pos + 4])[0]

		# Validate character count
		if char_count <= 0 or char_count > 100:
			return ""

		# Read UTF-16LE string (2 bytes per character)
		value_start = value_length_pos + 4
		byte_length = char_count * 2
		value_end = value_start + byte_length

		if value_end > len(data):
			return ""

		# Decode UTF-16LE
		try:
			return data[value_start:value_end].decode('utf-16-le')
		except:
			return ""
