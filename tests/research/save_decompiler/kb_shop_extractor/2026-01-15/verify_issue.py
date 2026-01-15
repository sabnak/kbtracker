#!/usr/bin/env python3
"""
Verification script to demonstrate the ShopInventoryParser directional search issue.

This script shows:
1. The shop with bocman/1460 exists in the save file
2. It's identified as m_portland_dark_6533
3. The parser extracts wrong inventory (skeleton/zombie/ghost2)
4. The correct inventory (bocman/1460) is AFTER the identifier, not before
"""

import struct
from pathlib import Path
from src.utils.parsers.save_data.SaveFileDecompressor import SaveFileDecompressor
from src.utils.parsers.save_data.ShopInventoryParserOld import ShopInventoryParserOld


def main():
    # Setup
    decompressor = SaveFileDecompressor()
    parser = ShopInventoryParserOld(decompressor)
    save_path = Path('/app/tests/game_files/saves/1768403991')
    data = decompressor.decompress(save_path)
    
    print('='*80)
    print('VERIFICATION: ShopInventoryParser Directional Search Issue')
    print('='*80)
    
    # Step 1: Find bocman/1460 in raw data
    bocman_pos = data.find(b'bocman/1460')
    print(f'\n1. Raw data contains bocman/1460 at position: {bocman_pos} (0x{bocman_pos:x})')
    
    # Step 2: Find the shop identifier
    shop_id_bytes = 'itext_m_portland_dark_6533'.encode('utf-16-le')
    shop_id_pos = data.find(shop_id_bytes)
    print(f'\n2. Shop identifier itext_m_portland_dark_6533 at position: {shop_id_pos} (0x{shop_id_pos:x})')
    
    # Step 3: Show position relationship
    print(f'\n3. Position relationship:')
    print(f'   Shop identifier: {shop_id_pos}')
    print(f'   bocman/1460:     {bocman_pos}')
    print(f'   Distance:        {bocman_pos - shop_id_pos} bytes AFTER identifier')
    
    # Step 4: Find .shopunits sections
    shopunits_before = data.rfind(b'.shopunits', max(0, shop_id_pos - 5000), shop_id_pos)
    shopunits_after = data.find(b'.shopunits', shop_id_pos, shop_id_pos + 5000)
    
    print(f'\n4. .shopunits sections:')
    print(f'   Before identifier: position {shopunits_before} (distance: {shop_id_pos - shopunits_before} bytes)')
    print(f'   After identifier:  position {shopunits_after} (distance: {shopunits_after - shop_id_pos} bytes)')
    
    # Step 5: Show content of both sections
    print(f'\n5. Section contents:')
    
    if shopunits_before != -1:
        strg_pos = data.find(b'strg', shopunits_before, shop_id_pos)
        if strg_pos != -1:
            length = struct.unpack('<I', data[strg_pos+4:strg_pos+8])[0]
            if 0 < length < 500:
                content = data[strg_pos+8:strg_pos+8+length].decode('ascii', errors='ignore')
                print(f'   Before: {content}')
    
    if shopunits_after != -1:
        strg_pos = data.find(b'strg', shopunits_after, shopunits_after + 200)
        if strg_pos != -1:
            length = struct.unpack('<I', data[strg_pos+4:strg_pos+8])[0]
            if 0 < length < 500:
                content = data[strg_pos+8:strg_pos+8+length].decode('ascii', errors='ignore')
                print(f'   After:  {content}')
    
    # Step 6: Show what parser extracts
    result = parser.parse(save_path)
    
    print(f'\n6. Parser extraction result for m_portland_dark_6533:')
    if 'm_portland_dark_6533' in result:
        shop_data = result['m_portland_dark_6533']
        print(f'   Units: {shop_data["units"]}')
        print(f'   Spells: {shop_data["spells"]}')
    else:
        print('   Shop not found!')
    
    # Step 7: Conclusion
    print(f'\n7. CONCLUSION:')
    print(f'   ✗ Parser searches BACKWARDS and finds: skeleton/zombie/ghost2')
    print(f'   ✓ Correct inventory is FORWARDS at: bocman/monstera/bear_white/demonologist')
    print(f'   → Parser needs bidirectional search or forward-first strategy')
    
    print('\n' + '='*80)


if __name__ == '__main__':
    main()
