
流程圖
-------------------
![流程圖](img/project_ML_from_download_to_training.jpg)


安裝
-------------------
Ubuntu16.04 安裝依賴套件：
>sudo apt-get install python3-setuptools python3-dev python3-h5py python3-matplotlib python3-psutil

Python3 安裝依賴套件：
>pip3 install -r requirement.txt


工作流程
--------------------
1) keyword2wnid.py   # 產生專案目錄以及wnid 列表檔
2) wnid2url.py   # 利用wnid 列表檔，產生url 列表檔
3) multithreads_download_from_url_files.py   # 利用url 列表檔，下載圖片資料
3.5) update_url.py   # 清理掉已經下載好的url 列表
4) ./pre-clean_images.sh   # 圖片清理
5) ./clean_images.sh   # 圖片清理
6) images2hdf5.py   # 講圖片檔轉成一個資料檔
7) dnn_2_layers_Training.py   # 一層的深度學習
