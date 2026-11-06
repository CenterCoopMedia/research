# CCM scrolling report template

Build reports, research papers, and narrative web pages from one editable JSON file. The output is standalone HTML. The default export opens from disk with no server, no package install, and no network request.

Start at the [guide](https://jamditis.com/ccm-report-template/guide.html). It shows the art, the palette, the type, and the section types on one page.

The [sample report](https://jamditis.com/ccm-report-template/) is what `report.json` builds. It runs a whole report through the kit in the order a reader meets one: three takeaways, a summary, prose with a note and a pull quote, the scrolling stage, the waterfall chart with its data editor, a bar figure, a sortable table, three findings, a chronology, a second run of prose, a glossary, a quote, the methods band with its sources and one placeholder download, then the authors, the read-next list and the correction log. Every number, name and quotation in it is invented. Its header links the guide and the examples index, and every example links back.

## Make a report

1. Copy this folder for your new report.
2. Edit `report.json` with a text editor.
3. Run `python3 build.py` from the copied folder.
4. Open `index.html` in a browser.

Python 3.11 or later runs the build with nothing else installed.

To keep several reports beside the template:

```bash
cp report.json my-report.json
python3 build.py my-report.json --output ../my-report/index.html
```

The build replaces the selected output file. Keep your JSON and edited source files in Git. Rebuild after each edit. Changes made directly to the exported HTML disappear on the next build.

## Hosted demo and asset links

The demo is live at `https://jamditis.com/ccm-report-template/`. The browser guide is at `guide.html`, and `report.css`, `report.js`, and `favicon.svg` sit beside it.

Use the complete `starter.html` markup with these asset links:

```html
<link rel="stylesheet" href="https://jamditis.com/ccm-report-template/report.css">
<link rel="icon" type="image/svg+xml" href="https://jamditis.com/ccm-report-template/favicon.svg">
<script defer src="https://jamditis.com/ccm-report-template/report.js"></script>
```

The kit styles a full report document. These links need the report structure in the starter. They do not convert an arbitrary page into a scrolling report.

To generate a report with hosted assets:

```bash
python3 build.py report.json --output starter.html --assets-url https://jamditis.com/ccm-report-template
```

The default build embeds the stylesheet, the script, and the icon in the page. Hosted-asset mode is the exception: that page fetches `report.css` and `report.js` from the base URL you pass, so it needs the network. The base URL must be absolute HTTP(S) with no query string and no fragment. The public asset URLs follow the deployed version. Copy the files beside your report when you need a fixed version. Do not treat a query string as version pinning.

The icon is the exception inside the exception. `favicon.svg` is drawn in the default palette and `build.py` paints your theme into it, so a report with its own colors carries its icon in the page even in hosted-asset mode. One shared file cannot be five palettes.

## Examples

Six complete pages, each built by `build.py` from the JSON file beside it, each in one of the four themes, and each linked from the guide under "In the wild". Every sentence, name, number and result on all six is invented for a design showcase.

| Page | What it holds |
| --- | --- |
| [A matter of scale](https://jamditis.com/ccm-report-template/examples/waterfall.html) | A waterfall unit chart with a local data editor and standalone export |
| [Who covers the town?](https://jamditis.com/ccm-report-template/examples/report.html) | A full research report: a county-by-county count of the paid people who cover local government in New Jersey |
| [Saying so](https://jamditis.com/ccm-report-template/examples/paper.html) | A research paper: how 60 invented newsrooms wrote their AI disclosures, and where on the page each notice sat |
| [Ninety days for one record](https://jamditis.com/ccm-report-template/examples/story.html) | A multimedia feature: one public records request from the first email to the last of 212 pages |
| [Five things the 2026 partner survey found](https://jamditis.com/ccm-report-template/examples/brief.html) | A one-page brief: what 214 invented partner newsrooms said they need next |
| [How a collaborative reporting project runs](https://jamditis.com/ccm-report-template/examples/explainer.html) | An explainer: the eight months from the first phone call to publication day |

The [examples index](https://jamditis.com/ccm-report-template/examples/) links all six.

Each page opens on a drawing of its own. The twelve marks are seeded from the report's `url`, or from its `title` when it states no url, so two reports in one theme carry two mark sets and the same report draws the same marks on every build.

`examples/` holds four scripts of its own. `downloads.py` writes the placeholder files the sample and the examples offer for download, each CSV read out of the table on the page that offers it, `pictures.py` draws the seven placeholder pictures the story page points at, `index.py` builds the index page from `index.json`, and `social.py` paints the 1200 × 630 social image of every page, the sample's own `og-image.png` included, from that page's cover drawing. `package.py` runs the first three after it builds the sample and the guide. It does not run `social.py`: that one needs Playwright and Pillow, which are tools for the examples and not dependencies of the kit, so the images are painted by hand and committed. Run it after a change to the drawing or to a cover; every card stays under 90 KB. `package.py` keeps the whole folder out of the ZIP, and `KEPT_BACK` states why.

## Content settings

| Field | Use |
| --- | --- |
| `title` | Cover headline, page title, and social title |
| `subtitle` | Standfirst under the headline, meta description, and social description |
| `organization` | Publisher: the header brand, the page title suffix, and the footer colophon |
| `series` | Series line on the cover and in the footer |
| `authors` | Byline on the cover. One string, or a list of authors, each with a `name` and an optional `role`, `bio` and `url` |
| `contributors` | Optional. A credits list. Each item has a `role` and a `name` |
| `related` | Optional. One to three reports to read next. Each item has a `title`, a `url` and a `description` |
| `series_links` | Optional. The report before this one and the report after it. Holds `previous`, `next`, or both, each with a `title` and a `url` |
| `form` | Optional. A signup form. Needs an `endpoint`, a `heading` and a `reason`. Takes an optional `button`, an optional `inline` and an optional `fields` list |
| `corrections` | Optional. A dated log. Each item has a `date` and a `text` |
| `downloads` | Optional. Files the reader can take. Each item has a `label`, a `url`, a `format` and a `size`. They render inside the methods band, so a report with downloads holds exactly one `methods` section |
| `date` | Byline date and footer date |
| `hero_caption` | Caption under the cover drawing |
| `tagline` | Optional. Left footnote at the foot of the cover |
| `scroll_cue` | Optional. Right footnote at the foot of the cover |
| `notice` | Optional. Specimen, draft, or editorial notice under the cover |
| `template_url` | Optional. Adds a "Use this template" link to the notice; remove for finished reports |
| `header_links` | Optional. One to three links beside the contents control, each with a `label` and a `url`. The url is an absolute HTTP(S) address or a plain relative path beside the page, such as `guide.html` or `../index.html`. Below 560px a report's links move into the contents panel, where there is room for them |
| `pdf_url` | Optional. Adds a "Read the paper" button to the cover; absolute HTTP(S) |
| `url` | Absolute final report URL. Canonical link, social URL, and the address printed in the footer |
| `image_url` | Absolute URL of the report's 1200 × 630 social image |
| `theme` | Five six-digit hex colors |
| `fonts` | Optional. The type preset the report sets in: `{ "preset": "system" }`, `field`, `quill` or `ink`. Leave it out for `system` |
| `layout` | Optional. `reading`, the centered column, or `wide`, the column against the gutter with a rail beside it. The default is `reading` |
| `lang` | Optional. The language of the report, written on `<html>`. A lowercase tag from the subset of BCP 47 the kit reads: a language of two or three letters, an optional script of four letters, an optional region of two letters or three digits, any number of variants, or a private use tag such as `x-local`. Examples: `en`, `es-419`, `pt-br`, `zh-hant-tw`. The default is `en` |
| `sections` | Ordered list of report sections |

Every text field is text. A number, a list, or an object where a sentence belongs stops the build and names the field, the section, and the step or item it is in, because `str()` on a list would otherwise render its Python form on the page.

`tagline` and `scroll_cue` are independent. Set both, one, or neither. The footnote band at the foot of the cover appears only when at least one of them is set.

The sample contains invented examples. Replace them and their notes before publication. Use the publisher's approved name and identity. The small CCM text mark is a template treatment, not an official logo asset.

Content fields carry text and the inline markup in the next section. HTML is escaped. Links accept absolute HTTP(S) URLs. Use Unicode characters directly in JSON.

## The page frame

The cover byline states how long the report takes to read. The build counts the words in every text field of every section, divides by 200 and rounds up. No field sets it.

The header carries a rule on its bottom edge that reports the reader's place in the report, and beside the brand it names the section the reader is in. The contents panel marks the same section. With no script the rule is hidden, because a rule that can only report zero is worse than no rule.

The footer gains **Copy link** and **Cite** beside the print button. Copy link writes the canonical `url` plus the section the reader is in. Cite opens a dialog with the report's citation in plain text, APA and BibTeX, each with a copy button. All three are built from `title`, `authors`, `organization`, `date`, `series` and `url`, so a citation can never name something the page does not carry. Paper prints the plain citation under the colophon.

## Text in any field

Every text field of every section reads one inline markup:

| You write | You get |
|---|---|
| `[the guide](https://example.org/guide)` | a link, with `rel="noopener"` |
| `[^3]` | a reference to note 3 of the same section |
| `{term}` | the glossary entry for that term |

A link URL must be absolute `http://` or `https://`. A reference to a note the
section does not carry stops the build, and so does a term the glossary does not
hold. Every other character is escaped, so text cannot add markup.

Titles, labels, step captions, and a findings `value` and `unit` are plain text.
A title names its section in the contents as well as in the heading, so it takes
no link.

Numbers on the page carry no leading zero. A step card reads "3 of 4" and the
citation list counts 1, 2, 3.

## Section types

Give every section a unique `id`. It must start with a lowercase letter and may then use lowercase letters, digits, and hyphens, such as `key-findings`. An id like `1-intro` fails the build. The ids `main` and `top` are reserved.

Two hyphens in a row are reserved as well, because `--` is what the kit puts between a section id and the name of an id it builds from that section: `counts--title` on a section heading, `views--panel-1` on a panel of a `tabs` section, `counts--pattern-1` on a print fill. An id of your own that holds `--` fails the build, so a generated id can never take the name of a section.

Every type except `quote` and `image` needs a `title`. It becomes the section heading, the contents link, and the address the heading links to, so an empty one would ship an empty heading and a link with no name.

| Type | Fields beyond `type` and `id` |
| --- | --- |
| `summary` | `title`, `text` (under 100 words) |
| `takeaways` | `label`, `title`, `items` (list of text, 2 to 5) |
| `prose` | `label`, `title`, `paragraphs` (list of text, or a block object) |
| `steps` | `label`, `title`, `items`: each has `title` and `text` |
| `glossary` | `title`, `terms`: each has `term` and `definition` |
| `waterfall` | `label`, `title`, `dataset`; see Waterfall charts below |
| `scrolly` | `label`, `title`, optional `center_label`, `steps` |
| `findings` | `label`, `title`, `items`: each has `value`, `title`, `text`, and optional `unit`, `note` and `trend` |
| `figure` | `label`, `title`, `chart`: `kind`, `unit`, `value_format` and the values the kind reads, `caption`, and optional `source` and `note` |
| `table` | `title`, `caption`, `columns`: each has `label`, `type` and optional `unit`, `rows`, `sort`, and optional `note` and `source` |
| `quote` | `text`, `attribution` |
| `tabs` | `label`, `title`, `panels`: two to five, each has `label` and `paragraphs` |
| `accordion` | `label`, `title`, `items`: each has `summary` and `paragraphs`; optional `exclusive` |
| `timeline` | `label`, `title`, `events`: each has `date`, `title`, `text` |
| `image` | `src`, `alt`, optional `caption`, `credit`, `decorative`, `lightbox`, and `width` of `reading`, `figure` or `bleed` |
| `compare` | `label`, `title`, `before` and `after`: each has `src`, `alt`, `label`; optional `caption` |
| `gallery` | `label`, `title`, `items`: each has `src`, `alt`, `caption` |
| `diagram` | `label`, `title`, `nodes`: `id`, `label`; `edges`: `from`, `to`, optional `label`; `layout` of `row`, `column` or `ring`; optional `caption` |
| `part` | `number`, `title`, optional `deck` |
| `methods` | `title`, `paragraphs`, optional `brief` of under 80 words, `sources`: each has `label`, `url` |

Reorder, repeat, or remove sections. The contents menu follows their order and uses each section's title. Quote and image sections carry no title, so they do not appear in the contents menu.

In a findings item, `unit` prints under the numeral and `note` prints under the text. Both are optional, and leaving one out leaves no empty element behind. Use them for the measure and the caveat: what the number counts, and over what period.

A findings item also reads an optional `trend`. A `trend` is a list of 3 to 24 numbers and draws the sparkline beside the numeral.

A scrolly section needs at least one step. Each step has:

```json
{
  "title": "Explain one change.",
  "text": "Connect the visual change to the argument in the report.",
  "caption": "Describe the visual state in plain text.",
  "layout": "groups",
  "highlight": 4
}
```

Available layouts are `scatter`, `groups`, `network`, and `orbit`. `highlight` takes either an integer from 0 to 12, which colors that many marks from the start of the set, or a list of mark indices from 0 to 11, such as `[0, 4, 8]`, with no index repeated. `center_label` changes the word inside the orbit ring. Its default is `Community`, and it holds at most 14 characters, because a longer word does not fit the ring.

The visual always contains 12 decorative marks. It is a narrative illustration, not a data chart. Do not use mark counts, areas, or distances to imply measured values. Put verified numbers in findings with units, dates, and source context. A `figure` section draws the measured numbers as a chart.

## Waterfall charts

A `waterfall` section uses the supplied “A matter of scale” interaction. It appears in the sample report, the research report example, and its own example. The contents menu links to its section heading.

Set `dataset` to an object with `title`, `unit`, `totalSquares` (1000, 2500 or 5000), `status`, `source`, `caveat`, and two to eight `groups`. Each group has a `label`, non-negative `value`, six-digit hex `color`, and optional `shortLabel`, `headline`, and `description`. An optional `summaryHeadline` names the final summary. Groups appear in data order. Use non-overlapping groups whose sum is the intended population.

“Use your data” opens the local editor. Readers can change values, colors, and narration, add or remove groups, sort by value, import or export JSON, and download a standalone HTML chart. Edits stay in the current browser page until exported. They do not change the report source. Copy an exported JSON dataset into a section's `dataset` field to rebuild the report with it.

The chart follows the report's scroll without an inner scroll frame. Styles and IDs stay inside each chart's shadow root. Without JavaScript, the report shows the input table and source notes. Print shows the full data table. The “Less motion” control replaces falling squares with immediate placement. The download includes the renderer and editor and opens offline. Exported social titles and descriptions use the edited data. Set the final publication URL and social image before publishing an exported chart; it does not copy these from the parent report.

## Blocks inside a prose section

An item of `paragraphs` is a string, or one of five objects. Every block keeps the reading column and adds no card and no color.

| You write | You get |
| --- | --- |
| `{"subhead": "What the work found"}` | a third-level heading |
| `{"list": ["One.", "Two."], "ordered": false}` | a list; `ordered` is optional and false by default |
| `{"callout": {"title": "One fact", "text": "..."}}` | an aside on the wash; `title` is optional |
| `{"caveat": {"text": "..."}}` | the same aside with a stronger rule and the title "Caveat" |
| `{"pullquote": "one sentence"}` | one sentence at display size |

A pull quote is a lift. Write the sentence a reader sees, without markup in it: the build reads it back against the paragraphs of the same section as a reader sees them, so a sentence that holds a link or a `{term}` can be lifted, and a pull quote that is not in the text stops the build.

## Notes

Any section can carry `notes`, a list of text. A `[^1]` in any text field of that section points at note 1 of that section.

Above 1000 pixels the note sits in the column beside the reading column, level with the word that points at it: the rail in the `wide` layout, the margin between the column and the figure width in `reading`. On a phone, on paper, with scripts off, in the `reading` layout on a window too narrow for that margin, and in a section too short to hold the notes beside it, the same note is a footnote at the end of the section with a link back to the word the reader left.

A note with no `[^n]` pointing at it stops the build, because nothing on the page would reach it. A title is plain text and a `[^1]` inside link syntax is a link, so neither of those counts as the reference.

A glossary definition holds no `[^n]`. The definition is shown twice, in the entry and in the popover, so one reference would put one id on the page twice. Put the note on the text that uses the term.

## The fields a figure reads

A `figure` states one `kind` and the list that kind reads.

| Kind | List | One item |
|---|---|---|
| `bar` | `bars` | `label`, `value`, optional `series` |
| `dot` | `bars` | `label`, `value`, optional `series` |
| `line` | `series` | `label`, `points` of `x` and `y` |
| `slope` | `lines` | `label`, `before`, `after` |
| `range` | `rows` | `label`, `low`, `high` |
| `stacked` | `rows` | `label`, `segments` of `label` and `value` |

The chart also reads `value_format` (`integer`, `decimal` or `percent`, default `integer`), `sort` (default true, for `bar`, `dot`, `range` and `stacked`), `percent`, `multiples`, and, for `slope`, `start_label` and `end_label`.

`percent` is for `stacked` and normalizes each row to 100, so the reader compares the share and not the total. The picture then draws the share, and the label on each segment states that share. The data table under the figure keeps both: one column for the value you gave and one for the share it draws.

A figure carries at most four series in one chart, because four marks are what a reader tells apart without color. `multiples` draws one small chart for each series instead, on the one scale the whole figure shares, so a figure with five series or more sets `multiples` and builds. Every panel draws in the first series color: a panel holds one series and its own heading names it.

## Tabs and accordions

A `tabs` section holds two to five panels of prose under a row of text tabs. Give each panel a `label` of one or two words and a list of `paragraphs`:

```json
{
  "type": "tabs",
  "id": "views",
  "label": "Example views",
  "title": "One question, three answers.",
  "panels": [
    {"label": "Reporters", "paragraphs": ["What this group gains."]},
    {"label": "Editors", "paragraphs": ["What this group weighs."]}
  ]
}
```

A report with fewer than two panels or more than five stops the build. The tab list appears only when the script runs. With no script every panel shows under a heading that repeats its label, so no panel is behind a control that cannot act. Paper prints every panel the same way.

An `accordion` section holds a list of summaries a reader opens for the detail under each one. Give each item a `summary` and a list of `paragraphs`. Set `exclusive` to `true` to close the open item when the reader opens another one:

```json
{
  "type": "accordion",
  "id": "questions",
  "label": "Example questions",
  "title": "The questions readers ask most.",
  "exclusive": true,
  "items": [
    {"summary": "How were the newsrooms selected?",
     "paragraphs": ["State the sampling frame."]}
  ]
}
```

Write a summary that is useful on its own. Many readers never open an item. Paper prints every panel open.

## Pictures

`src` points at your own file. It takes an absolute HTTP(S) URL, a path beside the report with forward slashes and no `..` in it, or a `data:image/svg+xml` URI. A path with a backslash in it, such as `pictures\map.png`, stops the build: a page reads forward slashes on every operating system. The kit ships text files only, so every specimen on the guide draws its own picture into a data URI and says in its caption that the picture is a placeholder.

`alt` is never optional. Describe what the picture shows. A picture that carries no information takes `alt: ""` and `decorative: true`, and the two cannot be set any other way round.

`lightbox: true` opens the picture at full size in a dialog. Escape closes it, a click outside closes it, and focus goes back to the picture. With scripting off the picture is a link to its own file.

## End matter

Six blocks follow the last section, in one fixed order: the authors, the credits, "Read next", the series links, the form and the corrections. Each block renders only when the report carries the field it reads. A field the report does not carry leaves no empty element behind.

`authors` takes the string the kit shipped with, or a list of authors. The byline joins the names with commas and "and". "About the authors" renders after the last section only when an author carries a `bio` or a `url`; a row of bare names repeats the byline and adds nothing. Every field an author gives is read and checked before that decision, so a bad `role`, `bio` or `url` stops the build and names the author and the field.

`related` holds one to three reports and takes its column count from that number. `series_links` holds a previous link, a next link, or both. The field is `series_links` and not `series`, because `series` is the series line on the cover and in the footer.

`downloads` render inside the methods band, under the citations. Each link states its format and its size, so the reader knows what the click starts. Every methods band renders the list, so a report with downloads holds exactly one `methods` section: with none the files would print nowhere and with two they would print twice, and each of those stops the build.

The form has settings of its own, and the next section states them.

## The form

A form ships only when `form.endpoint` is set, and the endpoint is an absolute HTTPS URL. `reason` states what the reader gets and how often, and it prints beside the button. `fields` defaults to one required email address. Each field takes a `name`, a `label`, an optional `autocomplete`, and an optional `required` whose default is true. At least one field must be required, because a form where every field is optional sends an empty reply and then tells the reader it has their answer. A blank label stops the build and names the field.

The form element keeps some names for itself: `action`, `method`, `submit`, `reset`, `elements`, `length`, `name`, `target`, `enctype`, `encoding`, `acceptCharset`, `autocomplete`, `noValidate`, and the spam trap's `website`. A field with one of these names hides the property of the same name behind its own input, so a script that reads `form.action` gets the input instead of the address. Such a name stops the build. The kit knows the autocomplete token for `email`, `full-name` and `organization`; every other field states its own.

`inline` chooses the send, and its default is false. Without it the script checks every field and then lets the browser post the form, so the reader leaves the page and the endpoint answers with its own page. With `inline: true` the script posts with `fetch`, the reader stays on the page, and one sentence takes the place of the form. Set `inline` only when the endpoint answers with CORS headers, such as Web3Forms or Formspree. Without those headers the browser rejects an answer the endpoint already accepted, and the page tells the reader the send failed after it landed.

## Motion

The stage holds four layouts: `scatter`, `groups`, `network`, and `orbit`. With motion on, the scroll position drives the drawing: the marks glide from one arrangement to the next as the cards pass, the connection lines of one state crossfade into the lines of the next, and the progress rule fills in the accent with the reader's place instead of stepping per card. Each state carries its own color, so the drawing warms from ink to the accent as the argument builds. The cover draws its own marks once per load. The header carries a pause control. Reduced motion and the pause control run the same path: the stage fires one settled state per card and every change becomes instant, so the reader still gets the right state and the correct caption, with nothing moving.

## Responsive

Below 1000px the rail of the `wide` layout folds into the column, and the stage stops being a column and becomes a band pinned under the header, with the drawing, the caption, and the progress rule inside it. Each step card then gets a screen of its own, clear of the band and of the soft edge under it. At 760px the cover, the findings grid, and the footer go to one column, and a report's header sheds the organization name. Below 1000px a report's header also sheds the section title and the motion label, so that a report's own links, up to three of them, have the room they need from 561px up. The guide and the examples index sheds the organization name at 420px instead, because they carry no links past two and no controls. Nothing in a header wraps to a second line: the links and the controls hold their own width, and the section title and the organization name cut off with an ellipsis. Nothing scrolls sideways from 1440 down to 320, and nothing interactive is shorter than 44px. A wide table below 760px, and a diagram at any width, scroll inside a box of their own, and each one shows a shade at its trailing edge while there is more to the side.

## Print

The browser print button gives a compact reading version. The rail of the `wide` layout is a screen band and names the screen media type, so both layouts print one column at the page margin at every sheet size, a landscape or an oversize sheet included, and the report prints in the faces its preset embeds. Paper is white, ink is black, and the screen-only chrome goes away: the grain, the sticky stage, the controls, and the cover buttons. The stage cannot scroll on paper, so the page prints one static copy of it per step: the sample's four states run as small multiples, two by two, above the step texts, each with its caption. The header keeps the brand and the footer keeps the canonical URL and the date, which is what a printed copy is passed around with. Every step and caption prints. It is not a tagged or publication-ready academic PDF.

## Choose a format

- **Report:** cover, introduction, scrolly explanation, findings, implications, methods.
- **Research paper:** cover, abstract (`prose`), findings, discussion (`prose`), methods and sources. Add `pdf_url` for the full paper.
- **Short web page:** cover, one prose section, one scrolly section, and sources.

## Choose the type

A report names one type preset in an optional `fonts` block:

```json
"fonts": { "preset": "field" }
```

| Preset | Body | Display and large numerals | Files it embeds |
|---|---|---|---|
| `system` | the reader's serif stack | the same stack at weight 800 | none |
| `field` | Figtree | Bricolage Grotesque at 800 | 97 KB |
| `quill` | Nunito Sans | Fraunces at 900, soft and wonky | 152 KB |
| `ink` | Recursive linear | Recursive casual at 1000 | 305 KB |

Leave the block out and the report sets in `system`, which embeds nothing and asks no font server for anything. Name any of the other three and the build writes that preset's woff2 files into the page as data, so the export still opens from a disk with no network. A hosted-asset build links them from `{assets-url}/fonts/` instead.

The files are latin subsets under `fonts/`, one variable file to a family, each with its OFL licence text beside it. A character the subset does not carry falls back to the reader's own faces. Any name but those four stops the build and lists the four.

## Choose the layout

A report names one page layout in an optional `layout` field:

```json
"layout": "wide"
```

`reading` is the default: one column, centered, 34em wide. `wide` puts the same column against the page gutter and opens a 22em rail beside it. The rail holds the sidenotes of a section, a pull quote inside a run of paragraphs, and any figure or table section that carries `"rail": true`:

```json
{
  "type": "figure",
  "id": "coverage",
  "title": "Coverage by county",
  "rail": true,
  "chart": { "kind": "bar", "unit": "newsrooms", "bars": [] },
  "caption": "An invented example."
}
```

Every other block keeps its own width, so a figure, a table, a timeline and the scrolly stage span the full figure width and break past the column. Below 1000 pixels the rail folds into the column at the place you wrote each block, and a phone reads one column in either layout. Paper reads one column too.

Use `wide` when the report has notes or figures and `reading` when it is prose alone. Any name but those two stops the build and names both.

## Change the visual theme

Edit the five `theme` colors. Keep text contrast readable. Default colors are a suggested CCM treatment, not a claim about official brand standards.

| Setting | Default | Purpose |
| --- | --- | --- |
| `paper` | `#f6f3eb` | Page and text-card background |
| `ink` | `#292925` | Text, lines, buttons |
| `accent` | `#a33e36` | Highlights and large numbers |
| `secondary` | `#466958` | Connections and cover caption |
| `wash` | `#e7e4d9` | Dividers and methods background |

The kit ships four themes. The guide shows all four as swatches at the top of the page, so you can read one before you take it; press a swatch and the page repaints in place.

| Theme | `paper` | `ink` | `accent` | `secondary` | `wash` |
| --- | --- | --- | --- | --- | --- |
| warm | `#f6f3eb` | `#292925` | `#a33e36` | `#466958` | `#e7e4d9` |
| cool | `#f1f4f3` | `#1b2828` | `#315d73` | `#51694b` | `#dce5e2` |
| night | `#1f2023` | `#ece9e1` | `#d98b7c` | `#8fb3a0` | `#2a2b2f` |
| clay | `#f7f4ef` | `#292831` | `#9b5324` | `#3f5f8a` | `#ebe6dd` |

A dark paper such as night's needs nothing else. The build reads the paper and writes the page's `color-scheme` from it, so the browser's scrollbars and form controls match the report, and it drops the icon's own dark treatment, because that tile is already dark.

Those five are the whole theme. Every other color on the page, including every hairline, every muted label, the focus ring, and the icon, is mixed from them, so a new theme moves the report, the guide, and the icon, and leaves no stranded gray behind. `DESIGN.md` lists every token, every mix, the contrast each pair holds, and the rules the stylesheet follows. Read it before adding a rule.

`report.css` holds typography, spacing, responsive behavior, and print rules. `report.js` holds the four visual layouts and the scrolling behavior. The generator embeds both in each default export.

The reading column is set in ems, so it follows the type instead of guessing at it. It is 34em of the 20px body, which is 680px, and it holds 62 to 66 characters a line in every preset.

## The guide

`guide.html` is generated, like the report. Edit `guide.template.html`, which holds the copy and the guide's own layout, and rebuild:

```bash
python3 build.py --guide --output guide.html
```

Everything on that page that comes from `report.json` or from the generator is a `{{name}}` placeholder: the theme block, the font block, the icon, the hero drawing, the three mark specimens, the palette and its hexes, the four theme swatches, one specimen for each type preset, one for each layout, the organization, the date, the canonical URL, the social image, the mark count, the table of section types, and one specimen for each section type. A new theme moves the guide with the report, and the build fails if the template and the generator disagree about what is on the page.

The specimens render in one pass, as one report, so the whole set shares one glossary: the prose specimen names a term the glossary specimen defines, which is how the page shows what a `{term}` looks like.

## Design reference

Reference: the locally saved "Scenarios for our Economic Future" Anthropic report, captured September 9, 2026.

What was studied: the reading approach. Warm paper, faint ruling, irregular ink marks, generous space, a narrow measure, a visual stage that pins while short narrative cards pass it, and captions that name each state. The saved file contains no JavaScript, so it showed the visual structure but not the original timing or interactive behavior.

What was built new: the marks and the four layouts, the stylesheet and its token system, the generator, the icon, and every line of demonstration copy. No text, font, mark, image, or saved-page asset was copied. The page uses native scrolling, and intercepts no wheel or touch event.

## Check before publication

Read the full output at desktop and phone widths. Follow every contents link. Test the motion control and print preview. Review custom theme contrast. Confirm all claims and links. Check that every `{term}` has a glossary entry, and that every glossary definition is 40 words or fewer.

Set the final `url` and `image_url`. The url is also the seed of the cover drawing, so a report keeps its own marks once it is set. Replace the demo's `og-image.png` with a 1200 × 630 image for your own report; the ZIP does not ship it. Check the icon in a light and a dark browser tab, since it carries its own dark treatment. A theme with a dark paper drops that treatment, because the tile is already dark; the build decides from the paper, and it sets the page's `color-scheme` from the same reading, so scrollbars and form controls match the report. Remove the demonstration notice, the template link and the `header_links` block, which point at this kit and not at your report.

The output keeps the full text without JavaScript. Motion preferences disable transitions; visual states still change instantly with scroll. Each step includes a text description. The default export makes no external requests, stores no visitor data, and needs no backend.

Upload the built HTML and social image through your normal publication process.

## Refresh the downloadable demo

Run `python3 package.py` to rebuild the offline demo, the hosted-asset starter, the guide, and `template.zip`. It refuses to build if a file it means to ship is missing, or if a source file in the folder is on neither its list nor its list of deliberate omissions. The ZIP contains the template sources, the guide and the template it is built from, and `DESIGN.md`. It omits the social preview image; supply your own image for each published report.

## Files

The kit is one folder. Every part of it sits beside `build.py`, so the ZIP unpacks into a folder that builds.

```
build.py              the command line
package.py            rebuilds the exports, the assets and the ZIP
report.json           the content of the demonstration report
kit/                  the generator, one module for each part of the page
  sections/           one module for each section type
styles/               the stylesheet, one file for each part of the page
scripts/              the script, one file for each part of the page
fonts/                one variable woff2 for each family, with its OFL licence
report.css report.js  the join of the partials, written by package.py
guide.template.html   the source of the guide
favicon.svg           the icon, painted in the report's own theme
```

`build.py` joins `styles/*.css` and `scripts/*.js` in sorted name order and writes both into the page. `package.py` writes the same join to `report.css` and `report.js`, which the hosted export links and the ZIP ships. Edit a partial, not `report.css` or `report.js`: the next build replaces both.

A new section type is one new module in `kit/sections/`. It states its name, whether it needs a title, the fields the guide's table lists, how it renders, and one specimen. Nothing else lists the types.

## Tests

The suite covers the generator's validation and escaping, the themed icon, the type presets and the two layouts, the guide against a fresh render of its template, the reproducibility of the committed demo, the joined assets, and the contents of the ZIP. Run it from the repository root: CI runs the suite and the drift check on every push and pull request that touches the kit.

```bash
python3 -m unittest discover -s tests -t . -v
```

No packages to install.
