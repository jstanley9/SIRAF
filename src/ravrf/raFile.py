import io
import pathlib
import struct
import sys

from config import RavrfConfig
from blockDescriptor import BlockType, HeadBlock, EndBlock


class raFile(io.BytesIO):
    __BUFFER_SIZE = 4096
    __DOT = "."
    __SUFFIX = ".ravrf"
    

    def __init__(self, path: pathlib.Path = None):
        self.__config: RavrfConfig = None
        self.__file: io.BufferedRandom = None
        self.__path: pathlib.Path = None
        self.__size: int = 0

        if path:
            self.setPath(path)

    def __str__(self):
        return f"raFile(path={self.__path}, size={self.__size}, config={self.__config})"            

    def setPath(self, path: pathlib.Path):
        if path.name.startswith(self.__DOT):
            raise ValueError("File name cannot start with a dot")
        
        suffix = path.suffix.lower()
        if len(suffix) == 0:
            self.__path = path.with_suffix(self.__SUFFIX)
        else:
            if suffix != self.__SUFFIX:
                raise ValueError(f"File suffix must be '{self.__SUFFIX}' or None")
            self.__path = path

        if self.__path.exists():
            if not self.__path.is_file():
                raise IsADirectoryError(f"Path '{self.__path}' is not a file")
            self.__size = self.__path.stat().st_size

    def Open(self, path: pathlib.Path = None):
        if path is not None:
            self.setPath(path)

        if self.__path is None:
            raise ValueError("File path is not set")
        
        self.__file = io.BufferedRandom(io.FileIO(self.__path, mode = "r+b", closefd = True), 
                                                  buffer_size = self.__BUFFER_SIZE)
        
        self.__file.seek(0, io.SEEK_SET)
        config = self.__file.read(RavrfConfig.getStorageSize())
        self.__config = RavrfConfig.decode(config)

    def Close(self) -> None:
        if self.__file is not None:
            self.flush()
            self.__file.close()
            self.__file = None
            self.__config = None


    def Add(self, data: bytearray) -> int:
        if self.__file is None:
            raise IOError("File is not open")
        if data is None or len(data) == 0:
            raise ValueError("Data cannot be None or empty")
        
        record, requiredSize = self.__buildRecord(data)
        location, availSize, previousAvailable, nextAvailable = self.__findAvailableSpace(requiredSize)
        self.__updateAvailableList(location, availSize, previousAvailable, nextAvailable, requiredSize)
        self.__write_data(location, record)

        return location

        
    def __read(self, recordId: int, expectedType: BlockType = BlockType.DATA_BLOCK) -> bytearray:
        if self.__file is None:
            raise IOError("File is not open")
        if recordId < 0:
            raise ValueError("Record ID must be non-negative")
        if recordId < RavrfConfig.getStorageSize(): 
            raise ValueError(f"Record ID ({recordId}) must be at least {RavrfConfig.getStorageSize()}")
        if recordId > self.__size:
            raise ValueError(f"Record ID ({recordId}) is past EOF ({self.__size})")
        
        self.__file.seek(recordId, io.SEEK_SET)
        head = bytearray(HeadBlock.getStorageSize())
        self.__file.readinto(head)
        headBlock = HeadBlock.decode(head)

        match headBlock.block_type: 
            case BlockType.AVAIL_01_BYTE | BlockType.AVAIL_02_BYTE | BlockType.AVAIL_03_BYTE | \
                 BlockType.AVAIL_04_BYTE | BlockType.AVAIL_05_BYTE | BlockType.AVAIL_06_BYTE | \
                 BlockType.AVAIL_07_BYTE | BlockType.AVAIL_08_BYTE | BlockType.AVAIL_09_BYTE | \
                 BlockType.AVAIL_10_BYTE | BlockType.AVAIL_11_BYTE | BlockType.AVAIL_12_BYTE | \
                 BlockType.AVAIL_MIN_FULL_FENCE:
                if expectedType != BlockType.AVAILABLE:
                    raise ValueError(f"Record is not an Available block: value={headBlock.block_type.value}")
                recordSize = headBlock.block_type.value
                dataSize = 0
            case BlockType.AVAILABLE:
                if expectedType != BlockType.AVAILABLE:
                    raise ValueError(f"Record is not an Available block: value={headBlock.block_type.value}")
                recordSize = headBlock.data_length
                remainder = recordSize - HeadBlock.getStorageSize() - EndBlock.getStorageSize()
                dataSize = 8 if remainder >= 8 else 0
            case BlockType.META_BLOCK | BlockType.DATA_BLOCK:
                if expectedType != headBlock:
                    expected = "DATA_BLOCK" if expectedType == BlockType.DATA_BLOCK else "META_BLOCK"
                    raise ValueError(f"Record is not {expected}: value={headBlock.block_type}")
                recordSize = headBlock.data_length
                dataSize = recordSize
            case _:
                raise ValueError(f"Invalid block type: {headBlock.block_type}[{recordId}]: Expected={expectedType}")

        endAddress = self.__file.tell() + remainder
        if endAddress > self.__size:
            raise IOError(f"Read past EOF ({self.__size}): Id={recordId}, Size={recordSize}, End={endAddress}")

        if dataSize > 0:
            data = bytearray(dataSize)
            return self.__file.readinto(data), dataSize, recordSize
        else:
            return None, dataSize, recordSize
    
    def __buildRecord(self, blockType: BlockType, data: bytearray) -> tuple[bytearray, int]:
        dataLength = len(data)
        if dataLength == 0:
            raise ValueError("Data cannot be empty")
        
        headBlock = HeadBlock(block_type = blockType, data_length = dataLength, checksum = 0)
        endBlock = EndBlock(data_length = dataLength, block_type = blockType)

        record = bytearray(headBlock.encode() + data + endBlock.encode())
        requiredSize = len(record)
        return record, requiredSize
    
    def __findAvailableSpace(self, requiredSize: int) -> tuple[int, int, int, int]:
        # Returns (location, availSize, previousAvailable, nextAvailable)
        if self.__file is None:
            raise IOError("File is not open")
        if requiredSize <= 0:
            raise ValueError("Required size must be positive")

        location = self.__config.first_available_address
        bestFitLocation = 0
        bestFitSize = sys.maxsize

        while location > 0:
            data, dataSize, recordSize = self.__read(location, expectedType = BlockType.AVAILABLE)
            if dataSize == 8 and recordSize >= requiredSize and recordSize < bestFitSize:
                bestFitLocation = location
                bestFitSize = recordSize
                if recordSize == requiredSize:
                    break
            _, location = struct.unpack(">II", data)

        if bestFitLocation == 0:
            return self._size, 0, 0, 0
        else:
            data, dataSize, recordSize = self.__read(bestFitLocation, expectedType = BlockType.AVAILABLE)
            previousAvailable, nextAvailable = struct.unpack(">II", data)
            return bestFitLocation, recordSize, previousAvailable, nextAvailable
            

    def __del__(self):
        self.Close()

    @classmethod
    def Create(cls, path: pathlib.Path):
        print(f"Enter Create: path = {path}")
        with io.open(path, "x+b") as file:
            config = RavrfConfig()
            file.write(config.encode())
            file.flush()

        ravrFile = raFile(path)
        ravrFile.Open()
        return ravrFile
    

def main():
    print("Enter main")
    object = raFile.Create(pathlib.Path("test.ravrf"))
    print(f"ra file: {object}")

if __name__ == "__main__":
    main()    