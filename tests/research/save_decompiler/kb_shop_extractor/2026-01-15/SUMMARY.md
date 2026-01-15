# Executive Summary: ShopInventoryParser Directional Search Bug

**Date**: 2026-01-15  
**Investigator**: Claude Sonnet 4.5  
**Save File**: /app/tests/game_files/saves/1768403991

## The Issue

The "missing shop" in dragondor with bocman/monstera/bear_white/demonologist is NOT actually missing from the parser. It was found as `m_portland_dark_6533`, but extracted with WRONG inventory data (skeleton/zombie/ghost2).

## Root Cause

The parser searches BACKWARDS from shop identifiers, but the save file structure places inventory sections AFTER the shop identifier. This causes the parser to:
1. Find inventory from the PREVIOUS shop instead of the current shop
2. Return empty inventory when no sections exist before the identifier

## Evidence

**Verification Script Output:**
```
Position 668370: .shopunits with skeleton/70/zombie/20/ghost2/2  (WRONG)
Position 668575: itext_m_portland_dark_6533 identifier
Position 669413: .shopunits with bocman/1460/monstera/250/...   (CORRECT)

Parser searches BACKWARDS → finds skeleton/zombie/ghost2
Correct data is FORWARDS → bocman/monstera/bear_white/demonologist
```

## Files Generated

1. `README.md` - Full investigation with detailed analysis
2. `PROPOSAL.md` - Proposed fix with implementation details  
3. `verify_issue.py` - Runnable script demonstrating the bug
4. `decompressed_data.bin` - Raw save file data for reference

## Recommended Action

Modify ShopInventoryParser to search BOTH directions from shop identifier:
- Check forward for sections (preferred)
- Fallback to backward search if forward yields nothing
- Validate section ownership in both directions

See PROPOSAL.md for detailed implementation approach.

## Impact Assessment

- Affects multiple shops throughout the save file
- Shop identifiers appear 9-13 times each in the file
- Parser deduplication keeps first occurrence found
- Depending on which occurrence and section placement, data may be wrong or empty

## Verification

Run verification script to see the issue:
```bash
docker exec kbtracker_app python /app/tests/research/save_decompiler/kb_shop_extractor/2026-01-15/verify_issue.py
```

Expected output shows:
- Raw data contains bocman/1460
- Shop identifier: m_portland_dark_6533
- Parser extracts skeleton/zombie/ghost2 (WRONG)
- Correct data is 885 bytes AFTER identifier

