'''
此程式的工作：
1. 多執行緒抓圖片url

*  如果下載中意外停止，可以先使用update_url.py
   來快速清理已經下載的連結，讓下載時間縮短。
工作方式：
one thread put(file.readline)
other thread get() , parse, requests and download images
'''

import os
import queue
import threading
import time
import requests
# 設定總執行緒數
num_threads = 31
# 等待put thread 先處理一陣子，在加入 get threads，秒
put_prepare_time = 3

def get_picture(image_dir, line_queue,  put_done):
    '''
    from start_time to Already exist cost 0.0001 s
    '''
    file_list =  os.listdir(image_dir)
    while not line_queue.empty() or not put_done["put_done"]:
        #start_time = time.time()
        if line_queue.empty():
            time.sleep(5)
            print("wait")
        else:
            if not line_queue.empty():
                line = line_queue.get()
                try:
                    # parse line
                    list_wnidid_url = line.split("\t")
                    wnid_id = list_wnidid_url[0]
                    fileName = wnid_id

                    if fileName in  file_list:
                        print("Already exist.")
                        #print(str(time.time() - start_time))
                        time.sleep(0.1)
                        continue

                    response = requests.get(list_wnidid_url[1], timeout=10, stream=True, allow_redirects=True)
                except requests.exceptions.ConnectionError as e:
                    # DNS failure, refused connection, etc
                    print("ConnectionError")
                except requests.exceptions.Timeout as e:
                    # Timeout exception
                    print('TimeOut')
                except requests.exceptions.TooManyRedirects as e:
                    # exceeds the configured number of maximum redirections
                    print('TooManyRedirects')
                except requests.exceptions.RequestException as e:
                    print("RequestException")
                except Exception as e:
                    print("%s"%e)
                    # record message
                    with open(os.path.join(image_dir, "..","download_error_messages"), 'a+') as fh:
                        fh.write(str(e)+"\n")
                    fh.close()
                else:
                    # 200
                    try:
                        # Open the output file and make sure we write in binary mode
                        with open(os.path.join(image_dir, fileName), 'wb') as fh:
                            for chunk in response.iter_content(1024 * 1024):
                                # Write the chunk to the file
                                fh.write(chunk)
                                # Optionally we can check here if the download is taking too long
                        print(fileName + ":download!")
                    except Exception as e:
                        print("%s"%e)
                        # record message
                        fh.close()
                        with open(os.path.join(image_dir, "..","download_error_messages"), 'a+') as fh:
                            fh.write(str(e)+"\n")
                    else:
                        fh.close()

def put_urls(url_file, line_queue,  put_done):
    with open(url_file, encoding='utf-8', errors='replace', mode='r') as f:
        while True:
            '''
            當queue里的資料數大於100條，
            則1秒增加1條。
            from start_time to calculate cost time 0.00001
            '''
            #start_time = time.time()
            url = f.readline()
            if url == "":
                break
            elif url == "\n":
                continue
            if line_queue.qsize() > 200:
                time.sleep(0.5)
                line_queue.put(url.strip())
            else:
                line_queue.put(url.strip())
            #print(str(time.time() - start_time))
    print("put thread done!")
    f.close()
    put_done["put_done"] = True

def foreman(url_file_name, working_dirPath):
    # 分配工作的工頭

    global num_threads, put_prepare_time

    line_queue = queue.Queue()
    put_done = {"put_done":False}
    thread_pool = []

    download_dirPath = os.path.join(working_dirPath, "image_" + url_file_name[-1])
    if not os.path.exists(download_dirPath):
        os.makedirs(download_dirPath)


    if num_threads > 1:
        t_put = threading.Thread(target=put_urls,
                                 name="tread-put",
                                 kwargs={'url_file':os.path.join(working_dirPath, url_file_name),
                                         'line_queue':line_queue,
                                         'put_done':put_done})
        t_put.daemon = True
        t_put.start()
        thread_pool.append(t_put)

    print("thread_put prepare: {} seconds.".format(put_prepare_time))
    time.sleep(put_prepare_time)

    for t in range(num_threads-1):
        thread = threading.Thread(target=get_picture,
                                  name="thread-get-" + str(t),
                                  kwargs={'image_dir':download_dirPath,
                                          'line_queue':line_queue,
                                          'put_done':put_done})
        thread.daemon = True
        thread.start()
        thread_pool.append(t)

    thread_pool[0].join()

    while True:
        time.sleep(1)
        if line_queue.empty():
            time.sleep(1)
            print("Job get down!")
            break
    # rewrite the file

def main():
    startTime = time.time()
    # 過濾篩選可能有效的資料夾
    dirList = list()
    for d in os.listdir():
        if os.path.isdir(os.path.join("", d)):
            if d != "urls" and d != "words" and d != "__pycache__" and d!= "img":
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
                    foreman(url_file_name=dirList[int(dirIdex)] + "_urls_1", working_dirPath=dirPath)
                    foreman(url_file_name=dirList[int(dirIdex)] + "_urls_0", working_dirPath=dirPath)
                    print("恭喜，完成這流程最長的環節。")
                    print("接下來，使用pre-clean_images_v2.sh 來整理下載的圖檔。")
                    break

        print("Cost time: {} ".format(time.time() - startTime))


if __name__ == "__main__":
    main()
