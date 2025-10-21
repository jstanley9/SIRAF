import io
import os
import pathlib
import re
import string
import sys

from config import RavrfConfig
from blockDescriptor import BlockType, HeadBlock, EndBlock
from enum import IntEnum

def main():
    filePath = getFilePath()
    textPath = getTextPath(filePath)    
    evaluateRAFile(filePath, textPath)
    
def evaluateRAFile(filePath: pathlib.Path, textPath: pathlib.Path):
    pattern = f"[^{re.escape(string.printable)}]"
    inputSize = os.path.getsize(filePath)
    with io.BufferedRandom(io.FileIO(filePath, mode = "r+b", closefd = True), buffer_size = 4096) as inputFile, \
        io.open(textPath, "w", encoding="utf-8", newline="\n") as textFile:

        textFile.write(f"RAVRF Lint Report for {filePath.name}\nFile Size: {inputSize:,} bytes\n\n")

        location = 0
        inputFile.seek(location)
        readSize = RavrfConfig.getStorageSize()
        config = inputFile.read(readSize)
        configuration = RavrfConfig.decode(config)
        textFile.write(f"Configuration: {configuration}\n\n")

        headBlockSize = HeadBlock.getStorageSize()
        endBlockSize = EndBlock.getStorageSize()
        location += readSize
        blockNumber = 0
        while location < inputSize:
            blockNumber += 1

            inputFile.seek(location)
            descriptorBytes = inputFile.read(headBlockSize)
            if len(descriptorBytes) < headBlockSize:
                textFile.write(f"ERROR: Incomplete block descriptor at location {location:,}\n")
                textFile.write(f"    Expected {readSize}, got {len(descriptorBytes)} [{descriptorBytes}]\n")
                break
            if BlockType(descriptorBytes[0]) not in (BlockType.DATA_BLOCK, BlockType.META_BLOCK, BlockType.AVAILABLE):
                textFile.write(f"ERROR: Invalid block type {descriptorBytes[0]} at location {location:,}  [{descriptorBytes}]\n")
                break
            
            headBlock = HeadBlock.decode(descriptorBytes)
            record_size = headBlock.record_size
            printData = True
            match headBlock.block_type:
                case BlockType.DATA_BLOCK:
                    headingString = expandDataHeader(headBlock, "Data Block")
                    data_size = headBlock.data_size
                case BlockType.META_BLOCK:
                    headingString = expandDataHeader(headBlock, "Meta Block")
                    data_size = headBlock.data_size
                case BlockType.AVAILABLE:  
                    headingString = expandAvailableHeader(headBlock)
                    printData = False
                case _: 
                    headingString = expandUnknownHeader(headBlock)
                    data_size = record_size

            textFile.write(f"{location:,}: {headingString}\n")

            location += headBlockSize
            textFile.write(f"    Data start location: {location:,}\n")
            if printData:
                inputFile.seek(location)
                dataBytes = inputFile.read(record_size)
                if len(dataBytes) < record_size:
                    textFile.write(f"    ERROR: Incomplete data size {location:,}\n")
                    textFile.write(f"           Expected {record_size}, got {len(dataBytes)} [{dataBytes}]")

                dataString = dataBytes.decode("utf-8", errors="replace")[:data_size]
                dataString = re.sub(pattern, "?", dataString)
                for i in range(0, len(dataString), 100):
                    textFile.write(f"    {dataString[i: i + 100]}\n")

            location += record_size
            inputFile.seek(location)
            endBytes = inputFile.read(endBlockSize)
            if len(endBytes) < endBlockSize:
                textFile.write(f"ERROR: Incomplete end block at location {location:,}\n")
                textFile.write(f"       Expected {endBlockSize}, got {len(endBytes)} [{endBytes}]")
                break

            endBlock = EndBlock.decode(endBytes)
            if endBlock.block_type != headBlock.block_type:
                textFile.write(f"ERROR: End block type {endBlock.block_type.name} does not match head block type {headBlock.block_type.name}\n")

            textFile.write(f"{location:,}: Block type = {endBlock.block_type}, record size {endBlock.record_size:,}\n\n")
            location += endBlockSize

        textFile.write(f"*/ End of file reached at location {location:,}\n")

def expandDataHeader(headBlock: HeadBlock, blockTypeName: str) -> str:
    return (f"{blockTypeName} record size {headBlock.record_size:,}, "
            f"data size {headBlock.data_size:,}, pad size {headBlock.open_size:,}")
    
def expandAvailableHeader(headBlock: HeadBlock) -> str:
    return (f"Available Block record size {headBlock.record_size:,}, "
            f"prev available {headBlock.prev_available:,}, next available {headBlock.next_available:,}")

def expandUnknownHeader(headBlock: HeadBlock) -> str:
    return (f"Unknown Block {headBlock.block_type}, record size {headBlock.record_size:,} "
            f"param1 {headBlock.prev_available:,}, param2 {headBlock.next_available:,}")


def getFilePath() -> pathlib.Path:
    if len(sys.argv) < 2:
        print("Usage: python ISAMLint.py <fileName>")
        sys.exit(1)
    fileName = sys.argv[1]
    filePath = pathlib.Path(fileName).absolute()
    return filePath

def getTextPath(filePath: pathlib.Path) -> pathlib.Path:  
    if not os.path.exists(filePath):
        print(f"File {filePath} not found.")
        sys.exit(1)
    textPath = filePath.with_suffix(".txt")
    return textPath

if __name__ == "__main__":
    main()    