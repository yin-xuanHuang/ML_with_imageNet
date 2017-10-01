'''
上工之第二個腳本！

此程式的工作為：
  1. 將使用者上一步建立的wnid 結果為索引，
     查找url/裡的url 檔案（請閱讀url/readme），
     將對應的urls 寫入新創的_urls_1檔案，
     另外隨機抓取非選擇的wnid 寫入新創的_urls_0檔案。
  2. 注意，因為url 檔都1G左右，本程式目前版本是邊讀邊寫，
     依據使用的的設備不同，下面的max_lines 可自行調整。

'''

import os
from random import shuffle
from psutil import virtual_memory
import time


def main():
    # 未避免記憶體塞暴，每隔 1024*256 寫入一次，並強制清空一次 lists
    max_lines = 1024*256
    # 紀錄開始時間
    startTime = time.time()
    shuffle_data = True  # 打亂順序
    # 查看urls資料夾里有沒有可能的url_file
    urls_dirPath = os.path.join("urls")
    urls_dirList = list()
    for d in os.listdir(urls_dirPath):
        if os.path.isfile(os.path.join(urls_dirPath, d)):
            if d != "readme":
                urls_dirList.append(d)
    # 假如有新檔案，就假設為url file
    if not len(urls_dirList):
        print("urls 資料夾內沒有url_file，請閱讀urls/readme，自行下載檔案。")
    else:
        # 列出可能有效的url file
        print("url file(s): {}".format("|".join(urls_dirList)), end=" ")
        print()
        # 過濾篩選可能有效的資料夾
        dirList = list()
        for d in os.listdir():
            if os.path.isdir(os.path.join("", d)):
                if d != "urls" and d != "words" and d!= "__pycache__":
                    dirList.append(d)

        if not len(dirList):
            print("沒有有效資料夾。")
        else:
            while True:
                # 列出有效資料夾
                for idx, value in enumerate(dirList):
                    print("[{}]:{}".format(idx, value))
                # 使用者輸入
                dirIdex = input("請選擇內含wnid_file的資料夾(9527=exit)(ex.:0):")
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
                    # 確認是否有 wnidFile
                    if not os.path.isfile(os.path.join(dirPath,
                                                       dirList[int(dirIdex)] + "_wnids")):
                        print("此 {} 資料夾內，沒有wnidFile！！".format(dirList[int(dirIdex)]))
                        break
                    else:
                        # 將檔案內的 wnid 以列為單位，讀到 list 內
                        wnidList = list()
                        with open(os.path.join(dirPath,dirList[int(dirIdex)] + "_wnids"), "r") as f:
                            wnidList = f.readlines()
                        f.close()

                        # 所有 wnid 所對應的 urls
                        wnidList2urlsList = list()
                        # 計數對應到的 line
                        count = 0
                        count0 = 0
                        count1 = 0
                        not_match_list = list()
                        # 將 url_file 有對應到 wnid 的 line 都存在 wnidList2urlsList
                        for url_file in urls_dirList:
                            with open(os.path.join(urls_dirPath, url_file), mode="r", errors="ignore") as f:
                                lineList = f.readlines()
                            f.close()

                            for line in lineList:
                                list_wnidid_url = line.split("\t")
                                wnid = list_wnidid_url[0].split("_")[0]
                                if wnid + "\n" in wnidList:
                                    wnidList2urlsList.append(line)
                                    count += 1
                                    count1 += 1
                                else:
                                    not_match_list.append(line)
                                    count0 += 1
                                if (count1 + count0) / max_lines >= 1:
                                    mem = virtual_memory()
                                    print("free memory: {} ".format(mem.free))
                                    if count1 == 0:
                                        # y=0 順序隨機調換
                                        if shuffle_data:
                                            shuffle(not_match_list)
                                        # 寫入檔案 y=0
                                        with open(os.path.join(dirPath, dirList[int(dirIdex)] + "_urls_0"), "a+") as f0:
                                            for line in not_match_list[:100]:
                                                f0.write(line)
                                        f0.close()
                                        not_match_list = list()
                                    else:
                                        # 寫入檔案 y=1
                                        with open(os.path.join(dirPath, dirList[int(dirIdex)] + "_urls_1"), "a+") as f1:
                                            for line in wnidList2urlsList:
                                                f1.write(line)
                                        f1.close()
                                        wnidList2urlsList = list()
                                        # y=0 順序隨機調換
                                        if shuffle_data:
                                            shuffle(not_match_list)
                                        # 寫入檔案 y=0
                                        with open(os.path.join(dirPath, dirList[int(dirIdex)] + "_urls_0"), "a+") as f0:
                                            if count0 < count1 * 3 + 1:
                                                for line in not_match_list:
                                                    f0.write(line)
                                            else:
                                                for line in not_match_list[:count1 * 3 + 1]:
                                                    f0.write(line)
                                        f0.close()
                                        not_match_list = list()
                                    count0 = 0
                                    count1 = 0

                        print("Y=1, count= {} ".format(count))
                        print("work get done!")
                        print("Cost time= {} ".format(time.time() - startTime))
                        print("接下來則執行multithreads_download_from_url_files.py 來下載圖檔。")
                        break


if __name__ == "__main__":
    main()
