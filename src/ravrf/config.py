import struct
from checksum import calc_16bit_checksum

class RavrfConfig:
    __MAGIC = b"/~ ravrf ~/"
    __CURRENT_VERSION = 1
    __STRUCT_MASK = ">11sBIIH"  # 11 bytes string, 1 byte, 4 bytes, 4 bytes, 2 bytes

    def __init__(self, version: int = __CURRENT_VERSION, meta_address: int = 0, first_available_address: int = 0, checksum: int = 0):
        self.__version = version
        self.meta_address = meta_address
        self.first_available_address = first_available_address

        calc_checksum = self.__getChecksum()
        all_zero = (checksum == 0 and meta_address == 0 and first_available_address == 0)
        if not (all_zero or checksum == calc_checksum):
            raise ValueError(f"Configuration checksum ({checksum}) does not match calculated checksum ({calc_checksum})")

    def encode(self) -> bytearray:
        # Format: 11s B I I H (11 bytes string, 1 byte, 4 bytes, 4 bytes, 2 bytes)
        return bytearray(struct.pack(self.__STRUCT_MASK, 
                                     self.__MAGIC, self.__version, self.meta_address, self.first_available_address, self.__getChecksum()
        ))
    
    def __getChecksum(self):
        return calc_16bit_checksum([self.__version, self.meta_address, self.first_available_address]) 

    @classmethod
    def decode(cls, data: bytearray):
        if len(data) != 22:
            raise ValueError("Bytearray must be exactly 22 bytes")
        magic, version, meta_address, first_available_address, checksum = struct.unpack(cls.__STRUCT_MASK, data)
        if magic != cls.__MAGIC:
            raise ValueError("Invalid magic header")
        return cls(version, meta_address, first_available_address, checksum)
    
    @classmethod
    def getStorageSize(cls):
        return struct.calcsize(cls.__STRUCT_MASK)
    
