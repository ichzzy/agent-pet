# Agent Pet

一隻住在桌面的寵物，當 Claude Code 思考或執行指令時會動起來。
限 Mac

## 效果

| 狀態 | 表現 |
|------|------|
| Claude 閒置 | 靜態圖（idle.png） |
| Claude 思考 / 執行中 | GIF 動畫（busy.gif） |

## 需求

- Python 3.10+
- macOS（Linux / Windows 需調整視窗 flag）

## 初始化專案

### 1. 建立 venv 並安裝套件

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### 2. 設定 Claude Code Hooks

在 `~/.claude/settings.json` 的 `hooks` 區段加入以下兩個事件：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo 1 > /tmp/claude_busy"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo 0 > /tmp/claude_busy"
          }
        ]
      }
    ]
  }
}
```

### 3. 啟動

```bash
venv/bin/python3 pet.py
```

## 參數

```
--idle PATH    靜態圖路徑（預設：assets/idle.png）
--busy PATH    動態 GIF 路徑（預設：assets/busy.gif）
--width  N     視窗寬度，單位 px（預設：120）
--height N     視窗高度，單位 px（預設：120）
```

範例：

```bash
venv/bin/python3 pet.py --width 150 --height 150
venv/bin/python3 pet.py --idle ~/my-cat.png --busy ~/my-cat-run.gif
```

## 操作

| 動作 | 效果 |
|------|------|
| 左鍵拖曳 | 移動到任意位置 |
| 右鍵單擊 | 關閉程式 |

## 替換圖片

將自訂圖片放入 `assets/` 並覆蓋同名檔案，或透過 `--idle` / `--busy` 參數指定路徑。

- 靜態圖支援：PNG、JPG
- 動態圖支援：GIF（建議透明背景）

## 原理

```
使用者送出訊息 → UserPromptSubmit hook → echo 1 > /tmp/claude_busy → 顯示 GIF
Claude 回覆完畢 → Stop hook           → echo 0 > /tmp/claude_busy → 回靜態圖
```

pet.py 每 1000ms 輪詢 `/tmp/claude_busy`，偵測到變化即切換圖片。

## 打包成 macOS App

安裝 PyInstaller 並產生 `dist/AgentPet.app`：

```bash
venv/bin/pip install pyinstaller
venv/bin/pyinstaller --onedir --windowed \
  --add-data "assets:assets" \
  --icon "assets/AgentPet.icns" \
  --name "AgentPet" -y pet.py
```

完成後將 `dist/AgentPet.app` 拖入 `/Applications` 即可直接使用。
