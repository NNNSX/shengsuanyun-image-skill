# Shengsuanyun Image Skill 中文说明

这个文件夹是一个可分享的 Codex skill，用于通过胜算云 Router API 调用 `openai/gpt-image-2` 生成图片。

## 适用场景

- 用文本提示词生成图片。
- 用提示词文件生成图片。
- 使用一张或多张参考图生成图片。
- 自动提交任务、轮询任务状态、下载生成结果。
- 保存请求响应 JSON，便于排查失败原因。

## 文件结构

```text
shengsuanyun-image/
├── SKILL.md                         # Codex 读取的 skill 说明
├── 中文自述.md                       # 中文使用说明
├── scripts/
│   └── shengsuanyun_image.py         # 通用画图脚本
├── references/
│   ├── usage.md                      # 命令行用法
│   └── prompting.md                  # 提示词与拒绝后改写建议
├── assets/
│   ├── .env.example                  # API Key 模板
│   └── example_prompt.txt            # 示例提示词
└── agents/
    └── openai.yaml                   # Codex UI 元数据
```

## 安装方式

把整个 `shengsuanyun-image` 文件夹复制到 Codex 的 skills 目录：

```bash
cp -R shengsuanyun-image ~/.codex/skills/
```

之后在 Codex 里可以说：

```text
使用 shengsuanyun-image skill，根据 prompts/frame_01.txt 生成一张图片，输出到 outputs/shengsuanyun。
```

## 配置 API Key

推荐使用环境变量：

```bash
export SHENGSUANYUN_API_KEY="你的API Key"
```

也可以复制模板创建私有 `.env` 文件：

```bash
cp shengsuanyun-image/assets/.env.example .env
```

然后编辑 `.env`：

```text
SHENGSUANYUN_API_KEY=你的API Key
```

不要把真实 API Key 写入 `SKILL.md`、Markdown 文档、代码仓库或共享文件。

## 直接命令行生成

```bash
python3 shengsuanyun-image/scripts/shengsuanyun_image.py \
  --env-file .env \
  --prompt-file shengsuanyun-image/assets/example_prompt.txt \
  --name test_image \
  --out-dir outputs/shengsuanyun \
  --size 1536x864 \
  --quality auto \
  --save-response
```

生成结果会输出到：

```text
outputs/shengsuanyun/
```

同时会保存：

```text
test_image_create_response.json
test_image_final_response.json
test_image_01.png 或 test_image_01.jpg
```

## 使用参考图

本地参考图和网络图片 URL 都可以作为参考图。多个参考图可以重复传入 `--reference-image`。

```bash
python3 shengsuanyun-image/scripts/shengsuanyun_image.py \
  --env-file .env \
  --prompt-file prompts/frame_01.txt \
  --reference-image references/style.jpg \
  --reference-image references/product.png \
  --name frame_01 \
  --out-dir outputs/shengsuanyun \
  --size 1536x864 \
  --quality auto \
  --save-response
```

建议在提示词中说明每张参考图的用途，例如：

```text
第一张参考图用于画面风格。
第二张参考图用于产品外形。
不要把风格参考图中的设备形态当作产品形态。
```

## 常用参数

| 参数 | 说明 |
|---|---|
| `--prompt` | 直接传入提示词 |
| `--prompt-file` | 从 UTF-8 文本文件读取提示词 |
| `--reference-image` | 参考图路径或 URL，可重复使用 |
| `--env-file` | 读取包含 `SHENGSUANYUN_API_KEY` 的 `.env` 文件 |
| `--api-key` | 单次命令传入 API Key，不推荐长期使用 |
| `--model` | 默认 `openai/gpt-image-2` |
| `--size` | 图片尺寸，常用 `1536x864`、`1024x1024` 或 `auto` |
| `--quality` | 质量，默认 `auto` |
| `--n` | 生成数量 |
| `--out-dir` | 输出目录 |
| `--name` | 输出文件名前缀 |
| `--save-response` | 保存创建和最终响应 JSON |
| `--dry-run` | 只打印请求体，不调用 API |

## 调试请求体

如果只想检查请求体，不真正生成图片：

```bash
python3 shengsuanyun-image/scripts/shengsuanyun_image.py \
  --env-file .env \
  --prompt "一张白色背景上的蓝色立方体" \
  --dry-run
```

## 常见问题

`Missing API key`：
没有设置 `SHENGSUANYUN_API_KEY`，也没有传入 `--api-key` 或 `--env-file`。

`HTTP 401`：
API Key 无效或过期。

网络或 DNS 报错：
当前运行环境可能限制联网，需要允许命令访问外部网络后重试。

生成结果不符合要求：
优先修改提示词重新生成，不要用裁切、遮挡等方式掩盖主体错误。

提示词被拒绝：
参考 `references/prompting.md`，将提示词改写为中性、非伤害、非伪造、非隐私侵犯的表达。
