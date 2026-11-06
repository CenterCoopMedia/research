# Design system

Every value on the page comes from a token in the `:root` block in
`styles/00-tokens.css`, which the join puts at the top of `report.css`. The
build writes one small block ahead of it that sets the five theme colors from
`report.json` and nothing else. If you want to change how the
report looks, change a token. If you find yourself typing a raw size or color
into a rule, the system is missing a token and the rule is a bug.

## Color

The theme carries five colors: `--paper`, `--ink`, `--accent`, `--secondary`,
`--wash`. Everything else is mixed from them with `color-mix()` in oklab, so a
new theme moves the whole page and never leaves a stranded gray behind.

| Token | Mix | Default | On paper | Use |
|---|---|---|---|---|
| `--ink-soft` | ink 80% on paper | `#4d4c47` | 7.76:1 | standfirst, secondary reading text |
| `--muted` | ink 62% on paper | `#706f69` | 4.55:1 | labels, captions, footnotes, byline date, the stage progress fill |
| `--rule` | ink 16% on paper | `#d2cfc8` | 1.40:1 | quiet hairlines and dividers |
| `--rule-strong` | ink 52% on paper | `#84837d` | 3.43:1 | any edge that is a control's only affordance |
| `--card-border` | ink 28% on paper | `#b7b5ae` | 1.85:1 | card and panel borders |
| `--line` | secondary 70% with ink | `#3e5548` | 7.29:1 | connection lines in the artwork |
| `--ink-strong` | ink 88% with black | `#21211d` | 14.57:1 | primary button on hover |
| `--focus` | accent | `#a33e36` | 5.74:1 | focus ring |
| `--select` | accent 22% on paper | `#e7cbc1` | 9.53:1 behind ink | `::selection` |
| `--scrim` | paper 70%, transparent | | | veil behind the contents panel |

Text holds 4.5:1 or better everywhere, captions included. `--rule` is meant to
be quiet, not invisible; anything a reader can click or tab to gets
`--rule-strong` so its boundary clears 3:1. The methods band sits on `--wash`,
so it redefines `--muted` locally as ink 66% on wash, which keeps that text at
4.81:1 on its own background.

`--rule-strong` is the border of anything a reader can click, and it holds
3.43:1 on paper. It is not the stage progress fill: that fill sits on `--wash`
rather than on paper, where the same mix reads 2.99:1, so the fill takes
`--muted` and holds 3.96:1 against its own track.

Every mix above is measured on all four themes, not on the default alone, and
two themes were moved to keep the floor. Cool's ink was `#243535`, which put
`--muted` at 4.14:1 on its paper and 4.28:1 on its wash; it is `#1b2828`, which
puts the same text at 4.75:1 and 4.93:1. Clay's ink was `#2b2a33`, which put
`--muted` at 4.48:1, and its accent was `#b8622b`, which put the sidenote
number and the ordered-list marker at 3.97:1 on paper and the citation counter
and the takeaways marker at 3.51:1 on the wash; they are `#292831` and
`#9b5324`, which put those at 4.59:1, 5.23:1 and 4.62:1. Night needed nothing.
On every theme, `--rule-strong` on `--wash` is the one pair under 3:1, at
2.99:1 on warm; nothing a reader clicks rests on that pair, and the one place
it would have (the progress fill) takes `--muted` instead.

The ruling inside a drawing is ink at 16 percent, the same value `--rule`
carries, so the grid under the marks reads as ruled paper rather than as a
haze. It dissolves under a radial mask instead of stopping at a rectangle.

The drawing is seeded per report. `seed_from` takes the report's `url`, or its
`title` where it states no url, and reduces it to a blake2s digest; `seeded`
mixes that digest with the mark's index and the property it answers for. The
stroke count, the size, the weight, the jitter and the angle of every mark
follow it, and so does the bend of each ruled line, so two reports in one theme
open on two drawings and no report opens on another's. The digest is used rather
than `hash()`, which is salted per process and would draw a different cover on
every build. A report with neither field takes seed 0, which is the drawing the
kit shipped with, so the guide specimens and the mark set they show are
unchanged. The angle the seed writes on each mark is the angle `report.js`
reads, so the scatter, the groups, the network and the orbit all follow the seed
as well.

`examples/social.py` paints every social card, the sample's own `og-image.png`
included, from the page's own drawing at the page's own seed, and in the faces
of the preset the page names. Each card is a 256 colour PNG under 90 KB.

Every page declares a `color-scheme`, and the build reads it off the paper
rather than typing it. `theme.py` takes the paper's WCAG relative luminance and
writes `dark` below 0.18 and `light` above it, in the same block that carries
the five colors. A reader whose system is set to dark then gets scrollbars and
form chrome that match the report's own paper instead of chrome painted for a
theme the page does not have, and a report on a dark paper gets dark chrome
even when the reader's system is light. The stylesheet states no scheme of its
own: it cannot know which paper the report was built with, and two answers on
one page is one too many. 0.18 is the middle of the sRGB range; every paper in
the themes table sits far from it.

Color-mix in oklab is required. That means a 2023 or newer browser. The icon is
the one color that is not mixed by the stylesheet, because it is a file rather
than a rule; `build.py` mixes it in oklab itself, so it lands on the same value
a `color-mix()` would give.

Figures take their categorical color from the same five. `--series-1` is the
accent, `--series-2` the secondary, `--series-3` the oklab midpoint of the two,
and `--series-4` that midpoint carried 45 percent toward ink. On the default
theme they hold 5.74:1, 5.53:1, 5.60:1 and 8.43:1 against paper, and 5.00:1,
4.82:1, 4.88:1 and 7.34:1 against the wash, so every series clears 3:1 on both
grounds. Four is the cap. A fifth series is small multiples, not a fifth color,
because four hues are already more than a reader can hold at once and the
hue-blind reader needs the pattern fills either way. A panel of a small
multiple draws in `--series-1` whatever its place in the set, because its own
heading names its series and a color would say nothing the heading does not.

Two more tints name a state rather than a role. `--tint-row` is the table row
under the pointer, which is `--wash`. `--mark-hover` is a figure mark under the
pointer or the focus ring, which is ink at 100 percent.

The text furniture holds these ratios on the default theme, measured on the
demo at 1440.

| What | Ratio |
| --- | --- |
| Callout and caveat title, `--muted` on `--wash` | 4.81:1 |
| Notes title, back link, sidenote, `--muted` on `--paper` | 4.55:1 |
| Sidenote number, `--accent` on `--paper` | 5.74:1 |
| Glossary definition, `--ink-soft` on `--paper` | 7.76:1 |
| Takeaways item, `--ink` on `--wash` | 11.47:1 |
| Step title, step text, footnote text, summary text, `--ink` on `--paper` | 13.17:1 |

Z-order is stated once, so no rule types a number of its own: `--z-stage` 2 for
the pinned band, `--z-header` 10 for the sticky header, `--z-grain` 20 for the
paper tooth, `--z-panel` 24, `--z-popover` 26, `--z-toast` 28 and `--z-skip` 30
for the skip link, which is over everything because it is the first control a
keyboard reader reaches.

## Type

Three roles, four presets, and a set of files the build embeds.

`--font-body` sets the sentences and everything with no face of its own.
`--font-display` sets the headings and the large numerals. `--font-label` sets
the header chrome, buttons, nav, eyebrows, captions, byline, step card headings
and footnotes. `--w-display` is the weight the display face takes, `--vs-body`
and `--vs-display` are the variable-axis settings each role runs at, and
`--num-display` is `lining-nums tabular-nums`, which every numeral takes so a
column of figures shares one baseline and one width.

`--font-serif` and `--font-sans` are still there as aliases of `--font-body`
and `--font-label`. Nothing in the kit reads them; they are here so a rule
written against the old names still resolves. `--font-numeral` is the body face
with lining tabular figures: a table, a date column, a list marker and a chart
label read in the face the sentences read in. Only the two large numerals, the
finding value and the part number, take the display face and the display
weight.

`--font-code` is the one exception and it is not used by a report at all. The
guide prints command lines a reader has to transcribe exactly, and a
proportional face makes a flag, a path and a line continuation hard to read, so
`pre` and `code` on that page run in a mono stack.

### The presets

A report names one preset in its `fonts` block. Every preset carries a display
weight of 800 or more, because the cover and the numerals are the two places
the page is allowed to be loud.

| Preset | Body | Display | Label | Weight | Axes |
|---|---|---|---|---|---|
| `system` | the serif stack | the serif stack | the sans stack | 800 | none |
| `field` | Figtree | Bricolage Grotesque | Figtree | 800 | none |
| `quill` | Nunito Sans | Fraunces | Nunito Sans | 900 | `SOFT` 100, `WONK` 1 |
| `ink` | Recursive, `CASL` 0 | Recursive, `CASL` 1 | Recursive, `CASL` 0 | 1000 | `MONO` 0 |

`system` is the default and it embeds nothing: a report with no `fonts` block
carries no font bytes and asks no font server for anything, which is what the
kit did before the presets. Its display weight is 800, which the reader's own
stack draws at whatever weight it has.

### The files

`fonts/` holds one variable woff2 for each family, latin subset, from Google
Fonts, with that family's OFL licence text beside it. A character outside the
latin subset falls back to the next family in the stack, so a report in a
language the subset does not cover still reads, in the reader's own faces.

| File | Bytes | Axes in the file | Presets that use it |
|---|---|---|---|
| `figtree.woff2` | 20,156 | `wght` 300 to 900 | `field` |
| `nunito-sans.woff2` | 31,076 | `wght` 200 to 1000 | `quill` |
| `fraunces.woff2` | 121,016 | `opsz`, `SOFT`, `WONK`, `wght` 100 to 900 | `quill` |
| `recursive.woff2` | 304,988 | `CASL`, `CRSV`, `MONO`, `slnt`, `wght` 300 to 1000 | `ink` |
| `bricolage-grotesque.woff2` | 76,888 | `opsz`, `wght` 200 to 800 | `field` |

