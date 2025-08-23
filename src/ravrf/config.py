import struct
from checksum import calc_16bit_checksum

class RavrfConfig:
    __MAGIC = b"/~ ravrf ~/"
    __CURRENT_VERSION = 1

    def __init__(self, version: int = __CURRENT_VERSION, meta_address: int = 0, first_available_address: int = 0, checksum: int = 0):
        self.__version = version
        self.meta_address = meta_address
        self.first_available_address = first_available_address

        calc_checksum = calc_16bit_checksum([self._version, self.meta_address, self.first_available_address])
        if checksum == 0:
            self.__checksum = calc_checksum
        elif checksum != calc_checksum:
            raise ValueError("Configuration checksum does not match calculated checksum")
        else:
            self.__checksum = checksum

    def encode(self) -> bytearray:
        # Format: 11s B I I H (11 bytes string, 1 byte, 4 bytes, 4 bytes, 2 bytes)
        return bytearray(struct.pack(
            "<11sBIIH", self.__MAGIC, self.__version, self.meta_address, self.first_available_address, self.__checksum
        ))
    
    def __getChecksum(self):
        return calc_16bit_checksum([self._version, self.meta_address, self.first_available_address]) 

    @classmethod
    def decode(cls, data: bytearray):
        if len(data) != 22:
            raise ValueError("Bytearray must be exactly 22 bytes")
        magic, version, meta_address, first_available_address, checksum = struct.unpack("<11sBIIH", data)
        if magic != cls.__MAGIC:
            raise ValueError("Invalid magic header")
        return cls(version, meta_address, first_available_address, checksum)