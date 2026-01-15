with open('decompressed_data.bin', 'rb') as f:
    data = f.read()

# Position 669222 is where we found building_trader@293 for m_portland_dark
# Let's trace backward and forward from there
pos = 669222

print('Analysis of shop structure at position 669222')
print('='*60)
print()

# Read 1000 bytes before
before = data[pos-1000:pos]
at = data[pos:pos+500]

print('1000 bytes BEFORE position 669222:')
print(before.decode('utf-8', errors='replace'))
print()
print('='*60)
print()
print('500 bytes AT position 669222:')
print(at.decode('utf-8', errors='replace'))
