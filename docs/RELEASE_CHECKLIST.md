# Release checklist

- [ ] `make release-check` passes on a clean worktree.
- [ ] Version matches `pyproject.toml` and `CHANGELOG.md`.
- [ ] Wheel, sdist, two HTML storyboards, ZIP and SHA256 sums exist.
- [ ] CI is green and no secret-looking values appear in artifacts.
