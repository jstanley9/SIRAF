import io
import os
import pathlib

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

    def setPath(self, path: pathlib.Path) -> None:
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

    def Add(self, data: bytes, padding: int = 0) -> int:
        if self.__file is None:
            raise IOError("File is not open")
        if data is None or len(data) == 0:
            raise ValueError("Data cannot be None or empty")
        if isinstance(data, bytes):
            return self.__addRecord(data, padding, BlockType.DATA_BLOCK)
        
        return self.__addRecord(bytes(data), padding, BlockType.DATA_BLOCK)

    def Close(self) -> None:
        if self.__file is not None:
            self.flush()
            self.__file.close()
            self.__file = None
            self.__config = None

    def Delete(self, recordId: int) -> None:
        if self.__file is None:
            raise IOError("File is not open")
        if recordId < RavrfConfig.getStorageSize():
            raise ValueError("Record ID is invalid")

        headBlock = self.__readAnyHead(recordId)
        if headBlock.block_type not in (BlockType.DATA_BLOCK, BlockType.META_BLOCK):
            raise ValueError(f"Record ID {recordId} is not a data or meta block. It is {headBlock.block_type}")
        
        self.__deleteRecord(recordId, headBlock)
        if headBlock.block_type != BlockType.META_BLOCK:
            self.__config.meta_address = 0
            self.__write_data(0, self.__config.encode())
    
    def GetMeta(self) -> bytes:
        if self.__config is None:
            raise IOError("File is not open")
        
        metaRREF = self.__config.meta_address
        if metaRREF == 0:
            return bytes(0)
        
        return self.__readData(metaRREF, BlockType.META_BLOCK)

    def Open(self, path: pathlib.Path = None) -> None:
        if path is not None:
            self.setPath(path)

        if self.__path is None:
            raise ValueError("File path is not set")
        
        self.__file = io.BufferedRandom(io.FileIO(self.__path, mode = "r+b", closefd = True), 
                                                  buffer_size = self.__BUFFER_SIZE)
        
        self.__file.seek(0, io.SEEK_SET)
        config = self.__file.read(RavrfConfig.getStorageSize())
        self.__config = RavrfConfig.decode(config)

    def PutMeta(self, data: bytes, padding: int = 0) -> None:
        if self.__config is None:
            raise IOError("File is not open")
        if data is None:
            raise ValueError("Data cannot be None")
        
        padding = int(padding)
        requiredSize = self.__calcRequiredLength(data, padding)
        metaRREF = self.__config.meta_address
        if metaRREF == 0:
            metaRREF = self.__addRecord(data, padding, BlockType.META_BLOCK)
            self.__config.meta_address = metaRREF
            self.__write_data(0, self.__config.encode())
        else:
            headBlock = self.__readHead(metaRREF, expectedType = BlockType.META_BLOCK)
            if headBlock.record_size >= requiredSize:
                record = self.__buildRecord(BlockType.META_BLOCK, data, headBlock.record_size)
                self.__write_data(metaRREF, record)
            else:
                newMetaRREF = self.__addRecord(data, padding, BlockType.META_BLOCK)
                self.__config.meta_address = metaRREF
                self.__write_data(0, self.__config.encode())
                self.__config.meta_address = newMetaRREF
                self.__write_data(0, self.__config.encode())
                self.__deleteRecord(metaRREF, headBlock)

    def ReadData(self, recordRREF: int) -> bytes:
        return self.__readData(recordRREF)

    def Save(self, recordRREF: int, record: str, padding: int = 0) -> int:
        if self.__config is None:
            raise IOError("File is not open")
        if record is None:
            raise ValueError("Record cannot be None")

        if isinstance(record, str):
            data = bytes(record, 'utf-8')
        else:
            data = bytes(record)

        requiredSize = self.__calcRequiredLength(data, padding)
        if recordRREF == 0:
            return self.Add(data, padding, BlockType.DATA_BLOCK)
        
        headBlock = self.__readHead(recordRREF, expectedType = BlockType.DATA_BLOCK)
        if headBlock.record_size >= requiredSize:
            record = self.__buildRecord(BlockType.DATA_BLOCK, data, headBlock.record_size)
            self.__write_data(recordRREF, record)
            return recordRREF
        
        newRecordRREF = self.__addRecord(data, padding, BlockType.DATA_BLOCK)
        self.Delete(recordRREF)
        return newRecordRREF
    
    def __addRecord(self, data: bytes, padding: int = 0, blockType: BlockType = BlockType.DATA_BLOCK) -> int:
        requiredSize = self.__calcRequiredLength(data, padding)
        BlockRREF, availableHeading = self.__findAvailableSpace(requiredSize)
        recordSize, RecordRREF = self.__updateAvailableList(BlockRREF, availableHeading, requiredSize)
        record = self.__buildRecord(blockType, data, recordSize)
        self.__write_data(RecordRREF, record)

        return RecordRREF

    def __adjustAvailableLinks(self, prevAvailableRREF: int, nextAvailableRREF: int, availableRREF: int):
        if nextAvailableRREF > 0:
            nextHead = self.__readHead(nextAvailableRREF, expectedType = BlockType.AVAILABLE)
            nextHead.prev_available = availableRREF if availableRREF > 0 else prevAvailableRREF
            self.__write_data(nextAvailableRREF, nextHead.encode())
            if nextHead.prev_available == 0:
                self.__config.first_available_address = nextAvailableRREF
                self.__write_data(0, self.__config.encode())

        if prevAvailableRREF > 0:
            prevHead = self.__readHead(prevAvailableRREF, expectedType = BlockType.AVAILABLE)
            prevHead.next_available = availableRREF if availableRREF > 0 else nextAvailableRREF
            self.__write_data(prevAvailableRREF, prevHead.encode())
        elif prevAvailableRREF== 0:
            self.__config.first_available_address = availableRREF if availableRREF > 0 else nextAvailableRREF
            self.__write_data(0, self.__config.encode())

    def __buildRecord(self, blockType: BlockType, data: bytes, requiredSize: int) -> bytes:
        dataLength = len(data)
        padding = requiredSize - dataLength
        
        headBlock = HeadBlock(blockType, requiredSize, dataLength, padding, 0)
        endBlock = EndBlock(requiredSize, blockType)

        return bytes(headBlock.encode() + data + bytes(b"\x00" * padding) + endBlock.encode())

    def __calc_end_block_RREF(self, recordRREF: int, dataSize: int) -> int:
        return recordRREF + HeadBlock.getStorageSize() + dataSize
      
    def __calc_next_record_RREF(self, recordRREF: int, dataSize: int) -> int:
        return recordRREF + self.__calc_record_size(dataSize)
    
    def __calc_record_size(self, dataSize: int) -> int:
        return dataSize + HeadBlock.getStorageSize() + EndBlock.getStorageSize()

    def __calcRequiredLength(self, data: bytes, padding: int) -> int:
        return len(data) + padding

    def __deleteRecord(self, recordRREF: int, headBlock: HeadBlock) -> None:

        if self.__config is None:
            raise IOError("File is not open")        

        headBlock.block_type = BlockType.AVAILABLE
        recordSize = headBlock.record_size

        nextRREF = self.__calc_next_record_RREF(recordRREF, recordSize)
        if nextRREF < self.__size:
            nextHead = self.__readAnyHead(nextRREF)
            if nextHead.block_type == BlockType.AVAILABLE:
                # Merge with next available
                recordSize += self.__calc_record_size(nextHead.record_size)
                headBlock.record_size = recordSize
                self.__adjustAvaliableLinks(nextHead.prev_available, nextHead.next_available, 0)

        prevEndRREF = recordRREF - EndBlock.getStorageSize()
        if prevEndRREF >= RavrfConfig.getStorageSize():
            prevEndBlock = self.__readEndBlock(prevEndRREF)
            if prevEndBlock.block_type == BlockType.AVAILABLE:
                prevTotalSize = self.__calc_record_size(prevEndBlock.record_size)
                availableRREF = recordRREF - prevTotalSize
                prevAvailableHead = self.__readHead(availableRREF, expectedType = BlockType.AVAILABLE)
                prevAvailableHead.record_size += recordSize + headBlock.getStorageSize() + EndBlock.getStorageSize()
                availableSize = prevAvailableHead.record_size
                self.__write_data(availableRREF, prevAvailableHead.encode())
                self.__write_data(self.__calc_end_block_RREF(availableRREF, availableSize), 
                                  EndBlock(availableSize, BlockType.AVAILABLE).encode())
                return
        
        headBlock.prev_available = 0
        headBlock.next_available = self.__config.first_available_address
        availableSize = headBlock.record_size
        self.__write_data(recordRREF, headBlock.encode())
        self.__write_data(self.__calc_end_block_RREF(recordRREF, availableSize), 
                                                     EndBlock(availableSize, BlockType.AVAILABLE).encode())
        self.__config.first_available_address = recordRREF
        nextAvailRREF = headBlock.next_available
        if nextAvailRREF > 0:
            self.__setPrevAvailable(nextAvailRREF, id)
        self.__write_data(0, self.__config.encode())

    def __findAvailableSpace(self, requiredSize: int) -> tuple[int, HeadBlock]:
        if self.__file is None:
            raise IOError("File is not open")
        if requiredSize <= 0:
            raise ValueError("Required size must be positive")

        availableRREF = self.__config.first_available_address
        saved_RREF = 0

        while availableRREF > 0:
            availHead = self.__readHead(availableRREF, expectedType = BlockType.AVAILABLE)
            recordSize = availHead.record_size
            if recordSize >= requiredSize:
                return availableRREF, availHead
            if availableRREF + self.__calc_record_size(recordSize) >= self.__size:
                saved_RREF = availableRREF
            availableRREF = availHead.next_available

        if saved_RREF > 0:
            self.__size = saved_RREF     ## Adjust EOF to remove trailing available space
                                         ## We already know that the trailing available block is too small
                                         ## So we will be expanding the file size
        
        return self.__size, HeadBlock.initAvailable(requiredSize, 0, 0, 0)

    def __read(self, recordRREF: int, length: int) -> bytes:
        if self.__file is None:
            raise IOError("File is not open")
        if recordRREF < 0:
            raise ValueError("Record ID must be non-negative")
        if length <= 0:
            raise ValueError("Read length must be positive")
        
        self.__file.seek(recordRREF, io.SEEK_SET)
        record = bytearray(length)
        self.__file.readinto(record)
        return bytes(record)
    
    def __readAnyHead(self, recordRREF: int) -> HeadBlock:
        headSize = HeadBlock.getStorageSize()
        headData = self.__read(recordRREF, headSize)
        return HeadBlock.decode(headData)
    
    def __readData(self, recordRREF: int, blockType: BlockType = BlockType.DATA_BLOCK) -> bytes:
        headBlock = self.__readHead(recordRREF, expectedType = blockType)
        dataSize = headBlock.data_size
        dataStart = recordRREF + HeadBlock.getStorageSize()
        data = self.__read(dataStart, dataSize)
        return data

    def __readEndBlock(self, recordRREF: int) -> EndBlock:
        endBlockData = self.__read(recordRREF, EndBlock.getStorageSize())
        return EndBlock.decode(endBlockData)
        
    def __readHead(self, recordRREF: int, expectedType: BlockType) -> HeadBlock:
        headBlock = self.__readAnyHead(recordRREF)

        if headBlock.block_type != expectedType:
            raise ValueError(f"Expected block type {expectedType}, but found {headBlock.block_type}")

        return headBlock
    
    def __setPrevAvailable(self, nextAvailRREF: int, availableRREF: int) -> None:
        nextHead = self.__readHead(nextAvailRREF, expectedType = BlockType.AVAILABLE)
        nextHead.prev_available = availableRREF
        self.__write_data(nextAvailRREF, nextHead.encode())

    def __updateAvailableList(self, availableRREF: int, availableHeading: HeadBlock, 
                              requiredSize: int) -> {int, int}:
        prevAvailableRREF = availableHeading.prev_available
        nextAvailableRREF = availableHeading.next_available
        dataAreaSize = availableHeading.record_size
        if dataAreaSize >= requiredSize:
            totalSize = requiredSize + HeadBlock.getStorageSize() + EndBlock.getStorageSize()

            if dataAreaSize > totalSize: 
                # Split the available block
                # The new record will go after this remaining available block
                # This method reduces IOs since the prev and next locations do not change
                remainingSize = dataAreaSize - totalSize
                availableHeading.record_size = remainingSize
                self.__write_data(availableRREF, availableHeading.encode())
                endEREF = self.__calc_end_block_RREF(availableRREF, remainingSize)
                self.__write_data(endEREF, EndBlock(remainingSize, BlockType.AVAILABLE).encode())
                return requiredSize, endEREF + EndBlock.getStorageSize()
            else:
                requiredSize = dataAreaSize
                self.__adjustAvailableLinks(prevAvailableRREF, nextAvailableRREF, 0)
        else:
            self.__adjustAvailableLinks(prevAvailableRREF, nextAvailableRREF, 0)
    
        return requiredSize, availableRREF

    def __write_data(self, recordRREF: int, record: bytes) -> None:
        if self.__file is None:
            raise IOError("File is not open")
        if recordRREF < 0:
            raise ValueError("Location must be non-negative")
        if record is None or len(record) == 0:
            raise ValueError("Record cannot be None or empty")

        self.__file.seek(recordRREF, io.SEEK_SET)
        self.__file.write(record)
        self.__file.flush()
        end_position = recordRREF + len(record)
        if end_position > self.__size:
            self.__size = end_position

    def __del__(self):
        self.Close()

    @classmethod
    def Create(cls, path: pathlib.Path) -> "raFile":
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
    rave = raFile.Create(test_file)
    try:
        listOfIds = []
        listOfIds.append(add_the_first_record(rave))
        print(f"ra file: {rave}")
        setupMeta(rave)
    finally:
        rave.Close()

def add_the_first_record(fileDescriptor) -> int:
    data = bytes(b"Hello, World!")
    record_RREF = fileDescriptor.Add(data)
    print(f"Added record at RREF: {record_RREF}")
    read_data = fileDescriptor.ReadData(record_RREF)
    print(f"Read data: {read_data}")
    return record_RREF

def setupMeta(fileDescriptor) -> None:
    schema = getSchema()
    lenSchema = len(schema)
    fileDescriptor.PutMeta(bytes(schema, "utf-8"), lenSchema / 10)
    retrievedSchema = fileDescriptor.GetMeta().decode("utf-8")
    if schema != retrievedSchema[:lenSchema]:
        print("ERROR: Retrieved schema does not match stored schema")
        print(f"Stored:    {schema}")
        print(f"Retrieved: {retrievedSchema}")

def getSchema() -> str:    
    return """Schema {
"fields": ["last_name", "first_name", "middle_initial", "nick_name", "birth_date", "descriptor"]
"key": ["last_name", "first_name"]
"config": {"case_sensitive": false, "pad": 10,}
}"""



if __name__ == "__main__":
    main()    