The folder is 576,088 bytes of faces and 21,974 bytes of licences. A page
carries only the files its own preset names: `field` embeds 97,044 bytes, which
is about 130 KB once it is base64. Bricolage Grotesque ships as the whole
variable file rather than as a pinned 800 instance, which would be 21,748
bytes: one variable file to a family is the rule, and the range is what lets
the optical size follow the type size.

`kit/fonts.py` turns a preset into `@font-face` rules and into the tokens
above. The default export writes the files it needs into the page as base64
data URIs, so an export still opens from a disk with no network. Hosted-asset
mode links `{assets_url}/fonts/<file>` instead. `package.py` ships `fonts/` in
the ZIP, reading each woff2 as bytes rather than as text.

### The scale

| Token | Size | Line height | Role |
|---|---|---|---|
| `--t-1` | 13px | `--lh-label` 1.5 | eyebrows, labels, captions, controls, footer |
| `--t0` | 15px | `--lh-label` | contents rows, small copy, sidenotes |
| `--t1` | 17px | `--lh-body` 1.55 | step card headings, glossary terms, timeline events |
| `--t-read` | 20px | `--lh-body` | the body |
| `--t2` | 22px | `--lh-subhead` 1.45 | running subheads, `h3`, brand mark |
| `--t3` | 28px | `--lh-title` 1.29 | section titles, quote |
| `--t4` | 40px to 61px | `--lh-display` 1.2 | cover title, findings numerals |

Seven steps, and only two things on the page are allowed to be large: the cover
title and the findings numerals. Nothing is uppercase. Labels take
`--track-label` at 0.01em; display type takes normal tracking.

`--t-read` is the body alone. The steps above it are fixed sizes, so a step
card, a caption and a label do not grow with the prose. Measure is `--reading`,
34em of the body size, so it follows the type instead of guessing at it: 680px
at 20px, which measures 62 to 66 characters a line in every preset and never
reaches 75. The 30em of 17px it replaced measured 51, which is under the
comfortable range rather than in it.

## Space

`--s1` 4px, `--s2` 8px, `--s3` 12px, `--s4` 16px, `--s5` 24px, `--s6` 32px,
`--s7` 48px, `--s8` 64px, `--s9` 96px, `--s10` 128px. The scale kept its
numbering while 64px was missing, so `--s8` went back in its place and no other
name moved. Paragraph gap is `--s5`, heading to body is `--s6`, a section
heading clears its section by `--s7`.

Three lengths sit off that scale because they are the size of one thing:
`--quote-rule` 40px opens a pull quote, `--card-w` 416px is the step card and
the column it sits in, and `--panel-w` is the contents panel. `--band-skirt` is
`--s7` under another name: the soft edge below the phone band, which the step
slots clear as well as the band itself.

## Grid

One gutter and three role widths. A role always uses its own width, so the page
reads as disciplined without every element sharing one left edge.

| Token | Value | Role | Left edge at 1440, reading | Wide | At 390 |
|---|---|---|---|---|---|
| `--wrapper` | 1400px | header, cover, notice, footer | 84px | 84px | 32px |
| `--figure` | 1092px | scrolly stage, findings grid | 174px | 84px | 32px |
| `--reading` | 34em, 680px at 20px | prose, quote, cover deck, section headings that open prose | 380px | 84px | 32px |
| `--rail` | `22 * --t0`, 330px | sidenotes, pull quotes, a figure marked for it | none | 812px | none |
| `--gutter` | `clamp(32px, 8vw - 24px, 64px)` | page margin | 64px | 64px | 32px |

`--col` is the width the reading column takes. In the reading layout it is
`min(--reading, 100%)`, which is what every role width said before the layouts.
In the wide layout it is `min(--reading, 100% - --rail - --s7)`, so a window
between the fold and the width the whole layout wants narrows the measure
rather than pushing the rail past the edge of the page. `--role-inline` is
where a role width sits inside its section, `auto` in the reading layout and
`0` in the wide one; every block that states a role width reads it, so the two
layouts share one set of rules.

A section heading takes the width of what it opens, not a width of its own: it
is on `--reading` over prose and on `--figure` over the findings grid and the
scrolly, so a heading always starts on the left edge of the block under it. The
methods band is two columns inside `--figure`, the note on `--reading` and the
citations beside it.

`--pad-wrapper` is the one formula that puts a full-bleed element on the
wrapper: it is the gutter, or half the space outside 1400px plus the gutter,
whichever is larger. The contents panel uses the same value for its right edge,
so it lands on the header's own right edge.

Section rhythm is flat: `--section` gives every section
`clamp(40px, 5vw, 64px)` top and bottom, whatever it holds. The two bookends,
the cover and the footer, use `--bookend`, which runs to 128px on a tall
screen and backs off on a short one. `--header` is 68px and feeds the sticky
header, the stage offset and `scroll-padding-top`, so those three can never
drift apart. `--cover-art` caps the cover drawing at 48svh so the whole cover,
scroll cue included, stays in one screen.

`--band` is the height of the pinned stage once it becomes a band,
`clamp(220px, 38svh, 320px)`, and the step slots offset their cards by it.
`--reading-print` is the measure on paper, 27em of the printed body size. It is
not a fourth role width; nothing on screen uses it.

Anything that scrolls sideways carries `.scroll-edge`: the table wrapper below
760px and the diagram frame at every width. The hint is an inset shade at the
trailing edge in `--rule-strong`, set while there is more to the side and gone
at the end of the scroll. It is an inset shade and not a drop shadow, because a
drop shadow reads as a card, and on a phone, where the box is the width of the
screen, it falls outside the gutter where nothing can see it.

`--overlay-w` 96vw and `--overlay-h` 92svh are the one pair that is measured
from the window rather than from the grid. The lightbox is the picture at the
size the screen has, so it is capped by the window and by `--wrapper`, and the
picture inside it by `--overlay-h` less `--s10` for the caption and the close
button.

Smooth scrolling is off. A contents jump can cross thousands of pixels, and
animating that runs the reader through every scrolly state on the way, so
jumps are instant and `scroll-padding-top` puts the landing under the header.

## The two layouts

A report names `reading` or `wide` in its `layout` field, and `build.py` writes
the name on `<body>`. `reading` is the default, and it is the centered column
the kit shipped with. Every rule of the wide layout sits in `styles/49-wide.css`
inside `@media screen and (min-width:1001px)`, so below that width, and on
paper at any sheet size, the wide layout is the reading layout. The media type
is there because the width alone is not enough: a landscape or an oversize
sheet has a print viewport of 1001px or more, and the band used to follow it
onto the paper.

The wide layout puts the reading column against the wrapper gutter, which is
the edge the header, the cover, the notice and the colophon already sit on, and
opens a rail beside it. The rail holds three things: the sidenotes of the
section, a pull quote inside a run of paragraphs, and a figure or a table whose
section carries `"rail": true`. Everything else keeps its role width and starts
at the same gutter, so a figure, a table, a timeline and the stage span
`--figure` and break past the column on purpose.

| Layout | Page | Characters a line | Text area at 1440 | Share |
|---|---|---|---|---|
| `reading` | the explainer example | 62 | 680px | 47.2% |
| `wide` | the kit sample | 62 | 1058px | 73.5% |
| `wide` | the report example | 64 | 1058px | 73.5% |
| `wide` | the paper example | 65 | 1058px | 73.5% |
| `wide`, figures | any | n/a | 1092px | 75.8% |

The reading area at 1440 was 35 percent of the viewport and 51 characters a
line before this. Both are fixed: the reading layout covers 47 percent and the
wide layout 74, and no line reaches 75 characters in any preset.

The three rail blocks are placed three different ways, because they arrive
three different ways. A sidenote is already an absolutely positioned column and
the wide layout moves that column to the rail; `scripts/50-notes.js` puts each
note level with its own reference and moves one down when it would land on the
note above it. A pull quote is written inside a run of paragraphs, so it floats
to the rail and gives back the room it took, which keeps it level with the
sentence it lifts and shortens no line of the paragraph beside it; the note
script reads its box, so a note never lands on it. The column is a `flow-root`
in the wide band, so it measures that float: a quote at the end of a short
section is taller than the sentences left beside it, and a plain block would
stop at its last line and let the quote hang into the band under it.
`flow-root` clips nothing, so the quote still stands outside the column. A
figure or a table marked for the rail is a whole section, so the section's
children take rail width and a start margin of the column plus the gap.

Below 1000px none of that applies and each of the three comes back into the
column at the place the author wrote it: a sidenote becomes the footnote at the
foot of its section, a pull quote sits in the paragraph run, and a marked figure
takes the full width. Nothing changes on a phone.

## Controls, states and hit targets

One control component: `.button` and `.control` share centered content,
`--radius-control` 6px, a `--rule-strong` border, sans at `--t-1`, and
`--tap` 44px of minimum height. Cards and panels use `--radius-card` 8px.
Those are the only two radii.

Three links set at the size of their own type: the brand in the header, the
template link in the notice, and the "Back to the text" link at the foot of a
note. A `::before` behind each one used to carry the hit area. It works for a
pointer, and it fails every measurement, because the box the link reports is
still the box of its own type: the review wave measured 35 × 22, 117 × 20 and
104 × 20 against the 24 × 24 of WCAG 2.2 success criterion 2.5.8. Each one is an
inline flex box now, `--tap` tall, with the type centred in it. The target is
44px at every width and it measures 44px.

