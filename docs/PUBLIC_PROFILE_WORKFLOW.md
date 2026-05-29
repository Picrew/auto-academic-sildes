# Public Profile Workflow

Use this workflow when the deck is about a person, lab, project, or company and
the source material comes from the public web.

## 1. Verify Before Writing

Collect at least two source classes:

- identity source: personal homepage, OpenReview profile, lab profile, GitHub
  profile, or institutional page.
- work source: paper page, project page, repo, leaderboard, demo, or benchmark.

Do not turn search-result snippets into biographical claims. If a claim matters,
it should be backed by a URL placed in `evidence.source` or a source manifest.

## 2. Choose Proof Surfaces

Select images by what they prove:

- homepage/profile page: proves identity and research positioning.
- paper title page: proves a technical thesis or authorship cluster.
- project page: proves artifact shape and research framing.
- leaderboard/table: proves comparison or measurement surface.
- GitHub repo: proves reproducibility, release shape, and artifact availability.

Avoid decorative portraits unless the slide is explicitly about identity. A
small cover thumbnail is enough.

Every non-cover screenshot, paper page, repo crop, project page, table, or
leaderboard must be inserted through an `evidence:` block with `evidence.image`,
finite crop, caption, and source. If a source has already been pre-cropped for
slide use, still write the full-frame crop explicitly. Top-level non-cover
`image` fields are accepted only as exact legacy mirrors of `evidence.image`.
If an image cannot earn that caption/source contract, leave it out.

## 3. Compile The Narrative

For a 5-6 slide profile, use:

- `cover`
- `stack`
- `matrix`
- `evidence`
- `evidence`
- `close`

Avoid `system`, `loop`, `product`, and `split` unless the person's work naturally
matches those semantic templates. Some of those layouts are intentionally tuned
for the original portfolio and should not be the default for public profiles.

## 4. Review Routes

- PPTX is the default delivery route because it is editable and institutionally
  portable.
- HTML is the style calibration route because it reveals layout taste quickly.
- Beamer is the formal PDF backup when a conservative academic handout matters.

Always inspect contact sheets. The automated quality report only catches
structural problems; it cannot tell whether the slide has taste.

If `quality-report.md` flags text budget errors, rewrite first. Public profiles
often gather long biography-like sentences; the deck should reduce them into
claims, source labels, and proof captions instead of shrinking the typography.

## 5. Public-Information Caution

Write with restraint. Public profile decks should sound like careful research
briefings, not claims of endorsement. Use phrases such as "public record",
"visible work", "profile anchor", and "representative artifact" when the source
is a web page rather than a private interview or CV.
