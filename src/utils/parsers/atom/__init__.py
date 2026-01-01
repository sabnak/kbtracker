from typing import TextIO

from src.utils.parsers.atom.AtomParser import AtomParser
from src.utils.parsers.atom.exceptions import AtomParseError, AtomSyntaxError, AtomEncodingError


def loads(s: str, convert_types: bool = True) -> dict | list:
	"""
	Parse atom format string to Python dict or list

	:param s:
		Atom format string
	:param convert_types:
		Whether to automatically convert types (default: True)
	:return:
		Parsed structure as dict or list
	"""
	parser = AtomParser(convert_types=convert_types)
	return parser.parse(s)


def load(fp: TextIO, convert_types: bool = True) -> dict | list:
	"""
	Parse atom format from file object

	:param fp:
		File object to read from
	:param convert_types:
		Whether to automatically convert types (default: True)
	:return:
		Parsed structure as dict or list
	"""
	content = fp.read()
	return loads(content, convert_types=convert_types)


def load_file(path: str, convert_types: bool = True) -> dict | list:
	"""
	Read and parse atom file with automatic encoding detection

	:param path:
		Path to atom file
	:param convert_types:
		Whether to automatically convert types (default: True)
	:return:
		Parsed structure as dict or list
	"""
	try:
		with open(path, 'r', encoding='utf-16-le') as f:
			content = f.read()
	except (UnicodeError, UnicodeDecodeError):
		with open(path, 'r', encoding='utf-8') as f:
			content = f.read()

	return loads(content, convert_types=convert_types)


__all__ = [
	'loads',
	'load',
	'load_file',
	'AtomParseError',
	'AtomSyntaxError',
	'AtomEncodingError',
]
