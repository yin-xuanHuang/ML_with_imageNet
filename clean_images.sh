#!/bin/bash
# 執行此程式前，請先確認是否已經執行完pre-clean_images_v2.sh
# 此程式的工作：
# 1.在 image_1 和 image_0 裡刪除 size 小於 4000bytes 的檔案，
#  （為什麼是4000bytes，這是苦主的經驗談。。。）
#   也就是 pre-clean_images_v2.sh 沒掃到的漏網之魚。
# 2.除了將image_1複製一份到cleaned_dir，
#   另外在製作一份左右對調的image_1圖片到cleaned_dir裡，
#   因為image_1 的資料相對於image_0資料少。
# 3.將cleaned_dir 裡的image_1 總數乘上3倍（預設），
#   就是我們要移入cleaned_dir 的image_0 數量拉，
#   有用亂數選定的方式，以保持分佈均勻。

# 預設 y = 0 的資料量為 y = 1 的資料量三倍（預設）。
((y0dy1=3))

clear

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
echo "1.執行內容有rm指令，移除非圖像檔案!移除後，無法復原！"
echo "2.y=1資料自動flop產生另一張。"
echo "3.y=0的資料，預設最多三倍的y=1數量。"
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

if ! [[ -d "image_1" ]]
then
  echo "image_1 資料夾不存在!"
  exit
elif ! [[ -d "image_0" ]]
then
  echo "image_0 資料夾不存在!"
  exit
fi

mkdir cleaned_dir

echo "第二階段：刪除轉換jpg失敗的，並複製成功的image_1到cleaned_dir，"
echo "並且另外轉換成功的image_1 為 左右對調 到cleaned_dir。"

((count1=0))
((count0=0))
# 轉換jpg失敗的刪除
# image_1轉換成功的複製一份到 cleaned_dir
# image_1 flog 一份到 cleaned_dir
for d in image_1 image_0;
do
  cd "$d"
  pwd
  # 刪除 size 小於 4000bytes 的檔案
  `find . -size -4000c -exec rm "{}" \;`
  for f in *;
  do
    if [[ `file "$f" | grep -v 'JPEG'` == "" ]]
    then
      if [[ "$d" == "image_1" ]]
      then
        cd ..
        cp "$d"/"$f" cleaned_dir/i_"$count1"_"$d".jpg
        convert "$d"/"$f" -flop cleaned_dir/f_"$count1"_"$d".jpg
        cd "$d"
        ((count1+=1))
      else
        ((count0+=1))
      fi
    else
      echo "Remove "$f" : JPEG."
      rm "$f"
    fi
  done
  cd ..
done

((count1=count1 * 2))

echo "image_0:"$count0""
echo "image_1:"$count1""

# 紀錄合法資料數量
echo "image_0:"$count0"" >> count_images
echo "image_1:"$count1"" >> count_images


# 如果 y = 0 資料量小於3倍的 y = 1，那 y = 0 設為原始資料量。
if [[ $(( count0 / count1  )) -ge $y0dy1 ]]
then
  ((count1=count1 * 3))
else
  ((count1=count0))
fi

echo "第三階段：將成功的image_0，亂數選定，最多image_1的3倍數量到cleaned_dir。"

((count=0)) # debug
cd image_0
all_image_0_files=(*)
random_file_range=( $(shuf -i 0-"$((count0 - 1))" -n "$count1" ))
# 複製 image_0 的圖片到 cleaned_dir
for idx in "${random_file_range[@]}";   #使用亂數
do
  cd ..
  cp image_0/"${all_image_0_files[$idx]}" cleaned_dir/i_"$count"_image_0.jpg
  cd image_0
  ((count+=1))
done
cd ..
echo "$count"
echo "clean done."
echo "接下來，按照流程，是執行images2hdf5.py 的時候。"
