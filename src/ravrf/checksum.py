import struct

def calc_16bit_checksum(items) -> int:
    """
    Calculates a 16-bit checksum from a list of strings, integers, and byte strings.
    Integers are packed as 4-byte little-endian before summing.
    Strings are encoded as UTF-8.
    """
    total = 0
    for item in items:
        if isinstance(item, int):
            total += sum(struct.pack('<I', item))
        elif isinstance(item, str):
            total += sum(item.encode('utf-8'))
        elif isinstance(item, (bytes, bytearray)):
            total += sum(item)
        else:
            raise TypeError("Only integers, strings, and byte strings are supported")
        
    total = total & 0xFFFF
    if total == 0:
        return 13  # Never return zero as checksum
    return total