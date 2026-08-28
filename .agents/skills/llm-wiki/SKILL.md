---
name: llm-wiki
description: Maintain a persistent Markdown knowledge base for Codex and Obsidian. Use when the user asks to ingest sources, query the wiki, file a useful answer, update cross-links or run a wiki health check.
---

# LLM Wiki

Maintain a Markdown wiki that separates immutable sources from agent-written knowledge pages.

## Locate the wiki

Use the directory named by the user. If none is given, look for `sources/`, `wiki/index.md` and `wiki/log.md` in the current project. Stop and ask before creating a new wiki outside the current project.

Read the wiki's `AGENTS.md` before changing files. Its local schema overrides this Skill when the two differ.

## Rules

- Never rewrite files in `sources/`.
- Cite source files and URLs for factual claims.
- Separate confirmed facts, source claims and inference.
- Do not hide contradictions. Record both claims and their dates.
- Prefer updating an existing topic page over creating a duplicate.
- Keep `wiki/index.md` current.
- Append one entry to `wiki/log.md` after every completed operation.
- Every new or materially updated source summary must embed at least one durable local image. Mermaid alone does not satisfy this requirement.
- If the wiki cannot support an answer, say so and list what is missing.
- Show the changed-file list at the end.

## Visual asset contract

- Prefer one to three high-information source-native visuals: architecture diagrams, method figures, result charts, tables, UI screenshots or representative frames.
- Store source-native visuals under `sources/assets/<source-slug>/`. Treat them as immutable after landing; corrections use a versioned replacement file.
- If the source has no meaningful native visual, create one explanatory image under `wiki/assets/<source-slug>/` and label it `Generated analysis / 生成式分析图`. Never present generated analysis as source evidence.
- For PDFs, render the relevant page, crop only when it improves readability and inspect the final image before filing it.
- For web pages, preserve a stable original image when possible; otherwise capture the relevant page section with the browser workflow.
- For repositories, prefer an official architecture image, verified UI or output screenshot, or a generated diagram grounded in inspected code.
- Embed images with Obsidian syntax such as `![[sources/assets/<source-slug>/<image>.png]]` or `![[wiki/assets/<source-slug>/<image>.png]]`.
- Put a one-sentence provenance caption directly below each image. Identify the original figure or page, screenshot source, or generated-analysis status.
- Before completion, verify every image path exists, the file opens, labels are readable and the caption records provenance.
- Keep the collection selective. Do not archive an entire paper or website as screenshots when one to three visuals explain the source.

## Operations

### Ingest

1. Read `wiki/index.md` and the new source.
2. Identify existing pages affected by the source.
3. Select and land one to three useful source-native images, or create a clearly labeled generated-analysis fallback when no meaningful source image exists.
4. Create or update the source summary, entity and concept pages. Embed at least one verified local image with a provenance caption in the source summary.
5. Add `[[wikilinks]]` where the relationship is useful.
6. Mark conflicts, uncertainty and publication dates.
7. Update the index and append an `ingest` log entry that records the number and type of visual assets added.

For a large change, list affected pages before editing. Do not rewrite unrelated pages.

### Query

1. Read the index, then the most relevant pages and cited sources.
2. Answer with page references and a confidence boundary.
3. If the result has lasting value, ask before filing it unless the user already requested writeback.
4. When filing, create or update one focused page, then update the index and log.

### Lint

Check for broken links, orphan pages, duplicate topics, stale claims, contradictions, missing citations and gaps worth researching. Also check for source summaries without a local image, broken image embeds, unreadable crops and captions without provenance. Report findings before making broad changes. Safe index and link repairs may be applied when the user requested fixes.

## Log format

```markdown
## [YYYY-MM-DD] ingest | Source title
- Updated: [[page-a]], [[page-b]]
- Visuals: 2 source-native figures under sources/assets/source-title/
- Notes: short description
```

Use `query` or `lint` in place of `ingest` for those operations.

## Reference

This workflow follows Andrej Karpathy's LLM Wiki pattern:
https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
