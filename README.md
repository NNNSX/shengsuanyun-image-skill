# 胜算云 gpt-image-2 画图 Skill

这是一个给 Codex 使用的画图 skill。它封装了胜算云 Router API，可以让 Codex 通过 `openai/gpt-image-2` 生成图片，并支持提示词文件、参考图、自动轮询和结果下载。

普通用户不需要理解 `SKILL.md` 或脚本细节。你只需要安装这个文件夹、配置 API Key，然后用自然语言告诉 Codex 你想画什么。

## 一、安装

把整个仓库放到 Codex 的 skills 目录：

```bash
cd ~/.codex/skills
git clone https://github.com/NNNSX/shengsuanyun-image-skill.git shengsuanyun-image
```

如果你是下载 zip 包，也可以解压后把文件夹改名为：

```text
~/.codex/skills/shengsuanyun-image
```

最终目录应类似：

```text
~/.codex/skills/shengsuanyun-image/
├── SKILL.md
├── README.md
├── scripts/
├── references/
└── assets/
```

## 二、配置 API Key

推荐在你的项目目录里创建 `.env` 文件：

```bash
cp ~/.codex/skills/shengsuanyun-image/assets/.env.example .env
```

然后编辑 `.env`：

```text
SHENGSUANYUN_API_KEY=你的胜算云API Key
```

不要把真实 API Key 上传到 GitHub，也不要写进共享文档。

你也可以使用环境变量：

```bash
export SHENGSUANYUN_API_KEY="你的胜算云API Key"
```

## 三、告诉 Codex 怎么用

安装后，你可以在 Codex 里直接说：

```text
使用 shengsuanyun-image skill，帮我生成一张 16:9 的产品概念图，输出到 outputs/shengsuanyun。
```

或者：

```text
使用 shengsuanyun-image skill，读取 prompts/frame_01.txt 作为提示词，参考 references/style.jpg 的风格，生成一张图。
```

或者：

```text
使用 shengsuanyun-image skill，用 references/device.png 作为设备外形参考，帮我生成一张真实摄影风格的演示图。
```

用户只需要描述需求。Codex 会根据 `SKILL.md` 自动选择脚本、读取提示词、附加参考图、调用 API 并保存结果。

## 四、常见需求示例

### 1. 纯文本画图

```text
使用 shengsuanyun-image skill，画一张明亮工作室中的智能硬件产品图，真实摄影感，少量中文标注。
```

### 2. 读取提示词文件

```text
使用 shengsuanyun-image skill，读取 prompts/image_prompt.txt 生成图片，保存到 outputs/shengsuanyun。
```

### 3. 使用参考图

```text
使用 shengsuanyun-image skill，参考 references/style.jpg 的画面风格，并参考 references/product.png 的产品外形，生成一张宣传图。
```

### 4. 调试提示词

```text
使用 shengsuanyun-image skill，先 dry-run 检查 prompts/image_prompt.txt 的请求体，不要真正调用 API。
```

## 五、输出位置

默认建议输出到：

```text
outputs/shengsuanyun/
```

通常会得到：

```text
image_name_01.png 或 image_name_01.jpg
image_name_create_response.json
image_name_final_response.json
```

JSON 文件用于排查任务状态、失败原因和远端返回内容。

## 六、用户需要知道的几个点

1. `SKILL.md` 是给 Codex 看的，不是普通用户教程。
2. `README.md` 是给用户看的安装和使用说明。
3. 真实 API Key 只放在你自己的 `.env` 或环境变量中。
4. 参考图要说明用途，例如“这张是风格参考”“这张是产品外形参考”。
5. 如果生成结果不符合预期，让 Codex 修改提示词重新生成，不要用遮挡或裁切掩盖主体错误。

## 七、直接命令行使用

一般用户不需要手动运行脚本。如果你想直接命令行使用，可以这样：

```bash
python3 ~/.codex/skills/shengsuanyun-image/scripts/shengsuanyun_image.py \
  --env-file .env \
  --prompt-file prompts/image_prompt.txt \
  --reference-image references/style.jpg \
  --name image_test \
  --out-dir outputs/shengsuanyun \
  --size 1536x864 \
  --quality auto \
  --save-response
```

更多脚本参数见：

```text
references/usage.md
```

