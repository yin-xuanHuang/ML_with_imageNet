
import os
import time

def worker(dirPath, dirName):

    for i in range(2):
        url_file = os.path.join(dirPath, dirName + "_urls_" + str(i))
        print("Read image list in memory,")
        images_list = os.listdir(os.path.join(dirPath, "image_" + str(i)))
        with open(url_file, mode="r", errors='ignore', encoding='utf-8') as f:
            lines = f.readlines()
            lines.reverse()
            print("Read url file in memmory.")
            altered_lines = list()
            count = 0
            while True:
                line = lines.pop().strip()
                if line == "\n":
                    continue
                fileName = line.split("\t")[0]
                if fileName in  images_list:
                    count = 0
                else:
                    altered_lines.append(line)
                    count += 1

                if count >= 10000 or len(lines) == 0:
                    altered_lines += lines
                    break
                elif count >= 100 and count < 3000:
                    print(count)
        print("Write file.")
        with open(url_file, "w") as f:
            f.write('\n'.join(altered_lines) + '\n')
        f.close()

def main():
    startTime = time.time()
    # 過濾篩選可能有效的資料夾
    dirList = list()
    for d in os.listdir():
        if os.path.isdir(os.path.join("", d)):
            if d != "urls" and d != "words":
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
                # 確認是否有 url files
                if not (os.path.isfile(os.path.join(dirPath, dirList[int(dirIdex)] + "_urls_0")) and os.path.isfile(os.path.join(dirPath, dirList[int(dirIdex)] + "_urls_1"))):
                    print("此 {} 資料夾內，沒有或缺少 url files！！".format(dirList[int(dirIdex)]))
                    break
                else:
                    # 紀錄開始時間
                    startTime = time.time()
                    #print("get images list {}".format(images_list))
                    worker(dirPath=dirPath, dirName=dirList[int(dirIdex)])
                    break

        print("Cost time: {} ".format(time.time() - startTime))


if __name__ == "__main__":
    main()