Hover has two patterns and no third. Text links move `text-decoration-color`
from `--rule-strong` to `--accent` over `--dur-hover` 140ms. Blocks, meaning
buttons, contents rows and the contents summary, fill with `--wash`; buttons
add a 1px lift over `--dur-control` 160ms and contents rows add a `--rule-mark`
accent inset rule.

Two rule weights carry a state rather than an edge. `--rule-mark` 2px is the
marker that says "this one": the accent rule under the open tab, the accent
rule at the leading edge of the contents row the reader is in, and the same
rule on the theme preset the guide is showing. `--rule-error` 2px is the
heavier ink edge a field in error takes, and the edge of the summary that
lists the errors. Both are a weight and not a color, so a reader who cannot
separate the hues still reads the state.

Focus is one rule everywhere: `--focus-width` 2px solid `--focus` at
`--focus-offset` 3px. The ring follows each element's own radius, so it never
cuts a corner or overlaps a neighboring row.

Every section heading is a link to its own section, so a reader can take the
address of the part they are reading. The link wraps the title rather than
sitting beside it as a glyph: a permalink beside the title contributes its own
name to the heading's, and every heading would then be announced with four
words that are not the heading. It carries no decoration at rest, so a heading
still reads as a heading, and the underline arrives on hover in the accent the
way it does on every other text link. The same `::before` hit box sits behind
it, so a one line heading is a full `--tap` target without a 44px line box.

The footer controls are Copy link, Cite and Print / save PDF. Every one is
hidden in the markup and shown by its script, so a reader with no script is
never offered a button that cannot act. Copy link writes the canonical URL plus
the current section fragment. Where the clipboard API is not available, which
includes a page opened from disk, a selection copy takes over. Cite opens a
native `<dialog>`: the browser holds focus inside it, Escape closes it and focus
returns to the control that opened it; a click outside closes it as well.

The toast is one `popover="manual"` element with `role="status"`, `--t0` sans on
ink. It is anchored to the footer's own control group, not to the footer:
`.footer-controls` carries `anchor-name: --controls`, and the message puts its
end edge on the group's end edge and its bottom on the group's top, so it lands
over the button that opened it. The footer is a full band, and anchoring to that
band put the message over the methods tint, well above and to the left of the
button. Where anchor positioning is not available, `50-share.js` measures how
much of the same control group is on the screen and the stylesheet lifts the
message by that, from the same end edge.
It enters in `--dur-enter` with a `--rise-enter` rise and holds for
`--dur-toast` 2400ms. `50-share.js` reads that hold out of the stylesheet with
`kit.ms()`, so the wait and the transition cannot drift apart.

## Motion

Two curves. `--ease` `cubic-bezier(.32,.72,0,1)` carries every arrival and
reflow. `--ease-draw` `cubic-bezier(.33,1,.68,1)` carries anything that draws
or erases a stroke. Durations are `--dur-hover` 140ms for pointer feedback,
`--dur-control` 160ms for buttons, `--dur-panel` 180ms for the contents panel.
Five more carry the components: `--dur-instant` 90ms for a pressed state,
`--dur-reveal` 220ms for anything that opens in place, `--dur-enter` 320ms for
anything that arrives over the page, and `--dur-count` 720ms for a numeral that
counts up. A staggered list steps by `--stagger-step` 16ms and stops at
`--stagger-cap` 180ms, so a list of twenty finishes when a list of ten does.
Two more state a distance and a wait rather than a curve: `--rise-enter` 6px is
how far anything that arrives over the page travels, and `--dur-toast` 2400ms
is how long the toast holds before it goes.

Reduced motion and the paused state run the same code path: transitions and
animations drop to `.01ms` with no delay instead of being removed, so every end
state is still correct and nothing has to branch. The media query is gated on
`:root:not(.motion-on)`, which report.js sets when the reader turns motion back
on with the header control. Without that gate the control would flip its own
label and change nothing, which is worse than not offering it.

The stage has its own durations, and they are tokens like everything else:
`--dur-travel` 620ms for a mark moving between layouts, `--dur-draw` 240ms for
one stroke or one line being drawn, `--dur-erase` 140ms for lines clearing out,
`--dur-color` 340ms for a mark taking or releasing the accent, `--dur-ring`
380ms for the orbit ring and its label, `--dur-progress` 300ms for the progress
rule and `--dur-caption` 320ms for the caption. `--draw-start` 434ms is when a
new line starts drawing, about seventy percent of the way through the travel,
so the lines arrive with the marks rather than after them. Per-element timing
rides on custom properties build.py or report.js writes: `--md` is a mark's own
travel delay, `--d` a line's draw delay, `--ring-delay` holds the ring back
until the lines finish. The stagger those last two come from is stated once, in
tokens: `--line-delay-first` 14ms and `--line-delay-last` 110ms across the lines
of one state, `--intro-mark-step` 30ms and `--intro-stroke-step` 12ms across the
marks and the strokes of the cover intro. report.js reads all of them, and every
duration it waits on, out of the stylesheet at startup, so a timing cannot be
changed in one file and left behind in the other.

The intro draws each stroke with a dash of one length. Strokes are not the same
length, so every stroke carries `pathLength` from build.py: the dash is then the
stroke, whatever its own arc length is, and nothing is left drawn short. The
delay is one rule over `--i`, the mark's index, and `--j`, the stroke's index in
its mark, both written into the markup, so a mark of any stroke count staggers
without a rule of its own.

Only `transform`, `opacity`, `stroke-dashoffset` and `stroke` ever animate. The
progress rule changes width with `scaleX`, not `width`, so no transition on the
page can force a layout.

The narrative and media components animate one thing. The lightbox dialog
arrives in `--dur-enter` with opacity and a `--rise-enter` rise, the same rise
the toast takes. The comparison divider
follows the pointer with no transition at all, on purpose. Nothing else in that
group moves: a timeline, a picture, a gallery and a diagram are all correct
with no animation of any kind.

Bars grow from zero and lines are drawn through a window that opens from the
left. Both are one transform, so the four properties this page animates stay
four. A dash offset cannot draw a line that also carries a non-scaling stroke,
because the dash is then measured in screen units and the path length is not,
which is why the line uses a clip rectangle instead.

The reveal runs once. With scripts, one IntersectionObserver adds a class on
first view and a second class when the reveal is over, and nothing starts it
again. With scripts off, `animation-timeline: view()` inside `@supports` drives
the same reveal from the reader's own scroll position, because there is no
timer to start it. A scroll timeline runs backwards when the reader scrolls
back up, so it is the fallback rather than the first choice. A scroll timeline
also reads a position rather than a clock, so shortening every duration does
not stop it: the reduced-motion gate turns the animation off outright, and the
end state is the base state.

A findings numeral counts up once, on first view, in `--dur-count`, on a cubic
ease out that matches `--ease-draw`, and lands on the exact value the build
wrote. It keeps a prefix and a suffix, so "330+" counts to 330 and keeps the
plus, and a value that holds no number does not move. The markup already holds
the value, so a reader with no script, with motion paused, or with reduced
motion set reads the number and nothing moves.

The scrolly's blend is the one motion that is not timed at all. The scroll
position is the clock: report.js writes the same four properties straight from
the reader's place, eased per segment on `--ease`, which it reads out of the
stylesheet and solves in script, so the stage settles on the same curve as
every other arrival and no third curve enters the system. A scrubbed stage
drops every timed transition inside it, because a transform that still eases
after the finger has moved reads as lag, not as polish. The mark keeps only
its stroke transition: the accent landing at the segment's midpoint is a state
change, not a travel. Pausing motion, or asking for reduced motion, takes the
stage off the blend and back onto one settled state per card.

## The scrolly

The stage is `position: sticky; top: 0; height: 100svh` with `padding-top` of
`--header` plus 4px, so the pinned frame clears the header. `--stage-h-safe` is
the viewport minus the header, written by report.js at load and on a width
change; the drawing's width is capped by it, so the art always fits the frame.

The steps column is led in by one stage height and pulled back by half a step
(`padding-top: 100svh; margin-top: -56svh`), each slot is `112svh` with its card
centered, and an `80svh` tail follows the last one. One passive scroll listener,
throttled with `requestAnimationFrame`, reads the place of every card against a
trigger line at 0.88 of the viewport height; one `IntersectionObserver` at
`rootMargin: "25% 0px"` decides whether that listener does any work. Resize
recomputes on a width change only, so a mobile browser hiding its own chrome
cannot fire a state change.

With motion on, the scroll position is the state. The scene's place is measured
in states: 0 is the first card, one less than the count is the last, and every
card after the first earns its share across three fifths of a viewport of
scroll after its top crosses the trigger line, so the drawing arrives as the
card reaches the middle of the screen. Between two cards the marks travel the
straight line between their places in the two layouts, the lines of the leaving
state fade out over the first half of the segment and the lines of the arriving
state fade in over the second, and the ring and its label follow the same
share. The caption and the accent belong to whichever state is nearer, and the
progress rule fills with the place itself instead of stepping from card to
card. The layout plans are computed once per state and cached against the
stage, so a scroll frame writes transforms and two opacities and nothing else.

With motion paused or reduced, the same reading runs the discrete path: the
last card whose top has passed the trigger line fires one settled state, and
the no-motion gate shortens every transition to nothing. The pause control
settles the stage at once, on the click, rather than waiting for the next
scroll frame.

