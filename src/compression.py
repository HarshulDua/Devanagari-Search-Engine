import sys

class IndexCompressor:
    def __init__(self):
        pass

    def encode_vbyte_number(self, number):
        """Encodes a single integer using Variable Byte Code."""
        bytes_list = []
        while True:
            byte = number & 0x7F
            number >>= 7
            
            if number == 0:
                byte |= 0x80 # Set high bit to 1 to mark end
                bytes_list.insert(0, byte)
                break
            else:
                bytes_list.insert(0, byte) 
        return bytes(bytes_list)

    def gap_encode(self, doc_ids):
        """Converts a sorted list of DocIDs into gaps (e.g. [10, 15, 20] -> [10, 5, 5])."""
        if not doc_ids: return []
        
        try:
            # Extract number from filename (e.g., "0010_doc.txt" -> 10)
            ids = sorted([int(d.split('_')[0]) for d in doc_ids])
        except ValueError:
            return []

        gaps = [ids[0]]
        for i in range(1, len(ids)):
            gaps.append(ids[i] - ids[i-1])
        return gaps