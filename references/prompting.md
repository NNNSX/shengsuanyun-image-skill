# Prompting Notes

## Recommended Structure

Use short sections in the prompt:

```text
画面用途：
画幅与风格：
主体：
场景：
文字/HUD：
禁止项：
```

## Reference Image Roles

Tell Codex which reference image is used for which role:

- hardware morphology reference
- layout/style reference
- color/lighting reference
- edit target

Do not use a style image as a hardware morphology reference if the equipment shapes differ.

## Text In Images

For presentation keyframes, keep in-image text sparse:

- Use broad labels instead of dense technical or numeric labels.
- Avoid filling the image with exact numeric parameters unless it is a technical scale diagram.
- Avoid English HUD words unless explicitly requested.

## Refusal-Safe Rewriting

If a prompt is refused, do not try to bypass the policy. First identify what likely triggered the refusal, then rewrite the request into a neutral, non-harmful, non-identifying, or clearly fictional/educational form while preserving the user's legitimate visual goal.

General rewrite principles:

- Replace harmful action with safe visualization, prevention, training, monitoring, simulation, or aftermath-free context.
- Remove instructions that enable real-world harm.
- Remove gore, graphic injury, coercion, or explicit sexual content.
- Use generic fictional people instead of real private individuals.
- For public figures, avoid misleading or defamatory depictions.
- For medical, legal, or financial content, frame images as educational diagrams or general concepts, not individualized advice.
- For copyrighted living-artist styles or protected characters, use high-level visual traits instead of direct imitation.
- For minors, keep content non-sexual, age-appropriate, and ordinary.
- For logos, IDs, documents, credentials, or privacy-sensitive material, avoid realistic forgery or usable personal information.

Examples of safer direction changes:

| Risky direction | Safer direction |
|---|---|
| Graphic injury or gore | Non-graphic safety training diagram, medical first-aid infographic, symbolic warning scene |
| Weapon use or attack instructions | Non-operational safety demo, emergency response training, abstract risk visualization |
| Real person in a compromising scene | Fictional person, non-identifying silhouette, neutral portrait |
| Living artist imitation | Broad traits such as watercolor texture, cinematic lighting, muted palette |
| Brand or document forgery | Fictional placeholder brand, clearly marked sample document |
| Explicit political persuasion | Neutral civic information graphic or historical context illustration |

When rewriting, keep the user's real design needs intact: subject, composition, aspect ratio, intended use, reference-image roles, and output path.