The drawing warms as the argument builds. The scatter stays ink, because
nothing is shared yet; the groups take `--secondary`, the network takes
`--series-3`, and the orbit arrives in `--accent`, connection lines included,
so a reader who never reads a card can still place the story by its hue.
Every state color is a series token, so the four states read as one palette
in every theme, and each one clears 5.5:1 on paper. The highlight keeps the
accent in every state, so a convener still stands out inside its green group.
The hue crosses on the stroke transition in both modes, because a state's
color is a state change, not a travel. The progress rule fills in the accent
for the same reason: the contrast suite holds the accent on the wash at 4.5:1
or better in every preset.

Each step card carries the caption of the state it fires, as visually hidden
text. That copy is the only description of the drawing in the document: the
stage's own `figcaption` is the sighted duplicate and is hidden from assistive
technology, so hiding this one too would leave a screen reader with no idea what
the drawing shows. It is hidden from the eye rather than from the page, in
reading order, inside the card it belongs to.

With scripting off there is no state to show and nothing to pin, so the scrolly
is not a staged column at all: the card's caption is shown, `.scrolly` stops
being a grid, the drawing sits
once at `--figure` under the same `--cover-art` cap the cover uses, and the
steps run down the `--reading` column in the order they are written. The lead-in,
the slots, the tail, the progress rule and the stage caption all go. A card
keeps no chrome but a hairline above it, because nothing here can become
active.

## The contents panel

The panel is a native `<details>`, so it opens with scripting off. `initContents`
in `report.js` adds four things and nothing else: it marks the reader's current
section with `aria-current` when the panel opens, closes on a click outside or
on the scrim, closes on Escape and returns focus to the summary, and moves
focus to the landing section after a jump. A click on the scrim reports the
`<details>` itself as the event target, which is how the handler tells a scrim
click from a click on the panel. Quote sections carry no title and are left out
of the contents.

## The header's own links

A report may name up to three links of its own in `header_links`. They render
as plain links in the label face, before the motion control and the contents
control, so Tab reaches them on the way to the panel and no button competes with
the report's own title. The url is an absolute address or a plain relative path,
because the guide and the examples index sit beside a hosted sample and inside a
folder in the download; a scheme other than HTTP(S), a host, or a query string
stops the build.

Below 560px a report's header holds the brand, the motion control and the
contents control and nothing more, so the links move into the contents panel and
take the row a section link takes, under a heavier rule. One copy is on the page
at any width, so Tab never stops on the same link twice. The guide and the
examples index carry no panel and no controls, so their links stay in the header
at every width; the `with-contents` class on a report's header is what separates
the two cases.

Above 560px the links are back in the header, and the header gives up what it
can state another way to make room for them. Below 1000px the section title
goes and the motion control is its icon; below 760px the organisation name goes
as well. Three links with all three of those parts beside them want about 878px
of header, so the page scrolled sideways from 561px to about 624px before this;
without them the same three links want about 544px at 561px. The order is by
what else says the same thing: the panel marks the section with `aria-current`,
the button keeps its `aria-label` and its play and pause marks, and the brand
mark still names the report.

Nothing in the header wraps. The links and the two controls hold their own
width, because there is no shorter form of a link than its own words; the
section title gives up its width first, with a shrink factor of 999, and the
organisation name second, and both cut off with an ellipsis rather than run to
a second line. A header that shrank its parts instead stood "Sample report" and
"Resume motion" on two lines each and the organisation name on three.

## Navigation

A `--progress-h` rule on the header's bottom edge reports the reader's place in
`<main>`.
It scales with `scaleX` and never sets `width`, so it never asks the page to lay
out again. It carries `role="progressbar"` with `aria-valuenow` in whole
percent. It never transitions, so it follows the scroll the same way under
reduced motion as it does with motion on. With no script it is hidden, because a
rule that can only report zero is worse than no rule.

The header names the section the reader is in, in `--t-1` sans, and swaps the
name at once. The contents panel marks the same section with `aria-current`,
full ink where the other rows step back, and an accent rule at the row's leading
edge. One reading of the page decides all three, and Copy link appends the same
section to the address it writes. Below 1000px the header title hides and only
the panel marks. The header copy is `aria-hidden`: the panel states the same
thing, and a text swap on every section would interrupt a reader.

## Sections

The summary is the lead of the report. It opens and closes on a hairline, the
way the findings do, and it sets one step above the body at `--t2` with
`--lh-subhead`. It takes no tint, because the takeaways are the tinted block
and two tinted blocks at the top of one report read as one. The build caps it
at 100 words, which is the length that fits inside the first screen, and the
section names itself with `aria-labelledby`, so a reader who moves by landmark
can jump to it.

The takeaways are a list on `--reading`, on `--wash`, opened by a `--rule`
hairline and closed by nothing. No border on the other three sides, no radius
and no shadow: a card here would compete with the findings grid, which is the
one block on the page that carries a numeral. The list marker is the accent.
Two items is the floor and five is the ceiling: under two is a sentence, and
over five is the report again. On paper the tint goes and a second hairline
closes the block.

The findings grid is `--figure` wide and takes its column count from the item
count: one item fills the row, two or four sit as a pair, and everything else
runs three across. A numeral is one line of `--font-numeral` at `--t4` with
`--lh-numeral`, so a row of statistics shares one baseline. The optional `unit`
sits under the numeral and the optional `note` under the text, both sans at
`--t-1` in `--muted`. Neither is emitted when the author leaves it out.

A findings item may carry a `trend` of 3 to 24 numbers. It draws one path in
`--line` with an end dot in the accent, no axis and no frame, beside the
numeral, with a hidden sentence that states the first value, the last value and
the count of points.

A figure is two layers. The marks are one SVG with a viewBox of 100 by 100 and
`preserveAspectRatio: none`, so an x is a percent of the plot width and a y a
percent of its height, and the stylesheet alone decides how tall a row is. The
labels are HTML beside that SVG, so they hold the token type size at every
screen width. A scaled SVG shrinks its own text to four pixels on a phone,
which is the reason the labels are not inside it. Every stroke carries
`vector-effect: non-scaling-stroke`, so the sideways stretch never changes a
line weight.

Six kinds ship: `bar`, `dot`, `line`, `slope`, `range` and `stacked`. A bar and
a stacked bar open at zero, because length is what carries the value there, and
a value under zero stops the build and names the row. A dot, a line, a slope
and a range take a scale that opens one eighth of the span below the smallest
value and closes the same distance above the largest, so a mark never sits on
the frame. Bars order themselves by value, largest first, unless the author
sets `sort` to false, which is what a calendar needs. Gridlines belong to the
line chart alone, at most four of them, in `--rule`: every other kind labels
its own marks, and a chart that labels its marks needs no ruling behind them.

Every mark carries its value. A value sits outside a bar until the bar passes
72 percent of the plot, then it moves inside the bar end in paper. A stacked
segment holds its value at 14 percent of the row and its series name at 22
percent; a narrower segment gives both to the data table. With `percent` on a
stacked chart the width of a segment is its share of the row, so the label on
that segment is the share as well: a row of 30 and 10 draws two marks of 75 and
25, and a 30 printed on the first of them would name a number the picture does
not draw. The data table then holds two columns for each segment, the value the
author gave and the share the mark holds, so nothing is lost.

A dot chart steps the dots of one row apart by series, across half the row
height, and puts each label beside its own dot. Two series that hold the same
value would otherwise draw one mark over the other, and the reader would count
one where there are two. A series is named
once, at its widest mark or at its line end, and never in a legend, because a
legend sends the eye back and forth between a key and a mark. Values are set in
`--font-numeral` with tabular figures at `--t-1` and category names in sans at
the same size.

Four series is the cap for the marks that share one chart, which is what a
reader tells apart without color. A fifth stops the build and names
`"multiples": true` as the fix, which draws one small chart for each series on
the one scale the whole figure shares. Small multiples are outside the cap, or
the fix the error names could not build. Every panel draws in `--series-1`: a
panel holds one series and its own heading names that series, so a second color
has nothing left to tell the reader apart. Each panel writes its own
definitions, so two panels never share the id of a pattern or of a drawing
window.

The picture sits on `--figure` and the caption on `--reading`. The whole
picture is hidden from assistive technology, the marks and the labels around
them together: the labels are HTML, and hiding the SVG alone left them in the
accessibility tree as a stream of words with no shape. The `<figure>` takes its
name from the section title through `aria-labelledby` to `{sid}--title`, the id
`page.py` gives every section heading through
`text.heading(label, title, section_id, heading_id)`. A figure and a table
point at that id and write none of their own. The caption states the trend in
one sentence, and a `<details>` under the figure, whose summary reads "Show the
data", holds a real table of every value. That table is also the keyboard path
into the data: a focus stop inside a hidden SVG would have no name to announce,
so the marks are not focusable and only the pointer lifts one to
`--mark-hover`.

A table section is a real table first. The head names the columns, the first
text column names its own rows, numerals are right aligned in `--font-numeral`
with tabular figures, and a numeric cell carries its own number in
`data-value`, so a sort reads the number and not the text that formats it. A
sort control is a `<button>` inside the head cell; `aria-sort` states the order
of the column it sits on, the rows re-order in place, focus stays on the button
the reader pressed, and a hidden `role="status"` sentence states the new order.
The mark beside the name stands at rest on every column that sorts, in `--muted`
at 55 percent, and it takes full ink at full opacity on the column that is
sorted. It was hidden until a column carried `aria-sort` and shown on hover, so
every head read as a plain bold label and a reader on a touch screen, which has
no hover, never learned that the table sorts.
Above 760px the head sticks under the page header. Below it the wrapper becomes
the scroll box, so the head holds its place there and the wrapper carries the
sideways scroll with `--shadow-card` as the hint that more is to the side. The
wrapper is a named focus stop, because a reader with a keyboard alone has to
reach that scroll.

