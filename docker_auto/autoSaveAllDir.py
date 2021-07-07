import subprocess
import glob
import os
import sys

argv = sys.argv
DIR_NAME = "museum2"


def saveDepth():
    commandList = [
        "cp ../data/autoInDocker.py ../data/%s/auto.py" % DIR_NAME,
        "./quick-start.sh /home/takashi/Desktop/study/M2/colmap/colmap-dev/MVS/data/%s"
        % DIR_NAME,
    ]
    imgPathList = glob.glob("../data/%s/wrk/dense/0/stereo/depth_maps/*.bin" % DIR_NAME)
    commandList = addAllDepthPath(commandList, imgPathList)
    doCommand(commandList=commandList, imgPathList=imgPathList)


def addAllDepthPath(commandList, imgPathList):
    commandList.append("mkdir -p ../data/%s/depth" % DIR_NAME)
    commandList.append("mkdir -p ../data/%s/normal" % DIR_NAME)
    for imgPath in imgPathList:
        IMG_NAME = os.path.basename(imgPath)
        baseName = IMG_NAME.split(".")[0]
        mode = IMG_NAME.split(".")[2]
        command = (
            "python ../data/mySaveDepth.py -d ../data/%s/wrk/dense/0/stereo/depth_maps/%s -n ../data/%s/wrk/dense/0/stereo/normal_maps/%s -dPath ../data/%s/depth/%s_%s.png -nPath ../data/%s/normal/%s_%s.png"
            % (
                DIR_NAME,
                IMG_NAME,
                DIR_NAME,
                IMG_NAME,
                DIR_NAME,
                baseName,
                mode,
                DIR_NAME,
                baseName,
                mode,
            )
        )
        commandList.append(command)
    return commandList


def doCommand(commandList, imgPathList):
    for command in commandList:
        commandElement = command.split(" ")
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)

    if not len(imgPathList):
        imgPathList = glob.glob(
            "../data/%s/wrk/dense/0/stereo/depth_maps/*.bin" % DIR_NAME
        )
        commandList = []
        commandList = addAllDepthPath(commandList, imgPathList)
        for command in commandList:
            commandElement = command.split(" ")
            Flag = subprocess.call(commandElement)
            if Flag:
                print("this status", Flag)
                raise Exception(ValueError)
    return


def main():
    DataList = glob.glob("../data/*/")
    # print(DataList)
    # TEMP_NAME=DataList
    global DIR_NAME
    for DataName in DataList:
        DIR_NAME = DataName.split("/")[2]
        print(DIR_NAME)
        saveDepth()


main()
