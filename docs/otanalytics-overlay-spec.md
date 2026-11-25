# Canvas overlay spec (option B + focus mode)

- Chips show the section **name**, never the id. Arrows only for **selected** flows. Track palette out of scope.
- Python emits geometry + state classes only; all styling is in `otanalytics.css`. Keep all existing element ids.
- Dots = zero-length path `d="M{x} {y}h0"`; size = stroke width. Items in screen px go in `<g transform="translate(x y)"><g class="ota-scaled">…</g></g>`.

## Markup

```html
<!-- layer: class "ota-overlay"; + "ota-focus" while _is_editor_active() -->
<rect class="ota-dim" width="{W}" height="{H}"/>
<g id="{id}" class="ota-section [area] [selected] [editing]">          <!-- polyline or polygon -->
  <polyline class="glow" …/><polyline class="casing" …/><polyline class="line" …/>
  <path class="pt-ring" d="M x y h0"/><path class="pt" d="M x y h0"/>   <!-- per point -->
  <g transform="translate(x+8 y-30)"><g class="ota-scaled ota-chip">  <!-- area: centroid -->
    <rect width="{16+7*len(name)}" height="22" rx="6"/><text x="8" y="15">{name}</text></g></g>
</g>
<g class="ota-knob [active]">                                           <!-- active = hovered/dragged -->
  <path class="halo" …/><path class="ring" …/><path class="core" …/><path class="hit" …/></g>
<line class="ota-rubber" …/>                                            <!-- last point → mouse -->
<g id="arrow-{a}-{b}" class="ota-flow [stale]">
  <path class="casing" d="M p0 Q c p1"/><path class="line" d="M p0 Q c p1"/>
  <g transform="translate(p1) rotate(angle(p1-c))"><g class="ota-scaled"><polygon class="head" points="0,0 -12,-5 -12,5"/></g></g>
  <g transform="translate(curve(0.5))"><g class="ota-scaled ota-badge">
    <rect x="{-w/2}" y="-10" width="{w=16+7*len(count)}" height="20" rx="10"/><text y="4">{count}</text></g></g>
</g>
```

`c` = midpoint + 12 % of length, perpendicular left. Hint bar (HTML, while editing): `<div class="ota-hint"><i></i><b>Editing {name}</b>Drag points · + add · Del remove · Enter finish · Esc cancel</div>`.

Scale, in `CanvasForm.build()`: `new ResizeObserver(([e]) => e.target.style.setProperty('--ota-s', e.target.viewBox.baseVal.width / e.target.clientWidth)).observe(layerSvg)`

## CSS

```css
.ota-overlay{--ota-s:1;--sage:#b4cbc0;--pri:#37483e;--cas:rgba(28,38,32,.7);font-family:"Open Sans",sans-serif}
.ota-overlay *{vector-effect:non-scaling-stroke;fill:none;stroke-linecap:round;stroke-linejoin:round}
.ota-scaled{transform:scale(var(--ota-s))}
.ota-dim{fill:rgba(17,24,21,.45);pointer-events:none;display:none}
.ota-focus .ota-dim{display:inline} .ota-focus .ota-section:not(.editing){opacity:.4}
.ota-focus .ota-flow{display:none}
/* The layer ignores the mouse (NiceGUI: pointer-events:none), so the cursor goes on the image below it. */
.ota-canvas:has(> .ota-focus) > img{cursor:crosshair}  /* CanvasForm adds ota-canvas to the image */

.ota-section{cursor:pointer}
.ota-section .glow{stroke:var(--sage);stroke-opacity:.35;stroke-width:14;opacity:0}
.ota-section:hover .glow{opacity:1}
.ota-section .casing{stroke:var(--cas);stroke-width:6}
.ota-section .line{stroke:var(--sage);stroke-width:3;pointer-events:stroke}
.ota-section .pt-ring{stroke:var(--sage);stroke-width:12} .ota-section .pt{stroke:var(--pri);stroke-width:8}
.ota-section.area .casing{stroke-width:5}
.ota-section.area .line{stroke-width:2;fill:var(--sage);fill-opacity:.2;pointer-events:all}
/* While editing, clicks pass through sections to the image, so a point can be added on top of a section. */
.ota-focus .ota-section .line{pointer-events:none}
.ota-section:is(.selected,.editing) .casing{stroke:var(--pri);stroke-width:9}
.ota-section:is(.selected,.editing) .line{stroke:#fff;stroke-width:4}
.ota-section.area:is(.selected,.editing) .casing{stroke-width:7}
.ota-section.area:is(.selected,.editing) .line{stroke-width:3;fill:#fff;fill-opacity:.12}
.ota-section.selected .pt-ring{stroke:var(--pri);stroke-width:14} .ota-section.selected .pt{stroke:#fff;stroke-width:10}

.ota-chip rect{fill:var(--pri);stroke:var(--sage);stroke-width:1}
.ota-chip text{fill:#fff;stroke:none;font-size:12px;font-weight:600}
.ota-section:hover .ota-chip rect{fill:#4a5e52;stroke:#fff}
.ota-section.selected .ota-chip rect{fill:#fff;stroke:var(--pri);stroke-width:1.5}
.ota-section.selected .ota-chip text{fill:var(--pri)}

.ota-knob{cursor:move} .ota-knob .halo{stroke:#fff;stroke-opacity:.25;stroke-width:26;opacity:0}
.ota-knob .ring{stroke:var(--pri);stroke-width:17} .ota-knob .core{stroke:#fff;stroke-width:12}
.ota-knob.active .halo{opacity:1} .ota-knob.active .ring{stroke:#fff;stroke-width:19}
.ota-knob.active .core{stroke:var(--pri);stroke-width:14}
.ota-knob :not(.hit){pointer-events:none}
.ota-knob .hit{stroke:#000;stroke-opacity:0;stroke-width:20;pointer-events:stroke} .ota-knob.active .hit{stroke-width:400}
.ota-rubber{stroke:#fff;stroke-width:2;stroke-dasharray:5 4;pointer-events:none}

.ota-flow{pointer-events:none} .ota-flow .casing{stroke:var(--cas);stroke-width:6}
.ota-flow .line{stroke:#fff;stroke-width:3} .ota-flow .head{fill:#fff;stroke:var(--cas);stroke-width:1}
.ota-badge rect{fill:#fff;stroke:var(--pri);stroke-width:1.5}
.ota-badge text{fill:var(--pri);stroke:none;font:600 11px "Roboto Mono",monospace;text-anchor:middle}
.ota-flow.stale{opacity:.55} .ota-flow.stale .line{stroke-dasharray:8 5}
.ota-flow.stale .ota-badge rect{fill:#fdeec4;stroke:#b48a2a} .ota-flow.stale .ota-badge text{fill:#7a5a14}

.ota-hint{position:absolute;top:12px;left:12px;display:flex;align-items:center;gap:10px;padding:6px 10px;
  border-radius:8px;background:rgba(255,255,255,.95);box-shadow:0 4px 12px rgba(17,24,21,.25);font-size:12px;color:#596d63}
.ota-hint b{color:#37483e} .ota-hint i{width:8px;height:8px;border-radius:50%;background:#37483e}
```

