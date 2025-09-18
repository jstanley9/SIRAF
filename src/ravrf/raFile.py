import io
import os
import pathlib
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

    def Add(self, data: bytearray, padding: int = 0) -> int:
        if self.__file is None:
            raise IOError("File is not open")
        if data is None or len(data) == 0:
            raise ValueError("Data cannot be None or empty")
        
        requiredSize = self.__calcRequiredLength(data, padding)
        location, availableHeading = self.__findAvailableSpace(requiredSize)
        recordSize = self.__updateAvailableList(location, availableHeading, requiredSize)
        record = self.__buildRecord(BlockType.DATA_BLOCK, data, requiredSize, recordSize)
        self.__write_data(location, record)

        return location

    def Close(self) -> None:
        if self.__file is not None:
            self.flush()
            self.__file.close()
            self.__file = None
            self.__config = None

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

    def __adjustAvaliableLinks(self, prevAvailable: int, nextAvailable: int, availableLocation: int):
        if nextAvailable > 0:
            nextHead = self.__readHead(nextAvailable, expectedType = BlockType.AVAILABLE)
            nextHead.prev_available = availableLocation if availableLocation > 0 else prevAvailable
            self.__write_data(nextAvailable, nextHead.encode())

        if prevAvailable > 0:
            prevHead = self.__readHead(prevAvailable, expectedType = BlockType.AVAILABLE)
            prevHead.next_available = availableLocation if availableLocation > 0 else nextAvailable
            self.__write_data(prevAvailable, prevHead.encode())
        else:
            self.__config.first_available_address = availableLocation
            self.__write_data(0, self.__config.encode())

    def __buildRecord(self, blockType: BlockType, data: bytearray, requiredSize: int, 
                      recordSize: int) -> bytearray:
        dataLength = len(data)
        padding = requiredSize - dataLength
        
        headBlock = HeadBlock(blockType, requiredSize, dataLength, padding, 0)
        endBlock = EndBlock(requiredSize, blockType)

        return bytearray(headBlock.encode() + data + bytearray(b"\x00" * padding) + endBlock.encode())

    def __calcRequiredLength(self, data: bytearray, padding: int) -> int:
        return len(data) + padding

    def __findAvailableSpace(self, requiredSize: int) -> tuple[int, HeadBlock]:
        if self.__file is None:
            raise IOError("File is not open")
        if requiredSize <= 0:
            raise ValueError("Required size must be positive")

        location = self.__config.first_available_address
        bestFitLocation = 0
        bestFitSize = sys.maxsize
        bestfitHead = None

        while location > 0:
            availHead = self.__readHead(location, expectedType = BlockType.AVAILABLE)
            recordSize = availHead.record_size
            if recordSize >= requiredSize and recordSize < bestFitSize:
                if recordSize == requiredSize:
                    return location, availHead
                bestFitLocation = location
                bestFitSize = recordSize
                bestfitHead = availHead

        if bestFitLocation == 0:
            return self._size, HeadBlock.initAvailable(requiredSize, 0, 0, 0)
        else:
            return bestFitLocation, bestfitHead

    def __read(self, recordId: int, length: int) -> bytearray:
        if self.__file is None:
            raise IOError("File is not open")
        if recordId < 0:
            raise ValueError("Record ID must be non-negative")
        if length <= 0:
            raise ValueError("Read length must be positive")
        
        self.__file.seek(recordId, io.SEEK_SET)
        head = bytearray(length)
        self.__file.readinto(head)
        return head

    def __readHead(self, recordId: int, expectedType: BlockType) -> HeadBlock:
        headSize = HeadBlock.getStorageSize()
        headData = self.__read(recordId, headSize)
        headBlock = HeadBlock.decode(headData)

        if headBlock.block_type != expectedType:
            raise ValueError(f"Expected block type {expectedType}, but found {headBlock.block_type}")

        return headBlock
    
    def __updateAvailableList(self, location: int, availableHeading: HeadBlock, 
                              requiredSize: int) -> int:
        prevAvailable = availableHeading.prev_available
        nextAvailable = availableHeading.next_available
        dataAreaSize = availableHeading.record_size
        totalSize = requiredSize + HeadBlock.getStorageSize() + EndBlock.getStorageSize()

        if dataAreaSize > totalSize:
            # Split the available block
            remainingSize = dataAreaSize - requiredSize
            newAvailableHead = HeadBlock.initAvailable(remainingSize, prevAvailable, nextAvailable, 0)
            newAvailableLocation = location + requiredSize + HeadBlock.getStorageSize() + EndBlock.getStorageSize()
            self.__write_data(newAvailableLocation, newAvailableHead.encode())
            self.__adjustAvaliableLinks(prevAvailable, nextAvailable, newAvailableLocation)
            return requiredSize
        
        self.__adjustAvaliableLinks

    def __write_data(self, location: int, record: bytearray) -> None:
        if self.__file is None:
            raise IOError("File is not open")
        if location < 0:
            raise ValueError("Location must be non-negative")
        if record is None or len(record) == 0:
            raise ValueError("Record cannot be None or empty")

        self.__file.seek(location, io.SEEK_SET)
        self.__file.write(record)
        self.__file.flush()
        end_position = location + len(record)
        if end_position > self.__size:
            self.__size = end_position

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
    test_file = pathlib.Path("test.ravrf").absolute()
    print(f"Test file: {test_file}")
    if os.path.exists(test_file):
        os.remove(test_file)
    rave = raFile.Create(pathlib.Path(test_file))
    try:
        add_the_first_record()
        print(f"ra file: {rave}")
    finally:
        rave.Close()

def add_the_first_record(fileDescriptor):
    data = bytearray(b"Hello, World!")
    record_id = fileDescriptor.Add(data)
    print(f"Added record at ID: {record_id}")
    read_data, data_size, record_size = rave._raFile__read(record_id, expectedType = BlockType.DATA_BLOCK)
    print(f"Read data size: {data_size}, record size: {record_size}, data: {read_data}")


if __name__ == "__main__":
    main()    