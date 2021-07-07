# ./dataName/直下にデータを揃える
# left.png, dispMVS.png, dispMono.png, dispMono.pfm
import os
import sys
import cv2
import numpy as np
import subprocess
import glob

DIR_NAME = "aquarium"
setDataPath = "../data/aquarium/4poisson"
imgName = "0001"
depthPath = "%s_geometric.png" % imgName


def doCommand(commandList=[]):
    for command in commandList:
        print(command)
        commandElement = command.split(" ")
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)
    return


def makeDataDir():
    os.makedirs(setDataPath, exist_ok=True)


def setDispMVS():
    depthPath = "../data/aquarium/depth/"
    depthPath = os.path.join(depthPath, imgName)
    depthMVS = cv2.imread(depthPath, 0)
    disp = np.zeros(depthMVS.shape)
    print(disp.shape)
    for x in range(depthMVS.shape[1]):
        for y in range(depthMVS.shape[0]):
            if depthMVS[y][x] == 0:
                continue
            else:
                disp[y][x] = 1.0 / depthMVS[y][x]
    Max = np.max(disp)
    Min = np.min(disp)
    disp = (disp - Min) / (Max - Min)
    saveDispMVSPath = os.path.join(setDataPath, "dispMVS.png")
    cv2.imwrite(saveDispMVSPath, disp * 255)


def setDispMono():
    commandList = [
        "conda activate midas",
        "python /home/takashi/Desktop/study/M2/poisson/MiDaS-master/myRun.py --input_path /home/takashi/Desktop/study/M2/colmap/colmap-dev/MVS/data/aquarium/images --output_path /home/takashi/Desktop/study/M2/colmap/colmap-dev/MVS/data/aquarium/dispMono"
        "cp ../data/aquarium/dispMono/%s.pfm %s/%s.pfm"
        % (imgName, setDataPath, imgName),
        "cp ../data/aquarium/dispMono/%s.png %s/%s.png"
        % (imgName, setDataPath, imgName),
        "conda activate COLMAP"
        # "cp ../data/aquarium/dispMono/%s.png" % imgName,
    ]
    doCommand(commandList=commandList)


def setColorImg():
    # commandList = [
    # "cp ../data/aquarium/images/%s.jpg %s/%s.jpg"
    # # "cp ../data/aquarium/images/%s.jpg %s/%s.jpg"
    # ]
    # doCommand(commandList=commandList)
    imgPath = glob.glob("../data/aquarium/images/%s.*" % imgName)
    colorImg = cv2.imread(imgPath[0])
    print(imgPath)
    cv2.imwrite("%s/%s.png" % (setDataPath, imgName), colorImg)


def main():
    makeDataDir()
    setColorImg()
    setDispMono()
    setDispMVS()


main()