The quote sits on the reading column, left aligned, opened by `--quote-rule` in
the accent. Its attribution is a paragraph with a `<cite>` in it, not a
`<footer>`: a blockquote is not sectioning content, so a footer inside one maps
to a second contentinfo landmark and the page reports two. That rule is a border and not a background, so it survives a
printer with background graphics turned off. The column is its only cap: at
`--t3` it holds under 40 characters a line, which is already display measure,
and `text-wrap: balance` evens the lines out.

The tabs section is the ARIA tabs pattern with automatic activation. The
container is `role="tablist"`, each control is `role="tab"` with
`aria-selected`, and each panel is `role="tabpanel"` named by its tab. Left and
Right move between tabs and wrap at the ends, Home and End jump to the ends, and
a tab shows its panel as soon as it takes focus. The selected tab is the group's
one stop in the page tab order and Tab from it lands in the panel. Tabs are text
with an accent underline on the selected one: no pill, no card. The panel
changes in `--dur-reveal` with opacity alone, through `@starting-style`, so no
text moves.

The accordion is a native `<details>`. When `exclusive` is true every item
shares the section id as its `name` and the browser closes the open one. The
summary is `--tap` tall and carries a drawn chevron that rotates in
`--dur-hover`. Where the browser supports `interpolate-size: allow-keywords` the
panel opens over `--dur-reveal`; where it does not, the panel opens at once,
which is what a `<details>` does today. This is the one place the kit animates a
size, and the `@supports` gate keeps it an enhancement.

A prose paragraph can also be one of five blocks. A subhead is an `h3` with
`--s7` above it. A list is a `ul` or an `ol` with quiet markers, and an ordered
list counts in `--font-numeral` in the accent, like the citation list. A
callout is an `aside` on `--wash` opened by a `--rule` hairline, and a caveat
is the same block with a 2px `--rule-strong` rule and the word "Caveat" as its
title. The caveat takes no color of its own, because a warning color is a sixth
color the theme does not hold, and it states its name because a limit a reader
has to notice cannot depend on a border to say what it is. A pull quote reuses
the quote section's `--quote-rule` and its `--t3` size inside the reading
column. The author writes the sentence a reader sees, and the build reads it
back against the paragraphs of the same section with the markup of each one
reduced to the same thing: a link becomes its text, a term becomes the term,
and a note reference goes. A sentence that holds a link can then be lifted, and
it prints as a sentence rather than as markup. The block carries `aria-hidden`,
because the sentence is already in the text above it.

The steps are the light sibling of the scrolly: the numeral comes from the
list's own counter in `--font-numeral` at `--t2` in the accent, the title sets
at `--t1` sans beside it, and the text runs under the title on `--reading`. One
`--rule` hairline sits between two steps, and there is no card, no icon and no
line down the column. The count carries no leading zero.

The glossary is a definition list, sorted at build time so an author adds a
term at the end of the file and the page still reads A to Z. Each entry opens
with a hairline, the term sets at `--t1` sans and takes `tabindex="-1"`, so a
jump to it moves the reader's focus as well as the page and lands under the
sticky header through the scroll padding the page already carries. The anchor
of a term counts the sorted terms of its section, `terms--term-1` and the one
after it, rather than spelling the term: a term in any writing system then has
an anchor, and two terms that differ only in an accent have two. Every mention
of a term reads its anchor off the list the entry reads, so the mention and the
entry always write one name.

Sources are a citation list. `counter-reset` numbers them 1, 2, 3 in sans
tabular figures in the accent, with no leading zero, because the list can never
pass nine and needs no sort order. Each row opens with a `--rule` hairline,
the label is the link and is `--tap` tall, and `build.py` writes the host of
the URL under it so a reader can see where a citation points before following
it. The band redefines `--muted` against `--wash`, so that host still holds
4.5:1.

The methods band is the one section with two columns: the note on `--reading`
and the citation list beside it, both inside `--figure`. One column of prose
centered in a full bleed tint leaves a third of the band empty on each side.
Below 1000px the two columns become one.

The band takes two more fields. `brief` is the "How we did this" lead: a label
in sans at `--t-1` over one sentence at `--t2`, at the top of the band above
the note, under 80 words, and 13pt on paper. It answers "can I trust this?" for
a reader who will not read the whole note. `downloads` is a top-level field, so
`endmatter.py` holds it and the band places it under the citations, in the same
column. `page.py` counts the methods bands once, before the first section
renders, and hands the list to the band on the context, so a report with
downloads holds exactly one band: with none the files would print nowhere and
with two they would print twice, and each of those stops the build with a
sentence that says where downloads render. Each download link states the format
and the size inside the link, so a screen reader hears them in the link's own
name. The band's grid keys on `data-aside`, which counts the citations and the
downloads together, and it goes to one column when they add up to fewer than
two.

The kit's own pages offer placeholder files, and they are files:
`examples/downloads.py` writes each one and `package.py` runs it with the other
example builders. Each CSV is the table of the page that offers it, read out of
the same JSON the page is built from, so a change to a table moves the file
with it; each PDF is one sheet that says what it stands for. Every one opens on
the sentence the pages carry in their notice, that the values are invented. The
addresses were written before the files were, so the sample and two examples
offered seven links and every one of them was a 404. The size a report
advertises is the size of the file, rounded up to the next whole KB, and the
suite holds it there.

A timeline is a list, not a drawing. Dates sit in one column in
`--font-numeral` with tabular figures, so the eye scans the column of dates on
its own; the event title is sans at `--t1` and its text is on `--reading`. One
hairline opens each event. There is no dot, no connector line and no
alternating side: a chronology that zigzags makes the reader work for an order
the dates already state. The two columns are a subgrid, so one hairline runs
the width of a row and every date shares one edge. Below 760px the date moves
above the event it belongs to. A date is text and prints as the author wrote
it, because a chronology that spans "1998" and "12 May 2025" has no one date
format that holds every entry.

A picture sits on `--reading`, `--figure` or `--bleed`, and on nothing between.
`src` takes an absolute HTTP(S) URL, a `data:image/svg+xml` URI, or a relative
path with forward slashes and no `..` in it. A relative path with a backslash
in it is a file name from another operating system, and it also walks past the
`..` check, which reads forward slashes only, so it stops the build first.
Its caption and its credit are sans at `--t-1` in `--muted` under it, and the
credit is last, because the reader wants the picture explained before they are
told who made it. Every picture is lazy and asynchronous: a report is a long
page and a picture halfway down it must not hold the first screen back. On
paper a reading picture keeps `--reading-print`, a figure picture fills the
text block the way the findings row does, and a bleed picture comes back to the
page margin, because paper has no bleed to reach.

The lightbox is a native `<dialog>`, so the browser holds focus inside it,
closes it on Escape and paints its own backdrop. The kit adds four things: the
trigger, the click outside, the close button and the focus return. The trigger
is the picture. With scripting off it is a link to the picture's own file; the
script makes it a button, because a link goes somewhere and a button acts. A
picture drawn into a data URI has no file to link to, so its markup carries no
link and the script gives that one a button of its own. The dialog is the one
thing in this family that moves: it arrives in `--dur-enter` with opacity and a
6px rise, through `@starting-style` and `transition-behavior: allow-discrete`,
and under reduced motion it is simply there.

A comparison renders side by side. That is the base state, the print state and
the state a reader with no scripting sees, and each picture keeps its own label
above it, because one label under both makes the reader work out which one it
names. With scripting the two stack, the second is clipped at the divider, and
an `<input type="range">` moves it. The range carries a visible label, steps by
2 percent so an arrow key moves 2 percent, starts at 50 and states its own
value in `aria-valuetext`. Dragging the divider works as well and never alone:
the range is the single-pointer path WCAG 2.5.7 asks a drag to be offered
beside. The split is a live custom property with no transition on it, because a
divider that eases is a divider that lags behind the pointer. The two pictures
have to be the same size and the same crop, or the overlay compares two frames
instead of one.

A gallery is a filmstrip with `scroll-snap`, and it never moves on its own.
There is no timer in it, so there is no pause control to need. The last item
stops short of the edge, so the reader can see that the strip holds more than
one picture. The two buttons are `--tap` tall and each one is disabled when the
strip has run out of room in its direction; the bar goes away when every
picture already fits. A count reads "3 of 8" in a `role="status"` beside them,
and it is written only when it changes, because writing the same line again
says it again. Every picture carries its own caption: one caption for a set
tells the reader nothing about the picture in front of them. With scripting off
the buttons and the count never appear and the strip scrolls by hand. On paper
it is a grid of two.

A diagram is a static drawing of how a few parts connect, in the cover's own
marks and the cover's own bowed lines, and nothing in it animates or can be
triggered. The frame is the figure column, 1092 units for 1092 pixels, so a
label set at 16 units is a label set at 16 pixels; the drawing holds that size
whatever the window does and its own frame scrolls when the column is narrower,
because a label that scales with the page stops being readable on a phone.
Below 760px the rule turns around: a phone frame is under a third of the
drawing, so a reader met the middle of the picture and had to scroll sideways to
find the node the flow starts from. The drawing gives up its minimum width at
that size and takes the room it is given. Its labels are small there, and the
ordered edge list under it, which is the drawing in sentences and is never
hidden, is what a reader on a phone reads.
Three layouts: `row`, `column` and `ring`, where the ring is an ellipse rather
than a circle so the wide frame is not two thirds empty. Every node keeps a box
of its own, its mark and its label together, and the layouts are built so that
no two of those boxes touch at any node count from two to eight. A line stops
short of the two marks it joins, so the column pitch holds both of those gaps
and 40 units of line between them; where a layout still puts two marks closer
than that, as a row of eight does, the line gives up a third of its span at
each end instead of the full gap, and it is always a line that points from one
mark to the other. A label is bound at .72em a character, the wide end of the
sans stack, so a label of wide glyphs cannot run over its neighbour and a label
of narrow glyphs simply wraps sooner than it has to. A label that cannot fit
the room its layout leaves stops the build and states the room it has, and one
word wider than its own node is reported on its own, with the node and the
room it had. The SVG is hidden from assistive technology, because a bare SVG tells a
screen reader nothing; under it an ordered list states every edge as one
sentence, and that list is shown rather than hidden. Every node has to carry at
least one edge, so the list names every node in the drawing.

