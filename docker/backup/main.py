# stereo と monoの深度情報をpoisson blendingで合成を行う
# その後stereo mono Naive Oursそれぞれを用いたFWを行い，中央視点をレンダリング
# 中央視点とレンダリング結果の差分を求めるプログラム
#centerが与えられている場合はFWを求める
import numpy as np
import copy as cp
import cv2
import os

from numpy.lib.function_base import disp

from Warping_method.libs.Warping_Tools import forward_warping, forward_warping_Sugie

DIR = "bridge"
dstDir = "./ppt/" + DIR
srcDir = "Data/" + DIR
# threshold = 0
left = cv2.imread(srcDir + "/left.png")
center = cv2.imread(srcDir + "/center.png")
disp_stereo = cv2.imread(srcDir + "/stereo.png", 0)
disp_mono = cv2.imread(srcDir + "/mono.pfm", -1)
disp_mono_ori = cv2.imread(srcDir + "/mono.pfm", -1)
mask_null = np.where(disp_stereo == 0)
mask_comp = np.where(disp_stereo != 0)
mask_comp_img = np.where(disp_stereo == 0, 0, 1)
width = disp_stereo.shape[1]


def dispSizeChecker():
    global disp_stereo, mask_comp, mask_null

    if disp_mono.shape == disp_stereo.shape:
        print("disp size is ok")
    else:
        print(disp_mono.shape)
        print(disp_stereo.shape)
        print("disp size is wrong")
        print("disp size is fitting by triming are you ok? y/n")
        c = input()
        if c == "y":
            # zeros = np.zeros(disp_mono.shape)
            # disp_stereo = disp_stereo + zeros
            diff0 = disp_mono.shape[0] - disp_stereo.shape[0]
            diff1 = disp_mono.shape[1] - disp_stereo.shape[1]
            if diff0:
                disp_stereo = np.pad(disp_stereo, [(diff0, 0), (0, 0)], "constant")
            if diff1:
                disp_stereo = np.pad(disp_stereo, [(0, diff1), (0, 0)], "constant")
            # print(diff)
            print("disp_mono shape", disp_mono.shape)
            print("disp_stereo shape", disp_stereo.shape)

            # mask_null = np.where(disp_stereo <= threshold)
            # mask_comp = np.where(disp_stereo > threshold)
            mask_null = np.where(disp_stereo == 0)
            mask_comp = np.where(disp_stereo != 0)

        else:
            raise


def ColorWarping(img, disp):
    chDic = {"r": 0, "g": 1, "b": 2}
    keyList = ["r", "g", "b"]
    chImgList1, chImgList2 = [], []
    left_shift_Num = 1
    up_shift_Num = 0
    for key in keyList:
        ch = chDic[key]
        warped_img, blendMask = forward_warping_Sugie(
            img[:, :, ch], disp, 0 - up_shift_Num, 0 - left_shift_Num,
        )
        chImgList1.append(
            np.reshape(warped_img[:, :], [left.shape[0], left.shape[1], 1])
        )
    colorImg1 = np.concatenate([chImgList1[0], chImgList1[1], chImgList1[2]], axis=2)
    for key in keyList:
        ch = chDic[key]
        warped_img, validMask = forward_warping(
            img[:, :, ch], disp, 0 - up_shift_Num, 0 - left_shift_Num,
        )
        chImgList2.append(
            np.reshape(warped_img[:, :], [left.shape[0], left.shape[1], 1])
        )
    colorImg2 = np.concatenate([chImgList2[0], chImgList2[1], chImgList2[2]], axis=2)
    blendMask = np.stack([blendMask, blendMask, blendMask], axis=2)

    colorImg = colorImg2 * (1 - blendMask) + colorImg1 * blendMask

    return colorImg, validMask


def mkDir(dirPath):
    if not os.path.isdir(dirPath):
        os.makedirs(dirPath, exist_ok=True)


def FW(disp, mode):
    disp = np.reshape(disp, (left.shape[0], left.shape[1])) / 4.0 + 0.5
    interpolated, validMask = ColorWarping(img=left, disp=disp)
    cv2.imwrite(dstDir + "/FW/FW_%s.png" % mode, interpolated)
    return interpolated, validMask


