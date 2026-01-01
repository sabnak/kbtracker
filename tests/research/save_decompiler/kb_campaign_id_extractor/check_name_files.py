"""
Check if save name files contain campaign-specific information.
"""
from pathlib import Path


def read_name_file(path: Path) -> str:
	"""Read and decode name file as UTF-16LE."""
	with open(path, 'rb') as f:
		data = f.read()

	# Decode as UTF-16LE
	try:
		name = data.decode('utf-16-le').rstrip('\x00')
		return name
	except:
		return f"[decode error: {data.hex()}]"


def main():
	"""Main function."""
	saves_dir = Path(r'F:\var\kbtracker\tests\game_files\saves')

	saves = {
		'C1S1': saves_dir / '1707078232' / 'name',
		'C1S2': saves_dir / '1707047253' / 'name',
		'C2S1': saves_dir / '1766864874' / 'name',
		'C2S2': saves_dir / '1767209722' / 'name',
	}

	print("=" * 80)
	print("SAVE NAME FILES ANALYSIS")
	print("=" * 80)

	names = {}

	for save_id, path in saves.items():
		name = read_name_file(path)
		names[save_id] = name

		print(f"\n{save_id} ({path.parent.name}):")
		print(f"  Name: '{name}'")
		print(f"  Hex: {open(path, 'rb').read().hex()}")

	# Check for campaign ID
	print("\n" + "=" * 80)
	print("CAMPAIGN ID ANALYSIS")
	print("=" * 80)

	c1s1_name = names['C1S1']
	c1s2_name = names['C1S2']
	c2s1_name = names['C2S1']
	c2s2_name = names['C2S2']

	print(f"\n  Campaign 1 Save 1: '{c1s1_name}'")
	print(f"  Campaign 1 Save 2: '{c1s2_name}'")
	print(f"  Campaign 2 Save 1: '{c2s1_name}'")
	print(f"  Campaign 2 Save 2: '{c2s2_name}'")

	c1_same = (c1s1_name == c1s2_name)
	c2_same = (c2s1_name == c2s2_name)
	campaigns_differ = (c1s1_name != c2s1_name)

	print(f"\nResults:")
	print(f"  Campaign 1 saves have same name: {c1_same}")
	print(f"  Campaign 2 saves have same name: {c2_same}")
	print(f"  Campaigns have different names: {campaigns_differ}")

	if c2_same and not c1_same:
		print("\n  Campaign 2 saves share the same name!")
		print("  Campaign 1 saves have different names")
		print("  -> Name file is NOT a reliable campaign ID (user can rename saves)")


if __name__ == '__main__':
	main()
