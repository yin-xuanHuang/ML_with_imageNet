'''
機器學習


'''

import os
import time

import h5py

import numpy as np
import matplotlib.pyplot as plt
import scipy
from PIL import Image
from scipy import ndimage

from dnn_app_utils_v2 import *

def two_layer_model(X, Y, layers_dims, learning_rate = 0.0075, num_iterations = 3000, print_cost=False, , paramsPath=None):
    grads = {}
    costs = []                         # keep track of cost
    learning_rates = []                # keep track of learning_rate
    m = X.shape[1]
    (n_x, n_h, n_y) = layers_dims

    # Parameters initialization.
    parameters = initialize_parameters(n_x, n_h, n_y)
    # 載入之前訓練的，前提是hidden layer 數量都要相同
    if paramsPath != None:
        parameters_filePath = os.path.join(paramsPath)
        if os.path.isfile(parameters_filePath):
            npload = np.load(parameters_filePath)
            parameters = npload.item()
            del npload

    W1 = parameters["W1"]
    b1 = parameters["b1"]
    W2 = parameters["W2"]
    b2 = parameters["b2"]

    per100iteration_time=time.time()
    # Loop (gradient descent)
    for i in range(0, num_iterations):

        A1, cache1 = linear_activation_forward(X, W1, b1, 'relu')
        A2, cache2 = linear_activation_forward(A1, W2, b2, 'sigmoid')

        cost = compute_cost(A2, Y)

        dA2 = - (np.divide(Y, A2) - np.divide(1 - Y, 1 - A2))

        dA1, dW2, db2 = linear_activation_backward(dA2, cache2, 'sigmoid')
        dA0, dW1, db1 = linear_activation_backward(dA1, cache1, 'relu')

        grads['dW1'] = dW1
        grads['db1'] = db1
        grads['dW2'] = dW2
        grads['db2'] = db2

        parameters = update_parameters(parameters, grads, learning_rate)

        W1 = parameters["W1"]
        b1 = parameters["b1"]
        W2 = parameters["W2"]
        b2 = parameters["b2"]

        if print_cost and i % 100 == 99:
            print("Cost after iteration {}: {}".format(i+1, np.squeeze(cost)))
            print("Periteration * 100 cost time: {}".format(time.time() - per100iteration_time))
            per100iteration_time=time.time()
        if print_cost and i % 100 == 99:
            learning_rates.append(learning_rate)
            costs.append(cost)
            # 每100個iteration 檢查一次是否在震盪，有就減少learning_rate 10倍
            if len(costs) >= 2:
                nowCost = costs[-1]
                preCost = costs[-2]
                if nowCost >= preCost:
                    learning_rate *= 0.1
                    print("Smaller the learning_rate to {}".format(learning_rate))

        print("Periteration cost time: {}".format(time.time() - periteration_time))

    return parameters, costs, learning_rates

def training(hdf5Path, SaveDirPath, project_name):
    image_size = 64
    # Loading the dataset
    X_train_orig, Y_train_orig, X_test_orig, Y_test_orig = load_dataset(hdf5Path=hdf5Path)

    X_train_flatten = X_train_orig.reshape(X_train_orig.shape[0], -1).T
    #X_val_flatten = X_val_orig.reshape(X_val_orig.shape[0], -1).T
    X_test_flatten = X_test_orig.reshape(X_test_orig.shape[0], -1).T

    X_train = X_train_flatten/255.
    #X_val = X_val_flatten/255.
    X_test = X_test_flatten/255.

    Y_train = Y_train_orig
    #Y_val = Y_val_orig
    Y_test = Y_test_orig

    print ("number of training examples = " + str(X_train.shape[1]))
    print ("number of test examples = " + str(X_test.shape[1]))
    print ("X_train shape: " + str(X_train.shape))
    print ("Y_train shape: " + str(Y_train.shape))
    print ("X_test shape: " + str(X_test.shape))
    print ("Y_test shape: " + str(Y_test.shape))

    # 設定hidden layer 的節點數，預設：7
    layers_dims = (X_train.shape[0], 7, 1)

    parameters, costs, learning_rates = two_layer_model(X_train, Y_train, layers_dims = layers_dims, num_iterations = 2500, print_cost=True)

    # save parameters
    np.save(os.path.join(SaveDirPath, project_name + ".npy"), parameters)

    # save costs
    strcosts = [ str(scost) for scost in costs ]
    costs2print = "\n".join(strcosts)
    with open(os.path.join(SaveDirPath, project_name + "_costsList"), "w+") as f:
        f.write(costs2print)
    f.close()

    # save learning_rates
    strlearning_rates = [ str(sl) for sl in learning_rates ]
    learning_rates2print = "\n".join(strlearning_rates)
    with open(os.path.join(SaveDirPath, project_name + "_learningRatesList"), "w+") as f:
        f.write(learning_rates2print)
    f.close()

    # plot the cost
    plt.plot(np.squeeze(costs))
    plt.ylabel('cost')
    plt.xlabel('iterations')
    plt.savefig(fname=os.path.join(SaveDirPath, project_name + ".png"))
    plt.show()

    predictions_train = predict(X_train, Y_train, parameters)
    print("Predictions of train: {}".format(predictions_train))

    predictions_test = predict(X_test, Y_test, parameters)
    print("Predictions of test: {}".format(predictions_test))

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
                dirPath = os.path.join(dirList[int(dirIdex)])
                # 確認是否有 url files
                if not (os.path.exists(os.path.join(dirPath, "dataset"))):
                    print(dirPath)
                    print("此資料夾，找不到dataset!!")
                    break
                else:
                    hdf5List = list()
                    for d in os.listdir(os.path.join(dirPath, "dataset")):
                        if os.path.isfile(os.path.join(dirPath, "dataset", d)):
                            if ".hdf5" in d:
                                hdf5List.append(d)

                    if not len(hdf5List):
                        print("沒有有效資料夾。")
                    else:
                        while True:
                            # 列出有效資料夾
                            for idx, value in enumerate(hdf5List):
                                print("[{}]:{}".format(idx, value))
                            # 使用者輸入
                            hdf5Idex = input("請選擇要訓練的hdf5檔案(9527=exit)(ex.:0):")
                            if not hdf5Idex.isnumeric():
                                print("請輸入自然數！！")
                            elif int(hdf5Idex) == 9527:
                                print("掰掰")
                                break
                            elif int(hdf5Idex) > len(hdf5List) - 1:
                                print("請輸入有效數字！！")
                            else:
                                # TODO:專案名稱
                                project_name = "project_dnn"
                                SaveDirPath = os.path.join(dirList[int(dirIdex)],
                                                               "dataset")
                                # 工作檔案
                                hdf5Path = os.path.join(dirList[int(dirIdex)], "dataset", hdf5List[int(hdf5Idex)])
                                # 紀錄開始時間
                                startTime = time.time()
                                training(hdf5Path=hdf5Path, SaveDirPath=SaveDirPath, project_name=project_name)
                                break
                        break

        print("Cost time: {} ".format(time.time() - startTime))


if __name__ == "__main__":
    main()
