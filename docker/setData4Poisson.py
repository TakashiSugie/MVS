# ./dataName/直下にデータを揃える
# left.png, dispMVS.png, dispMono.png, dispMono.pfm
import os
import sys
import cv2
import numpy as np
import subprocess
import glob
import myMiDaS.myRun as myRun

DIR_NAME = "aquarium"
imgName = "0001"
depthPath = "%s_geometric.png" % imgName
setDataPath = "../data/%s/4poisson" % (DIR_NAME)


def doCommand(commandList=[]):
    for command in commandList:
        commandElement = command.split(" ")
        Flag = subprocess.call(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)
    return


def doCommandRun(commandList=[]):
    for command in commandList:
        print(command)
        commandElement = command.split(" ")
        print(commandElement)
        Flag = subprocess.run("python test.py".split(" "))
        Flag = subprocess.run(commandElement)
        if Flag:
            print("this status", Flag)
            raise Exception(ValueError)
    return


def makeDataDir():
    os.makedirs(setDataPath, exist_ok=True)


def setDispMVS():
    depthPath = "../data/%s/depth/" % (DIR_NAME)
    depthPath = os.path.join(depthPath, imgName + "_geometric.png")
    # print(depthPath)
    depthMVS = cv2.imread(depthPath, 0)
    disp = np.zeros(depthMVS.shape)
    # print(disp.shape)
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
        # "python /home/takashi/Desktop/study/M2/poisson/MiDaS-master/myRun.py",
        "cp ../data/%s/dispMono/%s.pfm %s/dispMono.pfm"
        % (DIR_NAME, imgName, setDataPath),
        "cp ../data/%s/dispMono/%s.png %s/dispMono.png"
        % (DIR_NAME, imgName, setDataPath),
    ]
    doCommand(commandList=commandList)


def setColorImg():
    imgPath = glob.glob("../data/%s/images/%s.*" % (DIR_NAME, imgName))
    colorImg = cv2.imread(imgPath[0])
    print("%s/left.png" % (setDataPath))
    cv2.imwrite("%s/left.png" % (setDataPath), colorImg)


def main():
    global imgName, setDataPath, depthPath
    imgPathList = glob.glob("../data/%s/depth/*_geometric.png" % (DIR_NAME))
    for imgPath in imgPathList:
        tempName = os.path.basename(imgPath).strip("_geometric.png")
        imgName = tempName
        depthPath = "%s_geometric.png" % imgName
        setDataPath = "../data/%s/4poisson/%s" % (DIR_NAME, imgName)
        makeDataDir()
        setColorImg()
        setDispMono()
        setDispMVS()


main()
