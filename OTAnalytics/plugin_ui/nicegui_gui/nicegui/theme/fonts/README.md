# Fonts of the web UI

Bundled so the web UI needs no internet connection. Latin subset (includes
German umlauts) as WOFF2, taken from Fontsource 5.1.0 on npm.

| Font | Weights | Used for | License |
| --- | --- | --- | --- |
| Open Sans | 400, 600, 700 | Text | SIL Open Font License 1.1 (`OFL-open-sans.txt`) |
| Roboto Mono | 400 | Numbers, file names, times | Apache License 2.0 (`LICENSE-roboto-mono.txt`) |
| Amatic SC | 700 | Brand in the header | SIL Open Font License 1.1 (`OFL-amatic-sc.txt`) |

`otanalytics.css` declares them with `@font-face`; `add_fonts()` in
`global_theme.py` serves this folder.
