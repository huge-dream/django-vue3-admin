#!/bin/sh
# 获取传入的全局参数
dist_folder=$1
icon_path=$2

# 清空dmg文件夹。
rm -rf "$dist_folder/DVAServer"
rm -rf "$dist_folder/main"
# 如果DMG已经存在，则删除它。
test -f "$dist_folder/DVAServer.dmg" && rm "$dist_folder/DVAServer.dmg"
create-dmg \
  --volname "DVAServer" \
  --volicon $icon_path \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "DVAServer.app" 175 120 \
  --hide-extension "DVAServer.app" \
  --app-drop-link 425 120 \
  "$dist_folder/DVAServer.dmg" \
  "$dist_folder/"
