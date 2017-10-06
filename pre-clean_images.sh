#!/bin/bash
# pre-clean all file data in the directory
'''
此程式的工作：
1. 清除非圖片格式
2. 清除壞檔
3. 清除miss圖片
4. 統一圖片格式
'''

clear

# signature hash of miss images
readarray -t miss_identify_arr < wrong_image_signature

# size of miss images
# 二次確認
readarray -t miss_size_arr < wrong_image_size

declare -a darr=()
echo -n "Working directory(now):"
pwd

# 搜尋資料夾，並排除特定資料夾
for pd in */;
do
  if [[ "$pd" == "urls/" ]] || [[ "$pd" == "words/" ]] || [[ "$pd" == "__pycache__/" ]]
  then
    continue
  else
    darr+=("$pd")
  fi
done

# 將可能的資料夾全部印出
count=0
for pf in "${darr[@]}"
do
  echo "["$count"]:"$pf""
  ((count+=1))
done

# 沒有有效資料夾，則結束程式
if [[ ${#darr[@]} -eq 0 ]]
then
  echo "沒有有效資料夾！"
  exit
fi

# 選擇工作資料夾，並判斷輸入的 idex 是否合格
while true
do
  echo -n "輸入需要pre-clean的資料夾[idex]:> "
  read dir_idex
  if ! [[ "$dir_idex" =~ ^[0-9]+$ ]]
  then
    echo "請輸入自然數！"
  elif [[ "$((${#darr[@]} - 1 ))" -lt "$dir_idex" ]]
  then
    echo "請輸入數字區間0~"$((${#darr[@]} - 1 ))""
  else
    break
  fi
done

# 再次確認
echo ""
echo "注意！"
echo "執行內容有rm指令，移除非圖像檔案!移除後，無法復原！"
echo -n "請再次確認資料夾： "${darr[$dir_idex]}" (yes or no): "
read doOrnot
if [[ "$doOrnot" != "yes" ]]
then
  echo "程式結束!"
  exit
fi

# 切換到工作資料夾
cd ./"${darr[$dir_idex]}"
echo -n "Working directory(now):"
pwd

# 檢查image_0 image_1 是否存在
if ! [[ -d "image_1" ]]
then
  echo "image_1 資料夾不存在!"
  exit
elif ! [[ -d "image_0" ]]
then
  echo "image_0 資料夾不存在!"
  exit
fi

echo "第一階段：刪除miss images, not image dat 並且全部轉換成jpg。"
# error or miss 檔案處理開始
# 轉jpg
for d in image_1 image_0;
do
  cd "$d"
  pwd
  for f in *;
  do
    if [[ `file "$f" | grep -v 'image data\|PC bitmap'` == "" ]]
    then
      identify_f=`identify -verbose -format "%#" "$f"`
      if [[ " ${miss_identify_arr[@]} " =~ " $identify_f " ]]
      then
        size_f=`convert "$f" -format "%w x %h" info:`
        if [[ " ${miss_size_arr[@]} " =~ " $size_f " ]]
        then
          # delete miss image
          echo "Remove "$f": Miss image."
          rm $f
          continue
        fi
      fi
      cd ..
      convert "$d"/"$f" "$d"/"$f".jpg
      rm "$d"/"$f"
      cd "$d"
    else
      echo "Remove "$f" : Not image data."
      rm "$f"
    fi
  done
  cd ..
done
echo "Pre-clean images done!"
echo "接下來請執行clean_images.sh"
