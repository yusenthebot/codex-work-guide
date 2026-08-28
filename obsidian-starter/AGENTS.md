# Wiki instructions

This directory is an Obsidian vault maintained with Codex.

## Structure

- `inbox/`: unprocessed notes and ideas
- `sources/`: immutable source material
- `sources/assets/<source-slug>/`: immutable source-native figures, charts and screenshots
- `wiki/`: agent-maintained summaries, entities, concepts and analyses
- `wiki/assets/<source-slug>/`: generated-analysis visuals when a source has no meaningful native image
- `wiki/index.md`: catalog of Wiki pages with one-line descriptions
- `wiki/log.md`: append-only operation history

## Source integrity

- Do not edit or move files in `sources/` unless explicitly asked.
- Cite sources with relative links or stable URLs.
- Keep dates, numbers, names and attribution exact.
- Label inference and unresolved contradictions.
- If the vault does not contain enough evidence, say so.
- Treat landed source-native images as immutable. Use versioned replacement files instead of overwriting them.

## Wiki pages

- Use one focused topic per page.
- Search the index before creating a page.
- Update existing pages when new evidence changes them.
- Use `[[wikilinks]]` for useful relationships.
- Avoid empty pages, duplicate aliases and decorative tags.
- Every new or materially updated source summary must embed at least one durable local image. Mermaid alone is not enough.
- Prefer one to three source-native visuals. When none exists, create a local image under `wiki/assets/` and label it `Generated analysis / 生成式分析图`.
- Put a one-sentence provenance caption below every embedded image.

## Operations

After every ingest, query writeback or lint fix:

1. Update `wiki/index.md`.
2. Append a dated entry to `wiki/log.md`.
3. Verify that image paths exist, files open, labels are readable and captions identify provenance.
4. Report changed files, visual assets and unresolved questions.

For broad changes, list affected pages before editing.
