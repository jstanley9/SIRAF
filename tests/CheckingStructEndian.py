import struct

def main():
    value: int = 0x11223344

    data = struct.pack('>i8', value)
    print(data)


main()