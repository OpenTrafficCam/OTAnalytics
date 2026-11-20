# Fonts of the web UI

Bundled so the web UI needs no internet connection. Latin subset (includes
German umlauts) as WOFF2, taken from Fontsource 5.1.0 on npm.

| Font        | Weights       | Used for                   | License    |
| ----------- | ------------- | -------------------------- | ---------- |
| Open Sans   | 400, 600, 700 | Text                       | OFL 1.1    |
| Roboto Mono | 400           | Numbers, file names, times | Apache 2.0 |
| Amatic SC   | 700           | Brand in the header        | OFL 1.1    |

The license texts are next to the fonts:

- `OFL-open-sans.txt`: SIL Open Font License 1.1 of Open Sans
- `LICENSE-roboto-mono.txt`: Apache License 2.0 of Roboto Mono
- `OFL-amatic-sc.txt`: SIL Open Font License 1.1 of Amatic SC

`otanalytics.css` declares them with `@font-face`; `add_fonts()` in
`global_theme.py` serves this folder.
