import glob
import subprocess
import os
import shutil

dstDirPath = "./dataMatome"
dirList = glob.glob("./dataMatome/*")
keyList = []
for dir in dirList:
    # print(dirList)
    key = os.path.basename(dir)
    # glob("./dataMatome")
    keyList.append(key)

# def makeDataset(DIR_NAME, mode):
# print(DIR_NAME)
# os.makedirs("./dataMatome/%s/images" % DIR_NAME, exist_ok=True)
# commandList = [
#     "cp ./%s/%s/* dataMatome/%s/images/ -r -f" % (DIR_NAME, mode, DIR_NAME)
# ]
# doCommand(commandList)
def makeDataset(DIR_NAME, mode):
    if not DIR_NAME in keyList:
        # os.makedirs("./dataMatome/%s/images" % DIR_NAME, exist_ok=True)
        print(DIR_NAME)

        shutil.copytree(
            "./%s/%s/" % (DIR_NAME, mode), "dataMatome/%s/images/" % (DIR_NAME)
        )


def main():
    imgsdirList = glob.glob("./*/imgs/")
    imagesdirList = glob.glob("./*/images/")
    for imgsDir in imgsdirList:
        # print(imgsDir)
        DIR_NAME = imgsDir.split("/")[1]
        makeDataset(DIR_NAME, mode="imgs")
    for imagesDir in imagesdirList:
        # print(imagesDir)
        DIR_NAME = imagesDir.split("/")[1]
        makeDataset(DIR_NAME, mode="images")


def doCommand(commandList):
    print(commandList)
    for command in commandList:
        commandElement = command.split(" ")
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)


main()
