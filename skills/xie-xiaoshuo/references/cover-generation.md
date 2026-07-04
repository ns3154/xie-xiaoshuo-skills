# 小说封面生成

本文件是 `xie-xiaoshuo` 自带的封面流程。用户要封面、封面图、封面设计、上架素材时读取本文件，不转交其他技能。

## 目录

- 输入与依赖
- 平台尺寸
- 题材判定
- 风格库
- 提示词构建
- 调用图片 API
- 导出上传尺寸
- 质量检查与交付

## 输入与依赖

最低输入：

- 书名：必须由用户、项目资料或明确文件给出。
- 作者名/笔名：必须由用户、项目资料或明确文件给出。
- 目标平台：不知道时默认“其他平台竖版”，但如果用户要番茄、起点、晋江、知乎盐言、七猫、刺猬猫等平台，必须按平台风格处理。
- 输出目录：默认 `covers/<书名>`；用户指定时以用户指定为准。

书名和笔名缺任一时必须先问，不得编造、留空或用“作者名”占位。

环境变量：

| 变量 | 必填 | 默认 | 说明 |
|---|---:|---|---|
| `GPT_IMAGE_API_KEY` | 是 | 无 | OpenAI 或兼容代理的图片 API Key |
| `GPT_IMAGE_BASE_URL` | 否 | `https://api.openai.com/v1` | 兼容代理时覆盖 |
| `GPT_IMAGE_MODEL` | 否 | `gpt-image-2` | 图片模型 |
| `GPT_IMAGE_SIZE` | 否 | `1024x1536` | 生成尺寸，番茄建议 `768x1024` |
| `UPLOAD_SIZE` | 否 | 无 | 平台上传像素，例如番茄 `600x800` |
| `BOOK_DIR` | 是 | 无 | 输出目录，建议 `./covers/<书名>` |
| `REF_IMAGE` | 否 | 无 | 参考图本地路径或 URL，设置后走图生图 |

依赖命令：`curl`、`jq`、`base64`。导出上传尺寸优先用 `magick` 或 `convert`，macOS 可用 `sips` 兜底。

## 平台尺寸

| 平台 | 上传尺寸 | 比例 | 建议生成尺寸 |
|---|---:|---|---|
| 番茄小说 | 600x800 | 3:4 | `768x1024` |
| 其他竖版平台 | 按平台要求 | 常见 2:3 | `1024x1536` |

平台有固定上传尺寸时设置 `UPLOAD_SIZE`，后续用居中裁剪加缩放导出上传版。不要依赖中转代理一定遵守 `GPT_IMAGE_SIZE`，最终平台尺寸由本文件“导出上传尺寸”步骤保证。

## 题材判定

扫描书名、简介、项目设定和正文关键词。多题材命中时优先级：仙侠 > 西幻 > 古言 > 现言 > 都市 > 悬疑 > 科幻 > 历史 > 灵异 > 轻小说；无命中默认都市。

| 关键词 | 题材 | 英文标签 |
|---|---|---|
| 仙、道、剑、灵、修、宗、天、帝、尊、神 | 玄幻/仙侠 | `xianxia fantasy` |
| 都市、总裁、校园、重生、系统、学霸、医生、兵王 | 都市 | `urban modern` |
| 妃、皇、侯、宫、嫡、庶、后、朝、凤、鸾 | 古言 | `ancient romance` |
| 契约、替嫁、甜宠、娇妻、萌宝、闪婚 | 现言 | `modern romance` |
| 诡、案、侦探、悬疑、推理、密室、连环 | 悬疑 | `mystery thriller` |
| 星际、末世、机甲、赛博、废土、进化 | 科幻 | `sci-fi` |
| 龙、骑、魔法、异世界、精灵、领主 | 西幻 | `western fantasy` |
| 三国、大明、大唐、战场、将军、谋士 | 历史 | `historical epic` |
| 鬼、僵尸、阴阳、风水、盗墓、咒 | 灵异 | `supernatural horror` |
| 萌、喵、团宠、娇、转生 | 轻小说 | `light novel` |

## 风格库

### 平台风格