## Python

- `nicegui/svg/*`: drop all colour, stroke, fill and font fields; emit the markup above.
- `canvas_form.py`: delete the colour/size constants; set state classes; toggle `ota-focus` on the layer; add hint bar and ResizeObserver.
- `dummy_viewmodel._draw_sections()` passes `text=<section name>` to `draw_section()` (today it passes none). `_draw_arrow_for_selected_flows()` passes `count=get_tracks_assigned_to_each_flow().get(flow.id)`; add `count: int | None = None` to `AbstractCanvas.draw_arrow` (CustomTkinter ignores it).
- Pointer events use the target's id (`knob_index_from_element_id`). So the `.hit` path carries `id="edit-knob-{n}"` and is always present (`stroke-width` 20, 400 while dragging via `.ota-knob.active .hit`); all other knob paths get `pointer-events:none`. Point paths of a selected section carry the old circle ids `{id}-{n}`.
- Dim rect size = current image size (`_change_image`). Hint bar name: `self._current_section.name`, or "New line section"/"New area" while drawing.
- Update the unit tests in `tests/unit/.../nicegui_gui/nicegui/svg/` and `test_canvas_form.py`; they assert colour and stroke attributes.
- First check that NiceGUI's SVG sanitiser keeps `class` and `transform`.

## Editor affordances

Drawn by `CanvasForm` while a section is edited. Like all overlay markup they carry geometry and state classes only; sizes in screen px use `screen_px`, so they need the scale `--ota-s`. The browser also reports it to the server (`scalechange` event of the layer), which needs it to compare mouse positions with screen px sizes.

```html
<!-- knob: number of the knob inside its core, 1-based -->
<g class="ota-knob [active] [moving]">… <g transform="translate(x y)"><g class="ota-scaled"><text class="num">3</text></g></g> <path class="hit" id="edit-knob-2"/></g>
<!-- insert a knob in the middle of a segment (below the knobs, hidden while a knob is picked up) -->
<path class="ota-mid" id="edit-mid-{segment}" d="M x y h0"/><g transform="translate(x y)"><g class="ota-scaled ota-mid-plus"><path d="M-5 0h10M0-5v10"/></g></g>
<!-- shift ring around the picked up knob, shown once the mouse is still; label = position the knob gets -->
<g transform="translate(x y)"><g class="ota-scaled ota-shift">
  <path id="edit-shift-backward" class="half [hovered]"><title>…</title></path><text class="label">◀1</text>
  <path id="edit-shift-forward" class="half [hovered]"><title>…</title></path><text class="label">3▶</text></g></g>
<!-- preview of the section after the hovered shift -->
<g id="edit-shift-preview" class="ota-section editing preview">…</g>
<!-- finish/cancel pill next to the last placed knob, hidden while a knob is dragged -->
<g transform="translate(x y)"><g class="ota-scaled ota-action">
  <rect id="edit-action-background" class="background"/>
  <circle id="edit-action-finish" class="button finish [disabled]"/><path class="glyph"/>
  <circle id="edit-action-cancel" class="button cancel"/><path class="glyph"/></g></g>
```

The browser only reports pointer events of elements whose id starts with `edit-knob-`, `edit-mid-`, `edit-shift-` or `edit-action-`.
