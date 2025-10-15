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

def createInitialRcords(filePath: pathlib.Path) -> list:
    recordList = []
    if os.path.exists(filePath):
        os.remove(filePath)

    
    print(f"Creating {filePath}")
    rave = raFile.raFile.Create(filePath)
    for recordId in range (1,11):
        datalen = random.randint(20, 100)
        data = '{' + f'"ID": {recordId:03d}, "data": "{''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ", k=datalen))}"' + '}'
        dataBytes = bytearray(data, 'utf-8')
        pad = 0 if random.randint(1,5) != 4 else int(datalen / 4)
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

def main():
    filePath = ISAM.getFilePath()

    recordList = []
    recordList = createInitialRcords(filePath)
    print(f"list [{recordList}]")

    textPath = ISAM.getTextPath(filePath)    
    ISAM.evaluateRAFile(filePath, textPath)

    index = random.randint(0, len(recordList))
    deletedFirst = recordList[index]
    deleteARecord(filePath, deletedFirst)
    baseName = textPath.stem
    newTextPath = textPath.with_name(f"{baseName}_del{textPath.suffix}")
    ISAM.evaluateRAFile(filePath, newTextPath)

if __name__ == "__main__":
    main()
else:
    print("This module is not intended to be imported")
