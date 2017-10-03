'''
此程式的工作為：
  1. 將使用者輸入的單字，在words/words.txt 查找，
     然後建立專案資料夾，裡面包含在words.txt 查找的wnid 結果
  2. 使用者可以輸入多單詞，只要用空白間隔開，
'''
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
        testHyphen = multiple_keyword.replace("-", "")
        # 限定為純英文單字
        if not testHyphen.isalpha():
            print(chr(27) + "[2J") # 清理螢幕
            print("請輸入英文的字詞")
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
                print("找不到 words/words.txt 檔案，請閱讀words/readme 文件，自行下載檔案。")
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
                            print("[{}]={} {}".format(idx, list_wnid_sentence[0], list_wnid_sentence[1]))
                            f.write(list_wnid_sentence[0] + "\n")
                            print("http://www.image-net.org/synset?wnid=" + list_wnid_sentence[0])
                    f.close()
                    print("Get {}/{}_wnids file!".format(dirName, keyWord))
                    print("小建議：除非對英文很有自信，不然跟本苦主一樣，查一下比較好，有些wnid也可能已經失效。")
                    print("（苦主經驗：因為truck 學會hand truck 這個單字。）")
                    print("以上確認完畢後，接下來則執行wnid2url.py 來獲得下載urls列表。")
                    break


if __name__ == "__main__":
    main()
