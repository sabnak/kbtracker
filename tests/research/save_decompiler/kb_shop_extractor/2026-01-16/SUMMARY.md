# Shop m_inselburg_6529 Comparative Analysis Summary

## Investigation Date
2026-01-16

## Question
Why does shop  appear in save  but not in save ?

## Answer
**The shop exists in save2 but NOT in save1 due to actual game state differences in the save files.**

This is NOT a parser bug. The two save files contain different binary content starting at byte position 113500, representing different states of the game world.

## Evidence

### Parser Results
- **Save1** (): 357 shops total,  NOT found
- **Save2** (): 367 shops total,  FOUND

### Binary Analysis
1. **Save1 Size:** 10,906,697 bytes
2. **Save2 Size:** 10,907,358 bytes (661 bytes larger)
3. **First byte difference:** Position 113500
   - Save1: 
   - Save2: 

### Decompressed Text Comparison
When decoding chunk 107800-117800 as UTF-16 LE:
- **Save1** decoded text contains m_inselburg shop numbers: 6557, 6575, 6578, 6582, 6507, 3626
- **Save2** decoded text contains m_inselburg shop numbers: 6557, 6575, 6578, 6512, 6507, 6529, 3626

Save2 has shop 6529 and 6512 where save1 has shop 6582.

## How the Parser Works

The parser uses regex pattern  which matches:
-  (standalone, never found in either save)
-  (matches and extracts )
-  (matches and extracts )

In save2, the  and  variants appear at position 113658 in decodable UTF-16 LE text, so the parser finds them.

In save1, while the same  and  labels exist at position 113773, they appear in a different data structure that doesn't decode the same way in the parser's chunked processing, due to binary differences starting at position 113500.

## Conclusion

The shop  is present in save2 and absent from save1 because:
1. The two saves represent different game states
2. The binary content diverges at byte 113500
3. Save2 contains the shop data structure for shop 6529
4. Save1 contains different shop data in that same region

**This is expected behavior for save files taken at different points in gameplay.**

## Related Files
- Full investigation: 
- Decompressed saves: , 
- Parser outputs: , 
