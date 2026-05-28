---
name: shengsuanyun-image
description: Generate images with Shengsuanyun Router using openai/gpt-image-2, including prompt-file generation, local or URL reference images, task polling, downloads, and saved JSON responses. Use when the user wants Codex to call the Shengsuanyun image API, use gpt-image-2 through router.shengsuanyun.com, or package/reuse this API-based image generation workflow.
---

# Shengsuanyun Image

Use this skill to generate images through Shengsuanyun Router's task API, typically with `openai/gpt-image-2`.

## Core Rules

- Never store real API keys in shared files.
- Prefer `SHENGSUANYUN_API_KEY` or a private `--env-file .env` over `--api-key`.
- Use the bundled script instead of rewriting API callers.
- Save generated images into the current project unless the user asks for preview-only output.
- If reference images are used, state each image's role: hardware reference, style reference, layout reference, or edit target.
- If network/DNS fails in a sandboxed environment, rerun the same command with the required network permission.

## Files

- Script: `scripts/shengsuanyun_image.py`
- Usage reference: `references/usage.md`
- Prompting reference: `references/prompting.md`
- Config template: `assets/.env.example`
- Example prompt: `assets/example_prompt.txt`

Read `references/usage.md` when you need command examples or option details. Read `references/prompting.md` when preparing complex prompts or when a prompt is refused.

## Standard Workflow

1. Decide whether the request uses direct prompt text or a prompt file.
2. Decide whether reference images are needed and label their role.
3. Put the API key in `SHENGSUANYUN_API_KEY`, a private `.env` file, or use the user-provided key only for the command.
4. Run:

```bash
python3 <skill_dir>/scripts/shengsuanyun_image.py \
  --prompt-file <prompt.txt> \
  --env-file .env \
  --name <output_name> \
  --out-dir <output_dir> \
  --size 1536x864 \
  --quality auto \
  --save-response
```

5. Add one or more `--reference-image <path-or-url>` options if needed.
6. Inspect the generated image before judging success.
7. If the image fails the user's constraints, revise the prompt and regenerate rather than manually hiding major generated-image errors.

## Common Commands

Direct prompt:

```bash
python3 <skill_dir>/scripts/shengsuanyun_image.py \
  --prompt "一张白色背景上的蓝色立方体，简洁产品摄影风格" \
  --name test_cube \
  --out-dir outputs/shengsuanyun \
  --save-response
```

Prompt file with reference image:

```bash
python3 <skill_dir>/scripts/shengsuanyun_image.py \
  --prompt-file prompts/frame_01.txt \
  --reference-image references/style.jpg \
  --name frame_01 \
  --out-dir outputs/shengsuanyun \
  --size 1536x864 \
  --quality auto \
  --save-response
```

Dry run:

```bash
python3 <skill_dir>/scripts/shengsuanyun_image.py \
  --prompt-file prompts/frame_01.txt \
  --reference-image references/style.jpg \
  --dry-run
```

## Output

The script prints JSON containing:

```json
{
  "request_id": "...",
  "images": ["outputs/shengsuanyun/name_01.png"]
}
```

When `--save-response` is used, it also writes:

- `<name>_create_response.json`
- `<name>_final_response.json`

## Troubleshooting

- `Missing API key`: set `SHENGSUANYUN_API_KEY` or pass `--api-key`.
- `HTTP 401`: the token is invalid.
- Network/DNS failure: rerun with network permission.
- Policy refusal: rewrite into a neutral, non-harmful, non-identifying, or clearly educational/demo form; see `references/prompting.md`.
- Reference image ignored: try fewer references and make each role explicit in the prompt.
