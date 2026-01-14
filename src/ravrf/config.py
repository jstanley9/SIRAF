import struct
from checksum import calc_16bit_checksum

class RavrfConfig:
    # Configuration record
    # 9 bytes - Identifier "/~ravrf~/": Identifies file as Random Access Variable Record File
    # 1 byte  - Version number
    # 4 bytes - Meta block address
    # 4 bytes - First available block address
    # 2 bytes - Checksum
    # 20 bytes - Expansion area for future use
    __MAGIC = b"/~ravrf~/"
    # 20 byte expansion area for future use
    __EXPANSION_AREA = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    __CURRENT_VERSION = 1
    __STRUCT_MASK = ">9sBIIH20s"  # 9 bytes string, 1 byte, 4 bytes, 4 bytes, 2 bytes 20 bytes

    def __init__(self, version: int = __CURRENT_VERSION, meta_address: int = 0, 
                 first_available_address: int = 0, checksum: int = 0):
        self.__version = version
        self.meta_address = meta_address
        self.first_available_address = first_available_address

        calc_checksum = self.__getChecksum()
        all_zero = (checksum == 0 and meta_address == 0 and first_available_address == 0)
        if not (all_zero or checksum == calc_checksum):
            attributes = f"({all_zero}, {checksum}, {meta_address}, {first_available_address})"
            raise ValueError(f"Configuration checksum {attributes} " + \
                             f"does not match calculated checksum ({calc_checksum})")
        
    def __str__(self):
        return f"RavrfConfig(version={self.__version}, meta_address={self.meta_address}, " + \
               f"first_available_address={self.first_available_address})"

    def encode(self) -> bytes:
        return bytes(struct.pack(self.__STRUCT_MASK, 
                                 self.__MAGIC, self.__version, self.meta_address, self.first_available_address, 
                                 self.__getChecksum(), self.__EXPANSION_AREA
        ))
    
    def __getChecksum(self) -> int:
        return calc_16bit_checksum([self.__version, self.meta_address, self.first_available_address]) 

    @classmethod
    def decode(cls, data: bytes) -> "RavrfConfig":
        if len(data) != cls.getStorageSize():
            raise ValueError("bytes must be exactly 22 bytes")
        magic, version, meta_address, first_available_address, checksum, _ = struct.unpack(cls.__STRUCT_MASK, data)
        if magic != cls.__MAGIC:
            raise ValueError("Invalid magic header")
        return cls(version, meta_address, first_available_address, checksum)
    
    @classmethod
    def getStorageSize(cls) -> int:
        return struct.calcsize(cls.__STRUCT_MASK)