import os
import time

import h5py

import numpy as np
import matplotlib.pyplot as plt
import scipy
from PIL import Image
from scipy import ndimage

from dnn_app_utils_v2 import *

def two_layer_model(X, Y, layers_dims, learning_rate = 0.0075, num_iterations = 3000, print_cost=False):
    """
    Implements a two-layer neural network: LINEAR->RELU->LINEAR->SIGMOID.

    Arguments:
    X -- input data, of shape (n_x, number of examples)
    Y -- true "label" vector (containing 0 if cat, 1 if non-cat), of shape (1, number of examples)
    layers_dims -- dimensions of the layers (n_x, n_h, n_y)
    num_iterations -- number of iterations of the optimization loop
    learning_rate -- learning rate of the gradient descent update rule
    print_cost -- If set to True, this will print the cost every 100 iterations

    Returns:
    parameters -- a dictionary containing W1, W2, b1, and b2
    """

    grads = {}
    costs = []                              # to keep track of the cost
    m = X.shape[1]                           # number of examples
    (n_x, n_h, n_y) = layers_dims

    # Initialize parameters dictionary, by calling one of the functions you'd previously implemented
    ### START CODE HERE ### (≈ 1 line of code)
    parameters = initialize_parameters(n_x, n_h, n_y)
    ### END CODE HERE ###

    # Get W1, b1, W2 and b2 from the dictionary parameters.
    W1 = parameters["W1"]
    b1 = parameters["b1"]
    W2 = parameters["W2"]
    b2 = parameters["b2"]

    # Loop (gradient descent)
    per100iteration_time=time.time()
    for i in range(0, num_iterations):
        #periteration_time=time.time()

        # Forward propagation: LINEAR -> RELU -> LINEAR -> SIGMOID. Inputs: "X, W1, b1". Output: "A1, cache1, A2, cache2".
        ### START CODE HERE ### (≈ 2 lines of code)
        A1, cache1 = linear_activation_forward(X, W1, b1, 'relu')
        A2, cache2 = linear_activation_forward(A1, W2, b2, 'sigmoid')
        ### END CODE HERE ###

        # Compute cost
        ### START CODE HERE ### (≈ 1 line of code)
        cost = compute_cost(A2, Y)
        ### END CODE HERE ###

        # Initializing backward propagation
        dA2 = - (np.divide(Y, A2) - np.divide(1 - Y, 1 - A2))

        # Backward propagation. Inputs: "dA2, cache2, cache1". Outputs: "dA1, dW2, db2; also dA0 (not used), dW1, db1".
        ### START CODE HERE ### (≈ 2 lines of code)
        dA1, dW2, db2 = linear_activation_backward(dA2, cache2, 'sigmoid')
        dA0, dW1, db1 = linear_activation_backward(dA1, cache1, 'relu')
        ### END CODE HERE ###

        # Set grads['dWl'] to dW1, grads['db1'] to db1, grads['dW2'] to dW2, grads['db2'] to db2
        grads['dW1'] = dW1
        grads['db1'] = db1
        grads['dW2'] = dW2
        grads['db2'] = db2

        # Update parameters.
        ### START CODE HERE ### (approx. 1 line of code)
        parameters = update_parameters(parameters, grads, learning_rate)
        ### END CODE HERE ###

        # Retrieve W1, b1, W2, b2 from parameters
        W1 = parameters["W1"]
        b1 = parameters["b1"]
        W2 = parameters["W2"]
        b2 = parameters["b2"]

        # Print the cost every 100 training example
        if print_cost and i % 100 == 99:
            print("Cost after iteration {}: {}".format(i + 1, np.squeeze(cost)))
            print("Periteration * 100 cost time: {}".format(time.time() - per100iteration_time))
            per100iteration_time=time.time()
        if print_cost and i % 99 == 0:
            costs.append(cost)

        #print("Periteration cost time: {}".format(time.time() - periteration_time))

    return parameters, costs

def training(hdf5Path, npySaveFilePath):
    image_size = 64
    # Loading the dataset
    X_train_orig, Y_train_orig, X_test_orig, Y_test_orig = load_dataset(hdf5Path=hdf5Path)

    # Flatten the training, val and test images
    X_train_flatten = X_train_orig.reshape(X_train_orig.shape[0], -1).T
    #X_val_flatten = X_val_orig.reshape(X_val_orig.shape[0], -1).T
    X_test_flatten = X_test_orig.reshape(X_test_orig.shape[0], -1).T
    # Normalize image vectors
    X_train = X_train_flatten/255.
    #X_val = X_val_flatten/255.
    X_test = X_test_flatten/255.
    # Convert training, val and test labels to one hot matrices
    Y_train = Y_train_orig
    #Y_val = Y_val_orig
    Y_test = Y_test_orig

    print ("number of training examples = " + str(X_train.shape[1]))
    print ("number of test examples = " + str(X_test.shape[1]))
    print ("X_train shape: " + str(X_train.shape))
    print ("Y_train shape: " + str(Y_train.shape))
    print ("X_test shape: " + str(X_test.shape))
    print ("Y_test shape: " + str(Y_test.shape))

    hidden_layer_number = 7

    layers_dims = (X_train.shape[0], hidden_layer_number, 1)

    project_name = "_2_Layers_" + str(hidden_layer_number)

    parameters, costs = two_layer_model(X_train, Y_train, layers_dims = layers_dims, num_iterations = 2500, print_cost=True)

    np.save(npySaveFilePath, parameters)

    strcosts = [ str(scost) for scost in costs ]
    costs2print = "\n\n" + "\n".join(strcosts)
    with open(os.path.normpath(os.path.join(npySaveFilePath, "..", project_name + "_costsList")), "w+") as f:
        f.write(costs2print)
    f.close()

    # plot the cost

    plt.plot(np.squeeze(costs))
    plt.ylabel('cost')
    plt.xlabel('iterations (per tens)')
    plt.title("Learning rate =" + str(learning_rate))
    plt.savefig(os.path.normpath(os.path.join(npySaveFilePath, "..", project_name + ".png")))

    plt.show()

    print("Predictions of train: {}".format(predictions_train))

    predictions_train = predict(X_train, Y_train, parameters)

    print("Predictions of test: {}".format(predictions_test))

    predictions_test = predict(X_test, Y_test, parameters)

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
                                npySaveFilePath = os.path.join(dirList[int(dirIdex)], "dataset", hdf5List[int(hdf5Idex)][:-5] + "_2_Layers.npy")
                                # 工作檔案
                                hdf5Path = os.path.join(dirList[int(dirIdex)], "dataset", hdf5List[int(hdf5Idex)])
                                # 紀錄開始時間
                                startTime = time.time()
                                training(hdf5Path=hdf5Path, npySaveFilePath=npySaveFilePath)
                                break
                        break

        print("Cost time: {} ".format(time.time() - startTime))


if __name__ == "__main__":
    main()
