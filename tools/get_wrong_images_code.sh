#!/bin/bash

# 切換工作資料夾
cd wrong_image

# 砍掉原本的
rm wrong_image_signature
rm wrong_image_size

# 建立新的
touch wrong_image_signature
touch wrong_image_size

# 寫入signature hash 到檔案中
for i in *;
do
 echo `identify -verbose -format "%#" "$i"` >> wrong_image_signature
done

# 寫入圖片size 到檔案中
for i in *;
do
 echo `convert "$i" -format "%w x %h" info:` >> wrong_image_size
done
