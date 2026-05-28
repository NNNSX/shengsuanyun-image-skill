# Shengsuanyun Image Skill Usage

## Setup

Use an environment variable whenever possible:

```bash
export SHENGSUANYUN_API_KEY="your_api_key_here"
```

or copy `assets/.env.example` to a private `.env` file and pass `--env-file`:

```bash
cp <skill_dir>/assets/.env.example .env
# edit .env and fill SHENGSUANYUN_API_KEY
python3 <skill_dir>/scripts/shengsuanyun_image.py \
  --env-file .env \
  --prompt "一张白色背景上的蓝色立方体" \
  --name test_cube
```

You can also pass a key once with `--api-key`.

Do not write real API keys into prompts, Markdown files, shared repositories, or checked-in config files.

## Basic Generation

```bash
python3 <skill_dir>/scripts/shengsuanyun_image.py \
  --prompt "一张白色背景上的蓝色立方体，简洁产品摄影风格" \
  --name test_cube \
  --out-dir outputs/shengsuanyun \
  --save-response
```

## Prompt File

```bash
python3 <skill_dir>/scripts/shengsuanyun_image.py \
  --prompt-file prompts/frame_01.txt \
  --name frame_01 \
  --out-dir outputs/shengsuanyun \
  --size 1536x864 \
  --quality auto \
  --save-response
```

## Reference Images

Local files are converted to `data:image/...;base64,...` automatically. URLs are passed through as URLs.

```bash
python3 <skill_dir>/scripts/shengsuanyun_image.py \
  --prompt-file prompts/frame_04.txt \
  --reference-image references/device.png \
  --reference-image references/style.jpg \
  --name frame_04 \
  --out-dir outputs/shengsuanyun \
  --save-response
```

## Common Options

| Option | Purpose |
|---|---|
| `--prompt` | Prompt text |
| `--prompt-file` | UTF-8 prompt file |
| `--reference-image` | Repeatable local path or URL |
| `--env-file` | Optional `.env` file containing `SHENGSUANYUN_API_KEY=...` |
| `--model` | Default `openai/gpt-image-2` |
| `--size` | Default `auto`; common `1536x864`, `1024x1024` |
| `--quality` | Default `auto` |
| `--n` | Number of images |
| `--out-dir` | Output directory |
| `--name` | Output filename prefix |
| `--save-response` | Save create/final JSON |
| `--dry-run` | Print payload only |

## Failure Handling

- `401 Unauthorized`: invalid or missing API key.
- Network/DNS error: retry with network permission if Codex is sandboxed.
- Policy refusal: rewrite the prompt into neutral, non-harmful, non-identifying, or clearly educational/demo language.
- No image URL in final response: inspect the saved final response JSON.
