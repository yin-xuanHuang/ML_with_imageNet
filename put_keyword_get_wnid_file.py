import os
import re

def find_wnid(keyword, words_list, returnList):
    # 設定 regex
    re_filter = re.compile(r'(?:\t|, |,)(?:{})(?:\t| ,|,|\n)'.format("|".join(keyword)))
    # 查找 words 集
    for line in words_list:
        if line == "\n":
            continue
        elif line == "":
            continue
        else:
            result = re_filter.search(line)
            if result is None:
                continue
            else:
                returnList.append(line)

def main():
    # key words 檔案位置，開檔用
    words_file_path = os.path.join("words", "words.txt")
    while True:
        keyWord = input("請輸入關鍵字(ex:woman man):")
        multiple_keyword = keyWord.replace(" ", "")
        # 限定為純英文單字
        if not multiple_keyword.isalpha():
            print(chr(27) + "[2J") # 清理螢幕
            print("請輸入只含英文的字詞！")
        else:
            if len(multiple_keyword) == keyWord:
                # 英文小寫化
                keyWord = keyWord.lower()
            else:
                keyWord = keyWord.split(" ")
                for idx, value in enumerate(keyWord):
                    keyWord[idx] = value.lower()

            # 檢查檔案是否存在
            if not os.path.isfile(words_file_path):
                print(chr(27) + "[2J") # 清理螢幕
                print("找不到 words/words.txt 檔案。")
                break
            else:
                # 將檔案以列為單位，形成list()存到words_list
                words_list = list()
                with open(words_file_path, "r") as f:
                    words_list = f.readlines()
                f.close()

                # 對應的所有wnid列表
                words_match_wnid_list = list()
                find_wnid(keyWord, words_list, words_match_wnid_list)

                print("共有: {} 個標籤".format(len(words_match_wnid_list)))

                if words_match_wnid_list == []:
                    print(chr(27) + "[2J") # 清理螢幕
                    print("找不到含有 {} 關鍵字的標籤。".format(keyWord))
                    continue
                else:
                    if type(keyWord) is not str:
                        keyWord = "_".join(keyWord)
                    # 建立儲存結果資料夾
                    dirName = keyWord
                    count = 0
                    while True:
                        count += 1
                        if not os.path.isdir(dirName):
                            os.makedirs(dirName)
                            break
                        else:
                            dirName = keyWord
                            dirName = dirName + "_{}".format(count)

                    with open(os.path.join(dirName, keyWord + "_wnids"), "w+") as f:
                        for idx, line in enumerate(words_match_wnid_list):
                            line = line.strip()
                            list_wnid_sentence = line.split("\t")
                            print("[{}]={} {}".format(idx, list_wnid_sentence[0], list_wnid_sentence[1]), end=" ")
                            f.write(list_wnid_sentence[0] + "\n")
                            print("")
                    f.close()
                    print("Get {}/{}_wnids file!".format(dirName, keyWord))
                    break


if __name__ == "__main__":
    main()