def writeGraph(x, y, disp_mono, para):
    from matplotlib import pyplot as plt

    XMax = np.max(x)
    YMax = np.max(y)
    if not os.path.isdir(dstDir):
        os.makedirs(dstDir, exist_ok=True)
    X = np.arange(0, 180)
    Y = X * para[0] + para[1]
    fig = plt.figure()
    print(x[:, 0].shape, y.shape)
    plt.xlim([0, int(XMax + 5)])
    plt.ylim([0, int(YMax + 5)])
    plt.scatter(x[:, 0], y, s=1)
    plt.title("relationship between mono and stereo")
    plt.xlabel("Disparity (stereo) [pix]")
    plt.ylabel("Disparity (mono)")
    # plt.show()
    fig.savefig("%s/graph.png" % dstDir)
    plt.plot(X, Y)
    fig.savefig("%s/graphWithLine.png" % dstDir)

    cv2.imwrite("%s/mono.png" % dstDir, disp_mono)
    cv2.imwrite("%s/mono_ori.png" % dstDir, disp_mono_ori)
    print(np.max(disp_stereo), np.min(disp_stereo))

    cv2.imwrite("%s/mask.png" % dstDir, mask_comp_img * 255)
    cv2.imwrite("%s/stereo.png" % dstDir, disp_stereo)
    f = open("%s/scale_offset.txt" % dstDir, "w")
    f.write("scale: %f\n" % para[0])
    f.write("offset: %f\n" % para[1])
    f.close()


def poisson():
    global disp_mono
    A = np.double(disp_stereo[mask_comp])
    A = np.vstack([A, np.ones(len(A))]).T
    # print(type(b))
    b = disp_mono[mask_comp]
    scale, offset = np.linalg.lstsq(A, b, rcond=None)[0]
    print("Data: ", srcDir)
    print("scale: ", scale)
    print("offset: ", offset)
    writeGraph(A, b, disp_mono, [scale, offset])

    disp_mono = (disp_mono - offset) / scale
    b = (b - offset) / scale
    # writeGraph(A, b, disp_mono, [scale, offset])
    # raise
    lap = 4 * np.double(cp.deepcopy(disp_mono))
    lap = lap - np.roll(disp_mono, (+0, +1), axis=(0, 1))
    lap = lap - np.roll(disp_mono, (+1, +0), axis=(0, 1))
    lap = lap - np.roll(disp_mono, (+0, -1), axis=(0, 1))
    lap = lap - np.roll(disp_mono, (-1, +0), axis=(0, 1))

    disp_blend = np.double(cp.deepcopy(disp_stereo))
    disp_blend[mask_null] = cp.deepcopy(disp_mono[mask_null])

    for i in range(1000):
        tmp = np.zeros(disp_blend.shape)
        tmp = tmp + np.roll(disp_blend, (+0, +1), axis=(0, 1))
        tmp = tmp + np.roll(disp_blend, (+1, +0), axis=(0, 1))
        tmp = tmp + np.roll(disp_blend, (+0, -1), axis=(0, 1))
        tmp = tmp + np.roll(disp_blend, (-1, +0), axis=(0, 1))
        disp_blend[mask_null] = (lap[mask_null] + tmp[mask_null]) / 4.0
    return disp_blend


def saveData(disp_blend):
    FW_poisson, valid_poisson = FW(disp_blend, mode="poisson")
    cv2.imwrite(dstDir + "/disp/blend.png", disp_blend)
    cv2.imwrite(dstDir + "/disp/mono.png", disp_mono)
    cv2.imwrite(dstDir + "/disp/stereo.png", disp_stereo)
    cv2.imwrite(dstDir + "/FW/center.png", center)
    disp_blend = np.double(cp.deepcopy(disp_stereo))
    disp_blend[mask_null] = cp.deepcopy(disp_mono[mask_null])
    FW_init, valid_init = FW(disp_blend, mode="init")
    FW_mono, valid_mono = FW(disp_mono, mode="mono")
    FW_stereo, valid_stereo = FW(disp_stereo, mode="stereo")
    cv2.imwrite(dstDir + "/disp/init.png", disp_blend)

    return (
        FW_poisson,
        FW_init,
        FW_mono,
        FW_stereo,
        valid_poisson,
        valid_init,
        valid_mono,
        valid_stereo,
    )


def absImg(img1, img2, mode, valid):
    valid = np.stack([valid, valid, valid], axis=2)

    diff = np.abs(img1 - img2) * valid
    cv2.imwrite(dstDir + "/abs/%s.png" % mode, diff)
    cv2.imwrite(dstDir + "/abs/%s_5.png" % mode, diff * 5)


def main():
    dispSizeChecker()
    mkDir(dirPath=dstDir + "/FW")
    mkDir(dirPath=dstDir + "/disp")
    mkDir(dirPath=dstDir + "/abs")
    disp_blend = poisson()
    (
        FW_poisson,
        FW_init,
        FW_mono,
        FW_stereo,
        valid_poisson,
        valid_init,
        valid_mono,
        valid_stereo,
    ) = saveData(disp_blend)

    absImg(img1=center, img2=FW_poisson, mode="poisson", valid=valid_poisson)
    absImg(img1=center, img2=FW_init, mode="init", valid=valid_init)
    absImg(img1=center, img2=FW_mono, mode="mono", valid=valid_mono)
    absImg(img1=center, img2=FW_stereo, mode="stereo", valid=valid_stereo)


main()