A part is a chapter opener and it is the only place besides the cover title and
the findings numerals where `--t4` appears. The number is a numeral in
`--font-numeral` and it counts 1, 2, 3 with no padding zero. The title is
`--t3` and the deck sits on `--reading` under it. The block takes `--bookend`
above and below and sits on `--pad-wrapper`, the same left edge the cover, the
notice and the footer take, so a chapter opener reads as a full width pause
rather than as one more section. It is in the contents as its title, and on
paper it starts a new sheet, which is the whole job of the component.

The footer is a colophon: organization, series and date on the left, the
canonical URL and the two controls on the right, both on `--wrapper`.

## Notes

`kit/notes.py` renders the notes of every section type, through a hook in
`page.py` that runs after the section body. One note is written twice.

Above 1000px, and only in a section wide enough to hold the column, the note is
a sidenote in a column beside the reading column: the rail in the wide layout,
which is 330px, and the space between the reading column and `--figure` in the
reading layout, which is 182px at 1440 and too narrow to use below about
1200px. One width opens both, so a note goes to the side or to the foot at the
same place in either layout. It sets at `--t0` in the label face in `--muted`
with its number in the accent. `scripts/50-notes.js` measures the column with the stylesheet's own
arithmetic, puts each note level with the top of its own reference, and moves a
note down when it would land on the note above it. The height of the stack that
comes out of that is part of the same decision: four long notes beside three
lines of text end below the section they belong to, and a section whose stack
ends below it takes the footnotes back rather than laying its notes over the
section under it. Everywhere else, and on paper, and with scripts off, the same
note is a footnote at the end of the section with a link back to the reference.
The reference is itself a link, so following the back link moves the reader's
focus as well as the page.

One note carries one id. Two elements with one id is not a page, so the markup
gives `{sid}--note-{n}` to the footnote, which is the copy that a phone, a
printer and a page with scripts off all show, and the script hands that id to
the sidenote while the sidenote is the copy on the page. The copy that is not
on the page is hidden with `display` rather than with `aria-hidden`, because a
note can hold a link and `aria-hidden` would leave that link in the tab order.

A note with no reference on the page stops the build: a note nothing reaches is
a back link that points at nothing. The build reads the record the renderer
keeps of the references it emitted, and not the source of the section, because
a title is plain text and a `[^1]` inside link syntax is a link. Neither of
those two writes a reference, and a note that rests on one would sit under the
section with nothing to point at it.

## The definition control

A `{term}` in any text renders a `<button>` with `popovertarget`, a link to the
glossary entry beside it, and nothing else. The glossary section holds one
popover for each of its terms, so a term used ten times adds ten buttons and no
extra text.

The button states no `aria-expanded` of its own. A button with `popovertarget`
already reports the state of its popover, and a written attribute would be
wrong the first time a reader opened it. The browser opens the popover on
click, on tap, on Enter and on Space, closes it on Escape without moving the
reader's focus, and closes it on a click outside.

`scripts/50-definition.js` adds the two things the platform does not give. A
pointer that rests on a term for `--dur-intent` opens the definition; the
popover holds while the pointer is on it and closes when the pointer leaves
both, which is what WCAG 1.4.13 asks of content that appears on hover. A
definition the reader opened stays open until they dismiss it.

The file asks for the popover API before it binds anything, the way
`50-share.js` asks for it: a browser with no `showPopover` takes the
`no-popover` class, which keeps the plain link on the page and hides the button
that cannot work. The `enhanced` class cannot answer that question, because it
speaks for the whole page and one control is missing here.

The popover is placed by anchor positioning inside `@supports`, under the term,
flipping above it when there is no room. A popover opened by a click takes the
button as its implicit anchor; one opened by the pointer has no invoker to
take, so the script names the button the reader is on and points the popover at
that name. On a phone the box stops centring itself on the term and centres in
the window, because a box centred on a term needs space on both sides of it.
Where anchor positioning is not supported the script places the popover and
follows it on scroll.

The build caps a definition at 40 words, so the popover never needs a
scrollbar. A definition carries no note reference, because the same definition
is rendered twice, in the entry and in the popover, and one reference would
then write one id on the page twice. With scripts off the button is hidden and
the term is a plain link to the glossary entry. On paper the same link prints,
without its underline.

The term carries no `::before` hit box. An inline target inside a sentence is
the one target WCAG 2.5.8 excepts, and a 44px box around a word in body copy
covers the lines above and below it and takes their clicks.

## Text fields

Every text field of every section reads one inline markup, and nothing else:

- `[text](https://example.org)` is a link. The URL is absolute HTTP(S), the way
  every other URL in the kit is, and the link carries `rel="noopener"`.
- `[^3]` is a reference to note 3 of the same section. It renders a superscript
  link to the note, with an `id` the note links back to and an
  `aria-describedby` that names the note. A reference to a note the section does
  not carry stops the build.
- `{term}` is a glossary term. The renderer the caller passes in decides what a
  term becomes, so the parser holds no glossary of its own. A term with no
  glossary, and a term the glossary does not hold, both stop the build.

Every other character is escaped the way `esc()` escapes it. The parser lives in
`kit/inline.py` and every renderer calls it, so an author reaches the markup
through these three forms and through nothing else.

A title is the exception. A title names its section in the heading and in the
contents, and a link inside a contents entry is a link inside a link, so a
title, a label, a step caption, a findings value and a findings unit stay plain
escaped text. The step caption is doubly so: it also rides in a `data-caption`
attribute, where markup cannot go.

## The language of the report

`lang` is an optional top-level field and it is written on `<html>`. It is a
lowercase tag from one subset of BCP 47: a language of two or three letters,
then an optional script of four letters, then an optional region of two letters
or three digits, then any number of variants; or a private use tag, `x` and one
or more subtags. `en`, `es-419`, `pt-br`, `zh-hant-tw` and `x-local` are in the
subset. Extensions and grandfathered tags are not, because a report has no use
for them and a pattern loose enough to hold them also holds an incomplete tag
such as `en-a`. The default is `en`.

## End matter

`kit/endmatter.py` holds every block that comes after the last section, and the
cover byline as well, because the byline states the authors and the authors are
end matter. `page.py` calls `byline(data)` for the cover and `render(data)` for
the blocks, in that one place between the last section and the footer, so the
shape of `authors` changes in one file.

The build counts the words in every text field of every section, skips the
fields that name a structure or an address, divides by 200 and rounds up. The
cover states the result beside the date.

`kit/cite.py` builds the three citation forms the footer's Cite dialog shows,
and the print block puts the plain one under the colophon. Names stay as the
report writes them: the kit cannot tell which part of a name is the family name,
and an inverted name that guesses wrong is worse than a name printed the way its
owner writes it. BibTeX escapes every character LaTeX reads as syntax and drops
nothing, so a title that holds one keeps it. A date with no four-digit year gets
no `year` field rather than a guessed one.

The blocks run in one fixed order: the authors, the credits, "Read next", the
series links, the form and the corrections. Each one reads one top-level field
and renders nothing when the report does not carry it. The series links read
`series_links`, and not `series`: `series` is the line the cover and the footer
already carry, and one name cannot hold both.

Every block is quiet. It opens with a `--rule` hairline that goes edge to edge,
carries a label in sans at `--t-1` in `--muted`, and takes no card, no tint and
no icon. One wrapper inside the section states the role width, `--reading` for
five of the blocks and `--figure` for "Read next", and that wrapper carries the
body type size: the measure is stated in em, so a width on the small label
itself would come out of the label's own size and would be a third short.

An author row is the name in sans at `--t1`, then the role, the bio and the
link at `--t0` in `--ink-soft`. The link states the host it points at, the way
a citation does. There are no photographs. Every field an author supplies is
read and checked before the block decides whether the author says more than a
name, so a broken bio stops the build even when no block would print it.

The credits are a definition list. The role is the term and the name is the
value, because a reader looks for the work before the person who did it. The
two columns share a baseline.

"Read next" is a row of one to three reports on `--figure`. One report holds
the reading measure, two sit as a pair, and three run three across. Each title
is a `--tap` tall link at `--t1` in sans, with one line under it in
`--ink-soft`. The row holds its count down to 760px, where every count becomes
one column. Two columns at 1000px wrapped a row of three two and one, with a
hole where the third column was; three columns of 275px carry the title in two
lines and the row still reads as a row. The phone rule names every count,
because `.read-next[data-count="2"]` holds one class more than `.read-next` and
would otherwise keep its two columns on a phone.

The series links are a `<nav>` of two text links that carry the real titles.
The previous link holds the left of the row and the next link holds the right,
so a lone next link still reads as the one that follows. The direction label
carries no underline and the title carries one: the rule that does that holds
two classes, because `.endmatter a` would otherwise underline the label with
the title.

The corrections log is plain: a hairline, a date in sans tabular figures, and
one sentence. Nothing about it is styled to be read quickly, because a log that
is easy to skip is a log that gets skipped.

### The form

A form ships only when `form.endpoint` is set, and the endpoint is an absolute
HTTPS URL. A `mailto:` endpoint stops the build: a mail client cannot check a
field, cannot confirm a send, and puts the reader's address on a public page.