| 平台 | 英文关键词 |
|---|---|
| 番茄小说 | `vibrant saturated colors, eye-catching bold design, character portrait dominating frame, mass-market novel cover style, high contrast` |
| 起点 | `polished refined illustration, detailed cinematic composition, epic atmospheric, mature sophisticated style, premium quality` |
| 晋江 | `dreamy ethereal aesthetic, soft pastel tones, elegant romantic, delicate beauty, flower petals and bokeh` |
| 知乎盐言 | `minimalist literary style, clean composition with negative space, subtle moody atmosphere, independent film poster aesthetic` |
| 七猫 | `striking high-impact design, vivid dramatic colors, spectacular visual effects, attention-grabbing poster style` |
| 刺猬猫 | `anime illustration style, vibrant colorful, detailed character art, Japanese light novel aesthetic` |

### 题材风格

| 题材 | 画面标签 | 色彩 | 人物与背景 |
|---|---|---|---|
| 玄幻/仙侠 | `xianxia Chinese fantasy art style, ethereal atmosphere` | 深蓝、金、白、玄黑 | 长发束冠、剑/法器、云海、仙山、灵力光效 |
| 都市 | `modern urban contemporary style, clean cinematic composition` | 深蓝、灰、金、霓虹 | 西装/休闲装、城市天际线、办公室、校园、霓虹街 |
| 古言 | `ancient Chinese romance palace drama, elegant classical beauty` | 正红、金、墨黑 | 华服、凤冠步摇、宫殿、庭院、红墙、灯笼 |
| 现言 | `modern romance cover art, soft dreamy warm atmosphere` | 粉、暖白、浅金 | 双人互动、咖啡厅、花园、室内、夕阳海滩 |
| 悬疑 | `dark mystery thriller, noir atmosphere, high contrast shadows` | 黑、深灰、暗蓝、血红 | 剪影、背影、雨夜街道、老建筑、密室、暗巷 |
| 科幻 | `sci-fi cyberpunk, futuristic technology, post-apocalyptic` | 深蓝、黑、银、霓虹蓝紫 | 机甲、战术服、太空、废墟城市、实验室 |
| 西幻 | `western high fantasy, epic medieval atmosphere` | 深蓝、暗金、银白 | 骑士、法师、龙、城堡、魔法阵 |
| 历史 | `historical Chinese war epic, grand battlefield panorama` | 铁灰、暗红、土黄 | 将军、谋士、战场、城墙、军营、烽火 |
| 灵异 | `Chinese supernatural horror, eerie ghostly atmosphere` | 墨黑、幽绿、暗红 | 道士、鬼影、纸人、墓地、古庙、棺材 |
| 轻小说 | `anime light novel cover, vibrant colorful moe style` | 明亮多色 | 动漫角色、Q版元素、校园、异世界、星光 |

### 字体风格

| 题材 | 书名字体 | 作者名字体 |
|---|---|---|
| 玄幻/仙侠 | `bold golden brush calligraphy with metallic glow and sharp strokes` | `small refined white serif text with faint golden glow, flanked by delicate cloud-scroll ornaments, resting on a thin horizontal gold line` |
| 都市 | `modern bold sans-serif with metallic silver finish` | `small clean white modern text with subtle drop shadow, positioned above a thin silver horizontal divider line` |
| 古言 | `elegant golden traditional Kai script with ornate decoration` | `small elegant dark red traditional text inside a thin golden rectangular border frame with corner decorations` |
| 现言 | `soft rounded handwritten style in white with pink glow` | `small soft pink-white handwritten text with a tiny heart motif on the left side, light sparkle effect` |
| 悬疑 | `distorted bold cracked letters in blood red` | `small pale grey text with slight blur effect, almost hidden in the shadows, a thin cracked line underneath` |
| 科幻 | `neon glowing futuristic font in electric blue` | `small crisp white monospace text with subtle cyan scanline overlay, flanked by small geometric brackets` |
| 西幻 | `metallic embossed fantasy lettering with glow effect` | `small bronze medieval script text with aged parchment texture, enclosed in a small decorative shield or banner shape` |
| 历史 | `heavy stone-carved seal script in deep red` | `small dignified white Song typeface text above a double horizontal line in dark red` |
| 灵异 | `eerie dripping handwritten font in sickly green` | `small faded grey-green text slightly tilted, with a thin dripping ink line above` |
| 轻小说 | `colorful cartoon outlined bubbly font` | `small playful rounded white text with pastel color outline, tiny star decorations on both sides` |

