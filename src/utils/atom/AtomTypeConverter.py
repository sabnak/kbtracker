class AtomTypeConverter:
	"""
	Type converter for atom file values
	"""

	@staticmethod
	def convert(value: str) -> bool | int | float | str:
		"""
		Convert string value to appropriate Python type

		:param value:
			String value to convert
		:return:
			Converted value (bool, int, float, or str)
		"""
		if value == 'true':
			return True
		if value == 'false':
			return False

		if '.' not in value:
			return AtomTypeConverter._try_int_conversion(value)

		return AtomTypeConverter._try_float_conversion(value)

	@staticmethod
	def _try_int_conversion(value: str) -> int | str:
		"""
		Try to convert value to integer

		:param value:
			String value without decimal point
		:return:
			Integer if conversion successful and no leading zeros, otherwise string
		"""
		try:
			int_val = int(value)
			stripped = value.lstrip('-')
			if stripped.startswith('0') and len(stripped) > 1:
				return value
			return int_val
		except ValueError:
			return value

	@staticmethod
	def _try_float_conversion(value: str) -> float | str:
		"""
		Try to convert value to float

		:param value:
			String value with decimal point
		:return:
			Float if conversion successful, otherwise string
		"""
		try:
			return float(value)
		except ValueError:
			return value