What renders is a plain `<form method="post">` that posts on its own. Every
field has a label, an `autocomplete` token and its own error paragraph. The kit
knows the token for `email`, `full-name` and `organization`, and every other
field states its own. The field for a person's name is `full-name`, because
`name` is one of the names the form element keeps for itself: a field called
`action`, `method`, `submit`, `reset`, `elements`, `length`, `name`, `target`,
`enctype`, `encoding`, `acceptCharset`, `autocomplete` or `noValidate` hides
the property of the same name behind its own input, so the build stops such a
name. The trap name `website` stops the build as well. A spam trap sits between
the fields and the button, hidden from the eye, out of the tab order and out of
the accessibility tree.

`scripts/50-form.js` improves a form that already works. It checks a field when
the reader leaves it, and then on every keystroke once that field has shown an
error, so nothing interrupts a reader who is still typing the first time. A
reader on the way to the button gets no message on the way out of the field:
the message would grow the form between the press and the release, the button
would move, and the click would be lost. On submit the script checks every
field, writes an error summary at the top of the form, and moves focus to it;
the summary links to each field it names. Nothing reaches the network until
every field passes.

The form has two sends, and `inline` chooses between them. Without it the
script checks every field and then lets the native post run: the browser leaves
the page and the endpoint answers with its own page. With `inline: true` the
script posts with `fetch`, keeps the reader here, and puts one sentence in the
place of the form. The second send needs an endpoint that answers with CORS
headers, because the browser rejects an answer without them even when the
endpoint accepted the reply, and the page would then tell the reader the send
failed after it landed. The native post is the default, because it works with
every endpoint and it leaves no reader with a wrong answer.

The sentence that takes the place of the form names the first field the reader
filled, so the reader reads back what they gave. When every field is empty it
thanks the reader and names nothing. One field is always required, so the short
sentence is there for a filled spam trap alone, and a form where every field is
optional stops the build.

The error wording is in ink and opens with the word "Error". No error state
uses color alone, and none of them uses red. A field in error takes a
`--rule-error` ink edge and `aria-invalid`. The message opens in lower case because the field
shows it after "Error:"; the summary starts the same message at the head of a
line, so the stylesheet lifts its first letter.

The form is interactive, so it carries `screen-only` and paper does not show
it.

## Responsive

Two breakpoints, each with one job.

At 1000px the stage stops being a column and becomes a band: `--band` tall,
sticky under the header, full bleed across the section, with the drawing, the
caption and the progress rule inside it. Below 1000px a stage column and a
readable card cannot share a row. The steps column loses its lead-in and its
tail, each slot becomes one screen at `100svh`, and every card is pushed down
by the header plus `--band`, so it rests in the middle of what the band leaves
rather than in the middle of the slot. That is the difference between a card
the reader can read whole and a card cut in half by the band. The trigger does
not change: the active step is still the last card whose top has passed 0.88 of
the viewport.

At 760px the page itself stacks. The cover goes to one column with the copy
first, the findings grid goes to one column, the footer columns become one, and
the step card padding drops to `--s4`. A report's header drops the
organisation name here as well.

The 1000px fold does one more job in the header: the section title goes and the
motion control becomes its icon, which is what gives a report's own links their
room from 561px up.

At 420px the header of the guide and the examples index sheds the organization
name, and the contents panel runs full width between the gutters. A report's
header has already dropped that name at 760px, and the motion label at 1000px.

The step card never grows past `min(416px, 100%)` at any width. On the band
layout it centers instead of widening, so a card is one width everywhere and
the band above it always overhangs it.

Nothing scrolls sideways from 1440 down to 320, and nothing interactive is
shorter than `--tap`. Two boxes hold a scroll of their own: the table wrapper
below 760px and the diagram frame at every width. Each is its own scroll box
with the shared `.scroll-edge` hint on it, so the page under them does not
move.

## Print

Paper is white and ink is black. The print block redefines `--paper`, `--ink`
and `--wash`, and everything derived from them follows, so the report prints as
a document rather than as a picture of a screen. `--rule` is mixed harder for
paper, at 30 percent, because a 16 percent hairline does not survive a printer.
The block also states `color-scheme: light`. It is the one place in the
stylesheet that states a scheme, and it is stated because a dark theme carries
`dark` from its own theme block: the paper and the ink were reset for paper and
the scheme was not, so a night report printed with background graphics on came
out a black sheet with a white box inset in it.

What goes away: the grain, the skip link, the header controls, the progress
rule, the cover buttons and footnotes, the whole sticky stage, the back to top
link and the print button. Nothing new arrives; everything printed is already
in the document.

Each of those parts carries the `screen-only` class, and the print block hides
that one class. A component states what paper leaves out on its own markup, so
no selector list grows in the print stylesheet. The two exceptions are the grain
and the step column's tail, which are pseudo-elements and can hold no class.

The header keeps the brand and its hairline and hands the title to the cover
under it. The footer keeps the colophon and the canonical URL, which is what a
printed copy is passed around with.

The scrolly cannot scroll, so `report.js` builds one static copy of the stage
per step at load time, into the `.print-figure` container `build.py` emits, and
lays each one out with the same function the screen uses. The copies sit two by
two above the step texts and carry the captions, so the card's own caption is
hidden and no caption prints twice. Two by two rather than four across because
at a quarter of the text block a state is too small to read and the word inside
the orbit ring disappears. A copy cannot measure its own label, since
`getComputedTextLength` returns 0 inside a hidden container, so it takes the fit
the live stage worked out. Each copy renames its gradient
and its mask so several drawings can share a page without sharing an id, and
the print block turns off the line drawing animation, which never runs inside a
hidden container and would otherwise print as blank paper.

Print swaps the fills of a figure that carries two or more series for four
patterns: horizontal stripes, vertical stripes, a cross-hatch, and a checker.
Each one sits at its own density, so the four hold apart in grayscale and for
a reader who cannot separate the hues. The tile is one unit across and two
down; the plot stretches sideways, so the tile is not square once it is drawn,
and every tile is a stripe or a grid because neither shape stops a reader from
telling the four apart under a stretch. The definitions are written inside each
figure's own SVG with ids that carry the section id, so two figures on one page
never share an id and no page-level block is needed. A figure of one series
keeps its color on paper, because there is nothing to tell apart. A value
printed inside a patterned mark changes from paper to ink, and the mark takes a
hairline in ink so the reader sees where it ends.

A table prints as a table: the head repeats on every sheet, and nothing on it
reads as a control.

Measure on paper is `--reading-print`, 27em, which holds the longest line at 68
characters with the narrowest serif. The printed body is 11pt and `@page`
margins are 18mm top and bottom and 26mm at the sides, which puts the text block
at about 620px: the prose column is then two thirds of it rather than half, and
the findings row and the small multiples fill the rest. The measure cannot grow
to meet them without passing 68 characters, so the sheet keeps two widths on one
left edge. Every printed block starts at that margin, the step blocks included,
which open with a hairline the way a finding does rather than with an indent. A
label, a heading and the block under it never split across sheets, and a
findings row, a step and a quote never break inside.

The sidenote column carries `screen-only`. On paper every note is a footnote at
the page margin, the back link is a screen control and does not print, and a
footnote never splits across a sheet.

One trap to remember: a printed page is about 816px wide, so the 1000px rules
apply on paper as well. The print block overrides each rule it cares about
instead of trying to switch the query off. The wide band is the one exception,
and it earns it: a landscape or an oversize sheet is wider than 1001px, so the
width folded the rail on paper by accident rather than by rule. That band names
the screen media type, and the print block undoes none of it. Every role width
starts at the page margin on paper because the print block sets
`--role-inline` to 0 for both layouts, rather than because the wide layout set
it for one of them.

## Files

The kit is one flat folder. Every folder sits beside `build.py`, so the ZIP
unpacks into a folder a reader can run.

```
build.py              the command line and nothing else
package.py            ships the folders below
kit/
  art.py              seed_from, seeded, mark_shape, artwork,
                      resolve_highlight, mark_specimen
  assets.py           stylesheet() and script(): join the partials
  charts.py           the SVG builder for each chart kind
  cite.py             the report's citation, in three forms
  endmatter.py        the byline and the blocks after the last section
  guide.py            render_guide, the palette rows and the theme swatches
  inline.py           the inline markup parser: links, notes, terms
  notes.py            the sidenotes and the footnotes of every section
  page.py             the head, the header, the cover, the sections, the footer
  registry.py         finds kit/sections/*.py; TITLED comes from the modules
  text.py             esc, field, text, optional_text, check_text, url,
                      paragraphs, heading
  fonts.py            the type presets, their @font-face rules and their tokens
  theme.py            mix_oklab, relative_luminance, color_scheme,
                      theme_tokens, theme_icon, favicon_link, PRESETS
  sections/           one module for each section type; figure.py validates
                      and dispatches to charts.py
styles/               00-tokens 10-base 20-chrome 25-cover 30-artwork 40-cover
                      45-controls 48-layout 49-wide, one file for each
                      component, 90-state 95-responsive 99-print
scripts/              00-runtime, one file for each component, 99-boot
fonts/                one variable woff2 for each family, with its OFL licence
report.css report.js  the join, written by package.py, held by a test
```

Nine rules hold the layout together.

A section module states `NAME`, `TITLE_REQUIRED`, `ORDER`, `FIELDS`,
`render(section, heading_html, where, context) -> (body_html, attrs)` and
`SPECIMEN`. `registry.py` finds the modules with `pkgutil`, so no list is
edited to add a type. `TITLED` is the set of modules that need a title.
`ORDER` places the type on the guide, and the name breaks a tie, so two
authors can pick the same number.