## 提示词构建

提示词用英文写，直接包含中文书名和作者名。结构：

```text
Chinese web novel cover design, [平台风格].
Title text '{书名}' at top center in [书名字体].
Author name '{作者名}' at bottom center in [作者名字体].
[题材画面标签]. [具体人物描述]. [背景三层描述].
[色彩指令]. [光效指令].
Professional book cover, high detail digital painting, portrait [比例] ratio, keep title and author name inside the central safe area away from edges (inner 85%), no watermark
```

人物描述要具体到服饰、姿态、发型、表情、道具；背景按前景、中景、远景分层；光效指定方向和颜色。封面用 `digital painting style`，不要做真人照片感。

构图可选：人物特写、全身动态、纯场景、双人对峙/互动。首次生成可给 2-3 个构图方案，但真正调用 API 前只用一个完整提示词，避免模型目标分散。

## 调用图片 API

先设置变量：

```bash
export GPT_IMAGE_API_KEY="你的key"
export BOOK_DIR="./covers/书名"
export GPT_IMAGE_SIZE="1024x1536"
export UPLOAD_SIZE=""
export PROMPT="上一步拼好的英文提示词"
```

番茄示例：

```bash
export GPT_IMAGE_SIZE="768x1024"
export UPLOAD_SIZE="600x800"
```

文生图：

```bash
set -euo pipefail
: "${GPT_IMAGE_API_KEY:?请设置 GPT_IMAGE_API_KEY}"
: "${PROMPT:?请设置 PROMPT}"
: "${BOOK_DIR:?请设置 BOOK_DIR}"
BASE_URL="${GPT_IMAGE_BASE_URL:-https://api.openai.com/v1}"
MODEL="${GPT_IMAGE_MODEL:-gpt-image-2}"
SIZE="${GPT_IMAGE_SIZE:-1024x1536}"

mkdir -p "$BOOK_DIR/封面"
i=1
while [ -f "$BOOK_DIR/封面/封面_v${i}.png" ]; do i=$((i+1)); done
OUT="$BOOK_DIR/封面/封面_v${i}.png"
RESP=$(mktemp)
trap 'rm -f "$RESP"' EXIT

BODY=$(jq -n --arg m "$MODEL" --arg p "$PROMPT" --arg s "$SIZE" '{model:$m, prompt:$p, size:$s}')
curl -fsS --max-time 180 --retry 2 --retry-delay 5 \
  "$BASE_URL/images/generations" \
  -H "Authorization: Bearer $GPT_IMAGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$BODY" > "$RESP"

if jq -e '.error' "$RESP" >/dev/null 2>&1; then
  jq '.error' "$RESP" >&2
  exit 1
fi

jq -er '.data[0].b64_json // empty' "$RESP" | base64 --decode > "$OUT"
[ -s "$OUT" ] || { echo "empty or malformed output: $OUT" >&2; head -c 300 "$RESP" >&2; exit 1; }
printf '%s\n' "$PROMPT" > "${OUT%.png}.prompt.txt"
file "$OUT"
```

图生图：设置 `REF_IMAGE` 后走 `images/edits`。本地参考图必须存在；URL 先下载到临时文件。

