from enum import IntEnum


class ReadPriority(IntEnum):
	"""
	Source read priority for game data, from lowest to highest.

	Extracted files are placed in directories named ``<priority>-<session>``
	so that an ascending sort by directory yields ascending priority. When the
	same file name exists in several sources, the highest-priority source wins
	(``KFS_DATA`` over everything, loose session files lose to everything).
	"""

	LOOSE_SESSION = 1
	KFS_SESSION = 2
	LOOSE_DATA = 3
	KFS_DATA = 4

	def as_prefix(self) -> str:
		"""
		Render the priority as the directory name prefix

		:return:
			Numeric prefix string used in ``<priority>-<session>`` directories
		"""
		return str(self.value)
