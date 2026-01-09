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

def createInitialRecords(filePath: pathlib.Path) -> list:
    recordList = []
    if os.path.exists(filePath):
        os.remove(filePath)

    
    print(f"Creating {filePath}")
    rave = raFile.raFile.Create(filePath)
    for recordId in range (1,11):
        data = genData(recordId)
        dataBytes = bytes(data, 'utf-8')
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
    baseRecNbr = len(recordList)    
    for id in range(3):
        newRecNbr = baseRecNbr + id
        data = genData(newRecNbr)
        dataBytes = bytes(data, 'utf-8')
        pad = 0 if random.randint(1,5) != 4 else int(len(data) / 4)
        newId = rave.Add(dataBytes, pad)
        recordList.append(newId)
    rave.Close()
    return recordList

def deleteSpecificRecords(filePath: pathlib.Path, recordList: list, indexes: tuple) -> None:
    rave = raFile.raFile(filePath)
    rave.Open()
    for index in indexes:
        if index != 2:
            deletedId = recordList[index]
            print(f"Deleting record {deletedId} at index {index}")
            rave.Delete(deletedId)
    rave.Close()

def main():
    filePath = ISAM.getFilePath()

    recordList = []
    recordList = createInitialRecords(filePath)
    print(f"list [{recordList}]")

    textPath = ISAM.getTextPath(filePath)    
    ISAM.evaluateRAFile(filePath, textPath)

    baseName = textPath.stem

    index = 3
    deleted3 = recordList[index]
    deleteARecord(filePath, deleted3)
    recordList[index] = 0
    deletedLast = recordList[-1]
    deleteARecord(filePath, deletedLast)
    recordList[-1] = 0
    printResults(filePath, textPath, baseName, "Deleted 3 and last record", "del3Last")

    deleteARecord(filePath, recordList[0])
    recordList[0] = 0
    printResults(filePath, textPath, baseName, "Deleted record 0", "delZero")
    deleteARecord(filePath, recordList[4])
    recordList[4] = 0
    printResults(filePath, textPath, baseName, "Deleted record 4", "del4")

    recordList = addSomeRecords(filePath, recordList)
    printResults(filePath, textPath, baseName, "Added some records", "AddSome")
    
    deleteSpecificRecords(filePath, recordList, (5, 7))
    recordList[5] = 0
    recordList[7] = 0
    printResults(filePath, textPath, baseName, "Deleted records 5, and 7 in that order", "del5_7")

    deleteSpecificRecords(filePath, recordList, (6, 2))
    recordList[6] = 0
    recordList[2] = 0
    printResults(filePath, textPath, baseName, "Deleted record 6, and 2  in that order", "del6")

    for index in range(len(recordList)):
        if recordList[index] != 0:
            print(f"reading and restoring record[{index}] = {recordList[index]}")
            rave = raFile.raFile(filePath)
            rave.Open()
            record = rave.ReadData(recordList[index]).decode("utf-8")
            shorterRecord = record[0:int(len(record) - 2)]
            print(f"Reduce record length from {len(record)} to {len(shorterRecord)} characters")
            newRRef = rave.Save(recordList[index], shorterRecord)
            recordList[index] = newRRef
            print(f"Restored record at ID: {newRRef}")
            rave.Close()
            printResults(filePath, textPath, baseName, "Save shorter record back", "SaveShorter")

            rave.Open()
            record = rave.ReadData(recordList[index]).decode("utf-8")
            longerRecord = record + record
            print(f"Double record length from {len(record)} to {len(longerRecord)} characters")
            newRRef = rave.Save(recordList[index], longerRecord)
            recordList[index] = newRRef
            print(f"Restored longer record at ID: {newRRef}")
            rave.Close()
            printResults(filePath, textPath, baseName, "Save shorter record back", "SaveLonger")
            break




if __name__ == "__main__":
    main()
else:
    print("This module is not intended to be imported")
