import os
import pathlib
import random
import sys

print(f"Current path {pathlib.Path.cwd()}")
srcPath = f"{pathlib.Path.cwd()}/src/ravrf"
print(f"Source path {srcPath}")
sys.path.append(srcPath)
import raFile
import ISAMLint as ISAM

def genData(id: int) -> str:
    datalen = random.randint(20, 100)
    data = '{' + f'"ID": {id}, "data": "{''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ", k=datalen))}"' + '}'
    return data

def printResults(filePath: pathlib.Path, textPath: pathlib.Path, baseName: str,
                 actionDesc: str, suffix: str) -> None:
    print(actionDesc)
    newTextPath = textPath.with_name(f"{baseName}_{suffix}{textPath.suffix}")
    ISAM.evaluateRAFile(filePath, newTextPath)

def createInitialRcords(filePath: pathlib.Path) -> list:
    recordList = []
    if os.path.exists(filePath):
        os.remove(filePath)

    
    print(f"Creating {filePath}")
    rave = raFile.raFile.Create(filePath)
    for recordId in range (1,11):
        data = genData(recordId)
        dataBytes = bytearray(data, 'utf-8')
        pad = 0 if random.randint(1,5) != 4 else int(len(data) / 4)
        id = rave.Add(dataBytes, pad)
        recordList.append(id)

    rave.Close()

    return recordList

def deleteARecord(filePath: pathlib.Path, deletedFirst: int) -> None:
    print(f"Deleting record {deletedFirst} from {filePath}")
    rave = raFile.raFile(filePath)
    rave.Open()
    rave.Delete(deletedFirst) 
    rave.Close()
    return

def addSomeRecords(filePath: pathlib.Path, recordList: list) -> list:
    rave = raFile.raFile(filePath)
    rave.Open()
    for id in range(3):
        data = genData(10 + id)
        dataBytes = bytearray(data, 'utf-8')
        pad = 0 if random.randint(1,5) != 4 else int(len(data) / 4)
        id = rave.Add(dataBytes, pad)
        recordList.append(id)
    rave.Close()
    return recordList

def deleteSpecificRecords(filePath: pathlib.Path, recordList: list, indexes: tuple) -> None:
    rave = raFile.raFile(filePath)
    rave.Open()
    for index in indexes:
        deletedId = recordList[index]
        print(f"Deleting record {deletedId} at index {index}")
        rave.Delete(deletedId)
    rave.Close()

def main():
    filePath = ISAM.getFilePath()

    recordList = []
    recordList = createInitialRcords(filePath)
    print(f"list [{recordList}]")

    textPath = ISAM.getTextPath(filePath)    
    ISAM.evaluateRAFile(filePath, textPath)

    baseName = textPath.stem

    index = 3
    deleted3 = recordList[index]
    deleteARecord(filePath, deleted3)
    deletedLast = recordList[-1]
    deleteARecord(filePath, deletedLast)
    printResults(filePath, textPath, baseName, "Deleted 3 and last record", "del3Last")

    deleteARecord(filePath, recordList[0])
    deleteARecord(filePath, recordList[4])
    printResults(filePath, textPath, baseName, "Deleted records 0 and 4", "del0And4")

    recordList = addSomeRecords(filePath, recordList)
    printResults(filePath, textPath, baseName, "Added some records", "AddSome")
    
    deleteSpecificRecords(filePath, recordList, (5, 7, 6))
    printResults(filePath, textPath, baseName, "Deleted records 5, 7, and 6  in that order", "del5_6_7")


if __name__ == "__main__":
    main()
else:
    print("This module is not intended to be imported")
