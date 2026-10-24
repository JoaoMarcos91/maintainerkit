# MaintainerKit

**Small, review-first issue triage for open-source maintainers.** MaintainerKit is a GitHub Action that summarizes incoming issues, suggests existing labels, asks for missing details, and flags possible duplicates. It is built with Python's standard library and is designed to fail safely.

> MaintainerKit is an early MVP. Treat all generated triage as a suggestion, not as ground truth. It does not close issues, assign people, or change labels by default.

## What it does

- Runs when a regular issue is opened, edited, or reopened.
- Posts or updates one MaintainerKit comment instead of creating a new comment every run.
- Uses labels that already exist in the repository; it does not invent label names.
- Scans a configurable number of recent open issues to suggest possible duplicates.
- Works without an AI key using a small deterministic fallback classifier.
- Supports an optional OpenAI-compatible `/chat/completions` endpoint for richer summaries and triage.
- Applies suggested labels only when `apply_labels: 'true'` is explicitly configured.
- Uses only Python's standard library at runtime; no `pip install` is needed.

## Quick start

1. Copy `action.yml` and `src/maintainerkit.py` into your repository, or fork this repository.
2. Add the workflow below as `.github/workflows/maintainerkit.yml`.
3. In **Settings → Actions → General → Workflow permissions**, allow the workflow to write issues if your repository requires that setting.
4. Open a test issue and inspect the bot's comment.

```yaml
name: MaintainerKit
on:
  issues:
    types: [opened, edited, reopened]
permissions:
  contents: read
  issues: write
jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          api_key: ${{ secrets.MAINTAINERKIT_API_KEY }} # optional
          model: gpt-4.1-mini
          apply_labels: 'false'
```

For a local action in the same repository, the `uses` value must be `./`. The ready-to-copy version is in [`.github/workflows/triage.yml`](.github/workflows/triage.yml).

### Optional AI mode

Without `MAINTAINERKIT_API_KEY`, MaintainerKit uses its deterministic fallback. To enable AI mode, add a repository Actions secret named `MAINTAINERKIT_API_KEY`, then set it as the `api_key` input. The default base URL is `https://api.openai.com/v1`; set `base_url` to another compatible API base URL when appropriate. API usage may incur charges depending on the provider and account. **The fallback mode is the only mode that does not require an AI provider or API billing.**

Inputs:

| Input | Required | Default | Description |
|---|---:|---|---|
| `github_token` | Yes | — | Token with issue read/write access; normally `secrets.GITHUB_TOKEN` |
| `api_key` | No | empty | Optional AI provider key |
| `base_url` | No | `https://api.openai.com/v1` | OpenAI-compatible API base URL, or full `/chat/completions` endpoint |
| `model` | No | `gpt-4.1-mini` | Provider model name |
| `apply_labels` | No | `false` | Apply only existing, recommended labels |
| `max_issue_scan` | No | `30` | Recent open issues to consider (clamped to 5–100) |

## Safety and privacy

- The issue body and candidate issues are untrusted input. In AI mode, the prompt explicitly tells the model not to follow instructions embedded in issue content.
- AI requests send the current issue plus a bounded list of recent open issue titles and short body excerpts to the configured provider. Do not enable AI mode for repositories whose issue content should not leave GitHub unless the provider's data terms and your policies allow it.
- The generated output is constrained and sanitized before inclusion in a comment. Suggested labels must exist in the repository, and duplicate references must come from the issues scanned.
- `apply_labels` defaults to `false`; maintainers remain responsible for reviewing summaries, duplicates, and labels.
- Never place an API key directly in the workflow file. Store it in GitHub Actions secrets.
- Give the workflow the minimum permissions needed. The sample uses `contents: read` and `issues: write`.
- MaintainerKit is not a security scanner and does not verify whether a reported vulnerability is real.

## Development

Requires Python 3.10+ for local tests; GitHub-hosted Ubuntu runners include Python 3.

```bash
python3 -m unittest discover -v
python3 -m py_compile src/maintainerkit.py
```

No runtime dependencies are required. CI runs the tests on pull requests and pushes.

## Roadmap

- [ ] Improve duplicate detection with repository-specific evaluation data.
- [ ] Add configurable category/label mapping.
- [ ] Add integration tests with mocked GitHub and AI endpoints.
- [ ] Document metrics for false-positive labels and duplicate suggestions.
- [ ] Collect maintainer feedback before considering any automatic actions as a default.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the issue templates. Please include tests for behavior changes and avoid submitting real API keys, tokens, private issue data, or user information.

## License

MIT. See [LICENSE](LICENSE).
