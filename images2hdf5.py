
import os
import time

from random import shuffle
import glob

import numpy as np
import h5py

import cv2

def worker(parent_dirPath):
    image_size = 64

    shuffle_data = True  # shuffle the addresses before saving
    hdf5_path = os.path.join(parent_dirPath, "dataset", "dataset"+ str(image_size) +".hdf5")  # address to where you want to save the hdf5 file

    if not os.path.isdir(os.path.join(parent_dirPath, "dataset")):
        os.makedirs(os.path.join(parent_dirPath, "dataset"))

    train_path = 'cleaned_dir/*.jpg'

    # read addresses and labels from the 'train' folder
    addrs = glob.glob(os.path.join(parent_dirPath, train_path))
    labels = [0 if 'image_0' in addr else 1 for addr in addrs]  # 0 = other, 1 = object

    # to shuffle data
    if shuffle_data:
        c = list(zip(addrs, labels))
        shuffle(c)
        addrs, labels = zip(*c)

    # Divide the hata into 60% train, 20% validation, and 20% test
    train_addrs = addrs[0:int(0.6*len(addrs))]
    train_labels = labels[0:int(0.6*len(labels))]

    val_addrs = addrs[int(0.6*len(addrs)):int(0.8*len(addrs))]
    val_labels = labels[int(0.6*len(addrs)):int(0.8*len(addrs))]

    test_addrs = addrs[int(0.8*len(addrs)):]
    test_labels = labels[int(0.8*len(labels)):]


    data_order = 'tf'  # 'th' for Theano, 'tf' for Tensorflow

    # check the order of data and chose proper data shape to save images
    if data_order == 'th':
        train_shape = (len(train_addrs), 3, image_size, image_size)
        val_shape = (len(val_addrs), 3, image_size, image_size)
        test_shape = (len(test_addrs), 3, image_size, image_size)
    elif data_order == 'tf':
        train_shape = (len(train_addrs), image_size, image_size, 3)
        val_shape = (len(val_addrs), image_size, image_size, 3)
        test_shape = (len(test_addrs), image_size, image_size, 3)

    # open a hdf5 file and create earrays
    hdf5_file = h5py.File(hdf5_path, mode='w')

    hdf5_file.create_dataset("train_img", train_shape, np.int8)
    hdf5_file.create_dataset("val_img", val_shape, np.int8)
    hdf5_file.create_dataset("test_img", test_shape, np.int8)

    hdf5_file.create_dataset("train_mean", train_shape[1:], np.float32)

    hdf5_file.create_dataset("train_labels", (len(train_addrs),), np.int8)
    hdf5_file["train_labels"][...] = train_labels
    hdf5_file.create_dataset("val_labels", (len(val_addrs),), np.int8)
    hdf5_file["val_labels"][...] = val_labels
    hdf5_file.create_dataset("test_labels", (len(test_addrs),), np.int8)
    hdf5_file["test_labels"][...] = test_labels


    # a numpy array to save the mean of the images
    mean = np.zeros(train_shape[1:], np.float32)

    # loop over train addresses
    for i in range(len(train_addrs)):
        # print how many images are saved every 1000 images
        if i % 1000 == 0 and i > 1:
            print('Train data: {}/{}'.format(i, len(train_addrs)))

        # read an image and resize to (224, 224)
        # cv2 load images as BGR, convert it to RGB
        addr = train_addrs[i]
        img = cv2.imread(addr)
        img = cv2.resize(img, (image_size, image_size), interpolation=cv2.INTER_LINEAR)
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # add any image pre-processing here

        # if the data order is Theano, axis orders should change
        if data_order == 'th':
            img = np.rollaxis(img, 2)

        # save the image and calculate the mean so far
        hdf5_file["train_img"][i, ...] = img[None]
        mean += img / float(len(train_labels))

    # loop over validation addresses
    for i in range(len(val_addrs)):
        # print how many images are saved every 1000 images
        if i % 1000 == 0 and i > 1:
            print('Validation data: {}/{}'.format(i, len(val_addrs)))

        # read an image and resize to (224, 224)
        # cv2 load images as BGR, convert it to RGB
        addr = val_addrs[i]
        img = cv2.imread(addr)
        img = cv2.resize(img, (image_size, image_size), interpolation=cv2.INTER_LINEAR)
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # add any image pre-processing here

        # if the data order is Theano, axis orders should change
        if data_order == 'th':
            img = np.rollaxis(img, 2)

        # save the image
        hdf5_file["val_img"][i, ...] = img[None]

    # loop over test addresses
    for i in range(len(test_addrs)):
        # print how many images are saved every 1000 images
        if i % 1000 == 0 and i > 1:
            print('Test data: {}/{}'.format(i, len(test_addrs)))

        # read an image and resize to (224, 224)
        # cv2 load images as BGR, convert it to RGB
        addr = test_addrs[i]
        img = cv2.imread(addr)
        img = cv2.resize(img, (image_size, image_size), interpolation=cv2.INTER_LINEAR)
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # add any image pre-processing here

        # if the data order is Theano, axis orders should change
        if data_order == 'th':
            img = np.rollaxis(img, 2)

        # save the image
        hdf5_file["test_img"][i, ...] = img[None]

    # save the mean and close the hdf5 file
    hdf5_file["train_mean"][...] = mean
    hdf5_file.close()

def main():
    startTime = time.time()
    # 過濾篩選可能有效的資料夾
    dirList = list()
    for d in os.listdir():
        if os.path.isdir(os.path.join("", d)):
            if d != "urls" and d != "words" and d != "__pycache__":
                dirList.append(d)

    if not len(dirList):
        print("沒有有效資料夾。")
    else:
        while True:
            # 列出有效資料夾
            for idx, value in enumerate(dirList):
                print("[{}]:{}".format(idx, value))
            # 使用者輸入
            dirIdex = input("請選擇內含cleaned_dir的資料夾(9527=exit)(ex.:0):")
            if not dirIdex.isnumeric():
                print("請輸入自然數！！")
            elif int(dirIdex) == 9527:
                print("掰掰")
                break
            elif int(dirIdex) > len(dirList) - 1:
                print("請輸入有效數字！！")
            else:
                # 工作資料夾
                dirPath = os.path.join(dirList[int(dirIdex)])
                # 確認是否有 url files
                if not (os.path.exists(os.path.join(dirPath, "cleaned_dir"))):
                    print(dirPath)
                    print("此資料夾，找不到cleaned_dir!!")
                    break
                else:
                    # 紀錄開始時間
                    startTime = time.time()
                    worker(parent_dirPath=dirPath)
                    break

        print("Cost time: {} ".format(time.time() - startTime))


if __name__ == "__main__":
    main()