```bash
set -euo pipefail
: "${GPT_IMAGE_API_KEY:?请设置 GPT_IMAGE_API_KEY}"
: "${PROMPT:?请设置 PROMPT}"
: "${BOOK_DIR:?请设置 BOOK_DIR}"
: "${REF_IMAGE:?请设置 REF_IMAGE}"
BASE_URL="${GPT_IMAGE_BASE_URL:-https://api.openai.com/v1}"
MODEL="${GPT_IMAGE_MODEL:-gpt-image-2}"
SIZE="${GPT_IMAGE_SIZE:-1024x1536}"

mkdir -p "$BOOK_DIR/封面"
i=1
while [ -f "$BOOK_DIR/封面/封面_v${i}.png" ]; do i=$((i+1)); done
OUT="$BOOK_DIR/封面/封面_v${i}.png"
RESP=$(mktemp)
REF_TMP=""
trap '[ -n "$REF_TMP" ] && rm -f "$REF_TMP"; rm -f "$RESP"' EXIT

case "$REF_IMAGE" in
  http://*|https://*) REF_TMP=$(mktemp); curl -fsSL --max-time 60 -o "$REF_TMP" "$REF_IMAGE"; REF_LOCAL="$REF_TMP" ;;
  *) [ -f "$REF_IMAGE" ] || { echo "参考图不存在: $REF_IMAGE" >&2; exit 1; }; REF_LOCAL="$REF_IMAGE" ;;
esac

curl -fsS --max-time 240 --retry 2 --retry-delay 5 \
  "$BASE_URL/images/edits" \
  -H "Authorization: Bearer $GPT_IMAGE_API_KEY" \
  --form-string "model=$MODEL" \
  --form-string "size=$SIZE" \
  --form-string "prompt=$PROMPT" \
  -F "image=@$REF_LOCAL" > "$RESP"

if jq -e '.error' "$RESP" >/dev/null 2>&1; then
  jq '.error' "$RESP" >&2
  exit 1
fi

jq -er '.data[0].b64_json // empty' "$RESP" | base64 --decode > "$OUT"
[ -s "$OUT" ] || { echo "empty or malformed output: $OUT" >&2; head -c 300 "$RESP" >&2; exit 1; }
printf '%s\n' "$PROMPT" > "${OUT%.png}.prompt.txt"
printf '%s\n' "$REF_IMAGE" > "${OUT%.png}.ref.txt"
file "$OUT"
```

## 导出上传尺寸

设置了 `UPLOAD_SIZE` 时，把原图居中裁剪加缩放成平台精确像素，另存 `_上传.png`，不覆盖原图。

```bash
SRC="${OUT:-$(ls -t "${BOOK_DIR:-.}"/封面/封面_v*.png 2>/dev/null | grep -v _上传 | head -1)}"
TARGET="${UPLOAD_SIZE:-}"
if [ -n "$TARGET" ] && [ -f "$SRC" ]; then
  UP="${SRC%.png}_上传.png"; W="${TARGET%x*}"; H="${TARGET#*x}"
  if command -v magick >/dev/null 2>&1; then M=magick
  elif command -v convert >/dev/null 2>&1; then M=convert
  else M=""; fi

  if [ -n "$M" ]; then
    "$M" "$SRC" -resize "${W}x${H}^" -gravity center -extent "${W}x${H}" "$UP"
  elif command -v sips >/dev/null 2>&1; then
    cp "$SRC" "$UP"
    sw=$(sips -g pixelWidth "$UP" | awk '/pixelWidth/{print $NF}')
    sh=$(sips -g pixelHeight "$UP" | awk '/pixelHeight/{print $NF}')
    if [ $((sw*H)) -ge $((sh*W)) ]; then sips --resampleHeight "$H" "$UP" >/dev/null
    else sips --resampleWidth "$W" "$UP" >/dev/null; fi
    sips -c "$H" "$W" "$UP" >/dev/null
  else
    echo "缺少 magick/convert/sips，跳过上传尺寸导出" >&2
  fi
  [ -f "$UP" ] && file "$UP"
fi
```

## 质量检查与交付

检查项：

- 文字渲染：书名清晰，作者名可读，不能被裁切或遮挡。
- 题材匹配：画面、字体、色彩符合题材和目标平台。
- 构图合理：主体突出，文字在中心安全区，核心人物和书名不互相遮挡。
- 平台适配：比例和上传版像素正确；番茄上传版应为 `600x800`。
- 文件完整：原图、上传版、提示词副本存在；图生图时保留参考图记录。

交付时说明：封面文件位置、提示词副本位置、是否生成上传版、目标平台、书名/作者名是否清晰、是否需要下一版迭代。用户不满意时，只调整构图、色调、字体、平台风格或人物描述，不动小说正文。
