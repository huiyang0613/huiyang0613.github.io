# Editing this homepage

The homepage is a static page generated from JSON content and an HTML template. Edit the sources, then run `python3 scripts/build.py`. Direct changes to the root `index.html` are overwritten on the next build.

## Profile and sections

`_data/profile.json` contains the name, email, biography, social profiles, experience, and miscellaneous information.

- Biography paragraphs support inline HTML for links and emphasis.
- Social links use the icon names defined in `assets/icons.svg`. Only the supplied Google Scholar, Email, and GitHub links are included.
- Experience entries retain the institution, dates, location, lab, advisor, and local logo path from the old homepage.
- The current Misc. section contains academic service. Optional `interests` and `other` values can be filled in later to add a Beyond research column; empty values do not display placeholders.
- The portrait was copied from the supplied `profile.jpg` without changing the image. Keep its width and height attributes in `templates/index.html` consistent when replacing it with a differently sized photo.

## Publications

Each publication has a separate JSON file in `_publications/`. GenHOI and HOMAE were migrated with their original author order, summaries, images, and external links.

Required fields are `title`, `venue`, `selected`, `authors`, `media`, and `links`. Optional fields are `summary` and `highlight`.

- Filenames use `YYYY_MM_...json`. They determine the descending display order and year heading; there is no separate publication `date` field.
- `selected` must be the JSON boolean `true` or `false`. Both initial papers are selected.
- Prefix a filename with `_` to hide a record in both views while retaining its source.
- The profile owner's name is bolded in author lists automatically. An author name ending in `*` adds the Equal contribution note.
- Image media uses `{"type": "image", "src": "files/Project/teaser.png"}`. An optional `hover_src` enables switching by mouse hover, touch, or keyboard.
- Video media uses `type: "video"` with `src` and `poster`. Videos play muted and looping without visible controls, pause off screen, and resume when visible.
- Links point directly to papers, project sites, or code. No internal publication detail pages are generated.

## Build checks

```bash
python3 scripts/build.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p 'test_build.py'
git diff --check
```

The build validates publication filenames and required fields, checks referenced local assets, and formats HTML while preserving inline text and intentional line breaks. The preview server runs the same build when content sources change.

Check the page at desktop and phone widths after layout changes. Confirm the navigation and both publication filters work before publishing.

## GitHub Pages

The intended URL is `https://huiyang0613.github.io/`. There is no custom domain and no `CNAME` file. Keep `.nojekyll` at the publishing root.

When the new version is ready, commit and push `main`, then select **Deploy from a branch → main → /(root)** in Pages settings. If the repository currently uses a Jekyll GitHub Actions workflow, switch its Pages source to Deploy from a branch as part of that release. The static branch intentionally has no Jekyll workflow.

To restore the archived site, select **legacy-jekyll → /(root)** as the publishing source. The archived Jekyll source and its complete history are retained independently; merging it into `main` is unnecessary.