`context` is one object that `page.py` builds for each report, before the first
section renders. `context.data` is the whole report, `context.theme` is the
theme, `context.terms` maps each glossary term to its definition, read from
every `glossary` section, and `context.term(name, where)` renders the control
that shows one term with its definition. A term no glossary holds stops the
build and names the term. A renderer reads the markup function with
`inline.for_section(section, where, term=context.term)`, so a glossary term
works in the text of every section type. A module that needs a report-wide
value reads it off the context and takes no new argument of its own.

A section id is a lowercase slug, and it cannot hold two hyphens in a row.
`--` is the separator the kit puts between a section id and an id it builds
from it. Every generated id on the page is `{sid}--{name}`: `{sid}--title` on
the heading of every section that renders one, which is what a figure's data
table and a data table's own caption point at, `views--tab-1` and
`views--panel-1` in a `tabs` section, `brief--label` on the heading of a
summary, `method--note-2` and `method--ref-2` on a note and the word that
points at it, and `terms--term-1` and `terms--definition-1` on a glossary entry
and its popover. The media types follow the same rule: `map--lightbox` on the
dialog of an image section and `before-after--compare` on the divider of a
comparison. `page.py` refuses an author's id that holds the separator, so a
generated id and a section id can never be the same name. `50-tabs.js` also
pairs a tab with a panel inside the tabs group it is in, rather than by id in
the whole document.

A figure writes two more: `{sid}--pattern-{n}` on a print fill and
`{sid}--reveal` on the window a line is drawn through, both inside the figure's
own SVG.

An end-matter block comes after the last section and has no section
id, so it puts the separator after the name of the block instead: `form--email` on a
form field, `form--email-error` on the message under it, and
`series-links--label` on the heading the series navigation points at. The
drawing does the same with `hero--mask` and `hero--fade`.

`notes.py` renders the notes of every section type. `page.py` calls
`notes.render(section, sid, where, context)` after the body of a section and
inside it, so the sidenote beside the reading column and the footnote under the
section come from one module and no section module writes note markup. It runs
after the body because it holds each note against the references the body
rendered: `inline.for_section` records the note number of every reference it
emits, under the id of the section, and `notes.py` reads that record. A `[^1]`
in a title, and a `[^1]` a link consumed, render no reference and reach no
note.

A component's CSS lives in one `styles/50-<name>.css` and ends with its own
`@media (max-width: 1000px)`, `@media (max-width: 760px)` and `@media print`
blocks. `assets.py` joins `styles/*.css` in sorted name order.
`95-responsive.css` and `99-print.css` keep page-level rules only. The
component band is order free, because each partial holds only its own
selectors. The five components that shipped before the split keep the numbers
`50` to `58`, which hold the join in the order the one stylesheet had.
`styles/50-image.css` holds the caption and the credit every media component
shares, plus the three role widths a picture may take; the comparison, the
gallery and the diagram read those two classes and own everything else.

A component's script lives in one `scripts/50-<name>.js`. `assets.py` wraps the
join in one IIFE, so the partials share one scope and `00-runtime.js` can hand
every later partial the same `kit` object. `kit.tokens` holds every duration,
read out of the stylesheet once at startup, and `kit.ms('--name')` reads one
more on demand, in milliseconds, whether the token is written in seconds or in
milliseconds. A script that waits reads the wait with `kit.ms()` rather than
typing it, so a duration cannot be changed in the stylesheet and left behind in
the script. `kit.onReady(fn)` asks for work at
startup and `kit.onFrame(fn)` asks for work on each frame the reader scrolls,
so no component edits another component's loop. `00-runtime.js` also marks
every `.scroll-edge` box while the reader is short of the end of it, so the
table wrapper and the diagram frame share one hint and one rule. `99-boot.js` runs the ready
list and adds the `enhanced` class last of all. A partial that holds the closing
tag of its own element stops the build and names the file, because the default
export writes both assets into the page.

`build.py` embeds the joined stylesheet and script from memory. `package.py`
writes the same join to `report.css` and `report.js`, and a test holds the
committed pair against a fresh join. Edit a partial, never the join.

`package.py` ships `kit`, `styles` and `scripts` whole, and still refuses a
top-level source file that is on neither its ship list nor its list of
deliberate omissions. It reads every shipped file as text, so the ZIP carries
text files only.

`tests/ccm_report_template/helpers.py` loads `build.py` by its path and gives
the suite the kit, a fixture report, `render(data)` and `build_page(data)`. A
family adds `test_<family>.py` and edits no other test file.

## The icon

`favicon.svg` is the kit's only icon and its drawing: three accent strokes on a
paper tile, the cover mark reduced to one shape. Three, not five, because a
16px tile at 1x turns five 2.5 unit strokes into 1.25px of ink with 1.5px
between them; three strokes at 3.2 units land on 1.6px of ink with 3.1px
between them, which survives the reduction.

The file is drawn in the default palette and is the source, not the output.
`build.py` paints the report's own theme into it at build time, swapping paper,
ink and accent for the theme's, and mixing the dark scheme stroke from the
theme's own accent and paper. The default export carries the painted icon as a
`data:` URI, so it still opens from disk with its icon. The hosted export links
`favicon.svg` beside `report.css`, but only while the theme is the palette that
file is drawn in: one shared icon cannot be five palettes, so a themed report
carries its own in the page. A build with no `favicon.svg` next to `build.py`
stops instead of shipping a page with no icon, and so does one whose icon no
longer carries the colors `build.py` knows how to swap.

The tile turns to ink under `prefers-color-scheme: dark`, and the strokes lift
with it. The accent alone holds 2.29:1 on that tile and goes muddy at 16px, so
the dark stroke is the accent with 40 percent paper mixed into it. On the
default theme that is `#c9877c`, which holds 5.03:1 and still reads as the
accent.

That rule is there to darken a light tile. A report whose own paper is already
dark carries a dark tile at rest, and the rule would then paint the theme's
ink, which is the light color, over it. So the build drops the whole rule from
the icon of a dark report, and the icon keeps the one tile the page is drawn
on. An icon file that no longer carries the rule stops the build, the way a
missing color does.

## The guide

`guide.html` is generated, like the report. `guide.template.html` is its source
and holds only the copy and the guide's own layout; every value that comes from
`report.json` or from the generator is a `{{name}}` placeholder that
`render_guide()` in `kit/guide.py` fills: the theme block, the icon, the hero
drawing, the three mark specimens, the palette with its hexes and roles, the
organization, the date, the canonical URL, the social image, the mark count,
the layout names, the table of section types and one specimen for each type.
The table and the specimens are read from the registry, so a type that ships is
a type the guide names and draws. A specimen states what the type does, when to
use it, the JSON it is built from, and the section that JSON makes.

The section specimens render in one pass, as one report, so the set shares one
context and the glossary any specimen reads is the glossary of the whole page.
Rendered one at a time, no specimen but the glossary's own could hold a
`{term}`, and the guide could not show a reader the form they write one in.
The prose specimen names a term the glossary specimen defines, which is the
form itself and the page proving it works. `render_guide()` refuses to build if the template asks for a
value it does not have, or if it holds a value the template does not use, and a
test compares the committed `guide.html` against a fresh render.

Four theme presets sit under the standfirst: warm, cool, night and clay, the
four themes the kit ships. Each one is the kit's own control with the theme's
five colors as five stripes inside it and the theme's name beside them, and the
one the page is showing takes `aria-pressed` and the `--rule-mark` accent rule
an open tab takes. Pressing one writes the five colors and the color scheme
onto the root element, so the whole page repaints in place, drawings and
figures included. The script is in `guide.template.html` and nowhere else: a
report carries its five colors in its own JSON file and has no use for a
switcher. The line under the swatches says so, and says that the `theme` block
is what a reader copies.

That is the point of the page. The kit's promise is that five colors in a JSON
file drive everything, and the page a visitor sees first is the first place that
promise can be false. It links `report.css` and `report.js`, so the specimen
lays out and draws in exactly as the cover does, and with scripts off it shows
the same ring the report shows.

## Do not

Do not add a font family, a radius, or a third easing curve. `--font-code` is
the exception already taken, and it is for the guide's code blocks only.
Do not type a raw hex, px size, or duration into a rule; add or reuse a token.
Do not write a fallback into `var()` for a token `00-tokens.css` holds; the
fallback hides a typing error rather than stating a value.
Do not add a fourth content width, or center something at a width no role owns.
Do not give a heading a width the block under it does not have.
Do not use uppercase labels, letter-spaced display type, or a drop cap.
Do not put muted text on `--wash` without the local override; it drops below 4.5:1.
Do not give an interactive edge `--rule`; it needs `--rule-strong`.
Do not make anything interactive shorter than `--tap`.
Do not turn on global smooth scrolling.
Do not name a screen-only part in the print stylesheet; give it the
`screen-only` class instead.
Do not escape a text field by hand; call the inline parser, which escapes it.
Do not edit `report.css` or `report.js`; edit the partial and run `package.py`.
Do not autoplay a gallery, or give any picture set a timer.
Do not put one caption on a set of pictures; each picture takes its own.
Do not ship a picture with no alt text, and do not write alt text for a
picture marked decorative.
Do not put text inside a chart's SVG; the label layer is HTML, so it holds the
token type size at every width.
Do not give a figure a fifth series; use `"multiples": true`.
Do not draw a bar or a stacked bar from a value under zero.
Do not make a chart mark focusable; the SVG is hidden and the data table is the
keyboard path.
Do not declare `color-scheme` in a stylesheet rule; the build reads it off the
paper and writes it with the five colors.
Do not paint a color into a drawing without a rule that follows the token as
well; the attribute is for a file lifted out of the page, and the rule is what
follows a theme.
