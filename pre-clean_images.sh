#!/bin/bash
# pre-clean all file data in the directory
'''
1. 清除非圖片格式
2. 清除壞檔
3. 清除miss圖片
4. 統一圖片格式
'''



clear

# signature hash of miss images
declare -a miss_identify_arr=(\
"d4a4670b11e2417464335769490b733ad959496426f2b5704ec6be297a133233" \
"6063b581031cee0e0ae77f1a3f881a4ea0d22efdcbd56213c5aca0f374d33c27" \
"6688801de89661b46437baaea5bcd8ab857e136d7f109a2986e16419ecea9ee4" \
"c50781d3d929f9f3232f5baa988898ef8daa5591b0e395c973c1c999f3c900ae" \
"91f80c9893c8225c48a3413439fe29baeb6b396e594cf0aead3f26cea0a6b484" \
"1f5c9a8f9081d2c49b48c16415d3e83a31b595e5c75133c995da0c92e2b637fb" \
"d1fffff4fb594a425bfc9c3ff0ff5027b37338be5ee82ce2a66530e2f95d6ed3" \
"80cbe63642ee775d6abcc85cfd384ae70713570021e7c78936049d01a86e9e60" \
"230111da249d63ff7ec52416fae0c27da67c2fd6737e877c8cb6d57f95a4adc7" \
"8803cf3c04d6b3e221520f8400f3662371d709260b11e41a213abbc3228e770f" \
"21bd8cef75b8317a1c659f8d5882ec4b385b6fa280d5298cb0abdc153e771d94" \
"97ce74f08c601dd19fcf0ba6a7fda4843450f6e68d3072c80899b8b0fbf2e301" \
"91a5fc1b8ca65a2669d350e47eb07b33c673242819436a6da2ec550e7876b8fd" \
"78099efe4dac098628e366b692052ec328d96aa5a0bf08cc971107e44f7cffa2" \
"fe293b3cbe5a0fdf156d08692e11ae6b29f99a0b9d394cca82e7c858b2fc74a8")

# size of miss images
# 二次確認
declare -a miss_size_arr=(\
"200 x 200" \
"240 x 240" \
"500 x 374" \
"55 x 55" \
"371 x 450" \
"827 x 230" \
"775 x 185" \
"200 x 200" \
"240 x 134" \
"640 x 480" \
"400 x 250" \
"90 x 90" \
"374 x 53" \
"222 x 168" \
"140 x 120")

declare -a darr=()
echo -n "Working directory(now):"
pwd

# 搜尋資料夾，並排除特定資料夾
for f in */;
do
  if [[ "$f" == "urls/" ]] || [[ "$f" == "words/" ]]
  then
    continue
  else
    darr+=("$f")
  fi
done

# 將可能的資料夾全部印出
count=0
for f in "${darr[@]}"
do
  echo "["$count"]:"$f""
  count+=1
done

# 選擇工作資料夾，並判斷輸入的 idex 是否合格
while true
do
  echo -n "輸入需要pre-clean的資料夾[idex]:> "
  read dir_idex
  if [[ ${#darr[@]} -le $dir_idex ]] || [[ $dir_idex -lt 0 ]] || [[ "$dir_idex" == "" ]]
  then
    echo "請輸入數字區間0~"$((${#darr[@]} - 1 ))""
  else
    break
  fi
done

# 切換到工作資料夾
cd ./"${darr[$dir_idex]}"
echo -n "Working directory(now):"
pwd

# 合法檔案格式
declare -a allowArr=("JPEG" "PNG" "GIF" "PC")
mkdir cleaned_dir
cleaned_dir="../cleaned_dir"

# 檔案處理開始
for d in image_*;
do
  cd "$d"
  pwd
  count_num=0
  for f in *;
  do
    description=`file -b $f`
    d_extension=${description%% *}
    killed="NO"
    # 判斷是否為合法圖片格式
    if [[ " ${allowArr[@]} " =~ "$d_extension" ]]
    then
      # miss images compare
      identify_f=`identify -quiet -format "%#" $f`
      if [[ " ${miss_identify_arr[@]} " =~ "$identify_f" ]]
      then
        size_f=`convert "$f" -format "%w x %h" info:`
        if [[ " ${miss_size_arr[@]} " =~ "$size_f" ]]
        then
          # delete miss image
          echo "Remove "$f": Miss image."
          rm "$f"
          killed="YES"
        fi
      fi
      # 統一圖片格式為JPEG
      if [[ "$killed" == "NO" ]]
      then
        if [[ "$d_extension" != "JPEG" ]]
        then
          `convert "$f" "$cleaned_dir"/i_"$count_num"_"$d".JPEG`
        else
          `cp "$f"  "$cleaned_dir"/i_"$count_num"_"$d".JPEG`
        fi
      fi
    else
      # 非合法圖片刪除
      echo "Remove "$f": Not a image file."
      rm "$f"
    fi
    ((count_num+=1))
  done
  cd ..
done
echo "Pre-clean images done!"
