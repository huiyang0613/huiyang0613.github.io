# Hui Yang's personal homepage

A single-page static academic homepage for Hui Yang (杨慧), prepared for [huiyang0613.github.io](https://huiyang0613.github.io/). The site does not use Jekyll and has no custom domain.

## Editing content

- `_data/profile.json`: biography, contact links, experience, and academic service.
- `_publications/*.json`: one file per publication.
- `templates/index.html`: page structure.
- `styles.css` and `site.js`: desktop/mobile layout and interactions.
- `assets/images/profile.jpg`: the supplied portrait.
- `files/`: publication images and institution logos.

GenHOI and HOMAE are both marked `"selected": true`. **Show selected** is the default view. Set `"selected": false` to show a paper only under **Show all**. Files whose names start with `_` remain in the repository but are hidden in both views.

Publications are sorted by filename in descending order. Use a zero-padded `YYYY_MM_` prefix; a separate `date` field is not needed. The site displays publication information directly on the homepage and does not generate individual publication pages.

## Build and preview

Run commands inside the `main` worktree:

```bash
python3 scripts/build.py
python3 scripts/preview.py --port 8766
```

Open [the local preview](http://127.0.0.1:8766/). Refresh after editing: the preview server rebuilds the homepage when its content sources change. Stop it with Ctrl+C.

The build generates and formats `index.html` with two-space indentation. It uses Python 3's standard library only. No Ruby, npm, Jekyll, or separate HTML formatter is required.

## Publish when ready

Rebuild after changing the profile, publications, or template. GitHub Pages serves the committed `index.html`; it does not read the JSON files or run this Python script automatically.

```bash
python3 scripts/build.py
git status
git add -A
git diff --cached --stat
git commit -m "Update the static homepage"
git push origin main
```

Review the staged changes before committing. Include source data, generated HTML, and any changed assets together.

For this static version, use the repository's **Settings → Pages → Deploy from a branch**, with **main** and **/(root)**. Leave **Custom domain** empty and retain `.nojekyll`. No `CNAME` file is needed. The legacy Jekyll workflow is removed from this version.

The previous site remains on `legacy-jekyll` in its own local worktree and remote branch. Both versions can be maintained independently; no merge between these branches is needed to switch the published design.

See [DEVELOPMENT.md](DEVELOPMENT.md) for more editing details. The sibling `WORKTREE_GUIDE.md` explains the two local worktrees.
