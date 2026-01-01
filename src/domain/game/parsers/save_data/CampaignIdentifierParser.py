from pathlib import Path
import hashlib

from dependency_injector.wiring import inject, Provide

from src.core.Container import Container
from src.domain.game.parsers.save_data.ICampaignIdentifierParser import ICampaignIdentifierParser
from src.domain.game.parsers.save_data.ISaveFileDecompressor import ISaveFileDecompressor


class CampaignIdentifierParser(ICampaignIdentifierParser):

	EXCLUDED_KEYWORDS: set[str] = {
		'crap', 'flags', 'clouds', 'hero', 'nickname',
		'arena', 'enemy', 'player', 'shop', 'item',
		'spell', 'unit', 'quest', 'map'
	}

	@inject
	def __init__(
		self,
		decompressor: ISaveFileDecompressor = Provide[Container.save_file_decompressor]
	):
		"""
		Initialize campaign identifier parser

		:param decompressor:
			Save file decompressor
		"""
		self._decompressor = decompressor

	def parse(self, save_path: Path) -> dict[str, str]:
		"""
		Extract campaign identifier from save file

		Scans decompressed save data for hero character names and generates
		a unique campaign ID via MD5 hash.

		:param save_path:
			Path to save 'data' file
		:return:
			Dictionary with campaign_id, first_name, second_name, full_name
		:raises ValueError:
			If save file is invalid
		:raises FileNotFoundError:
			If save file doesn't exist
		"""
		data = self._decompressor.decompress(save_path)
		first_name, second_name = self._extract_hero_names(data)
		campaign_id = self._compute_campaign_id(first_name, second_name)

		return {
			'campaign_id': campaign_id,
			'first_name': first_name,
			'second_name': second_name,
			'full_name': f"{first_name} {second_name}".strip()
		}

	def _extract_hero_names(self, data: bytes) -> tuple[str, str]:
		"""
		Extract hero first and second names from decompressed save data

		:param data:
			Decompressed save file data
		:return:
			Tuple of (first_name, second_name)
		"""
		candidates = []
		search_limit = min(100000, len(data))

		i = 0
		while i < search_limit - 4:
			byte1 = data[i]
			byte2 = data[i + 1]

			if byte2 == 0x04 and 0x10 <= byte1 <= 0x4F:
				string = self._extract_utf16_string_at(data, i)

				if string and 4 <= len(string) <= 20:
					string_lower = string.lower()
					if not any(keyword in string_lower for keyword in self.EXCLUDED_KEYWORDS):
						if string not in candidates:
							candidates.append(string)

				i += len(string.encode('utf-16-le')) if string else 2
			else:
				i += 1

			if len(candidates) >= 3:
				break

		first_name = candidates[1] if len(candidates) > 1 else ""
		second_name = candidates[2] if len(candidates) > 2 else ""

		return first_name, second_name

	def _extract_utf16_string_at(self, data: bytes, offset: int, max_length: int = 100) -> str:
		"""
		Extract UTF-16LE string starting at offset

		:param data:
			Binary data to read from
		:param offset:
			Starting position
		:param max_length:
			Maximum characters to read
		:return:
			Decoded string or empty string if invalid
		"""
		string_bytes = bytearray()
		i = offset

		while i < min(offset + max_length * 2, len(data) - 1):
			b1 = data[i]
			b2 = data[i + 1]

			if b1 == 0 and b2 == 0:
				break

			if (b2 == 0x04) or (b2 == 0x00 and 0x20 <= b1 <= 0x7E):
				string_bytes.append(b1)
				string_bytes.append(b2)
				i += 2
			else:
				break

		if string_bytes:
			try:
				return bytes(string_bytes).decode('utf-16-le')
			except:
				return ""

		return ""

	def _compute_campaign_id(self, first_name: str, second_name: str) -> str:
		"""
		Compute campaign identifier from hero names

		:param first_name:
			Hero's first name
		:param second_name:
			Hero's second name
		:return:
			Campaign ID as hex string
		"""
		combined = f"{first_name}|{second_name}"
		return hashlib.md5(combined.encode('utf-8')).hexdigest()
