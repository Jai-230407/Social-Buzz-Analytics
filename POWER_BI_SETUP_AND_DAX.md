# Power BI Desktop — opening the project and understanding every measure

## Deliverable format: what is PBIP vs PBIX?

This package includes a **Power BI Project (`.pbip`)**: an editable human-readable report (`.Report/definition`) and a **TMDL semantic model** (`.SemanticModel/definition`). This is a documented Power BI Desktop format, not a `.pbix` binary. In Power BI Desktop on Windows, you can use **File → Save As → Power BI Desktop file (`.pbix`)** after opening the project. See https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview.

The `.pbip` was created from public PBIR/TMDL format specifications and was checked for JSON structure. Because this runtime is Linux, **it has not been loaded, refreshed or rendered in Power BI Desktop**; Power BI versions may require adjustments. For a guaranteed route on your PC, use the CSV-import steps below. Both routes are offered so you can complete the project regardless of your Desktop version.

## Option A: Open the preauthored PBIP source

1. Extract the **entire ZIP**; do not move only the `.pbip` file. Keep the sibling `.Report/` and `.SemanticModel/` folders.
2. On Windows with a recent Power BI Desktop version, double-click `powerbi/Social_Buzz_Dashboard/Social_Buzz_Dashboard.pbip`.
3. The project contains a self-contained **compressed copy of the synthetic cleaned CSV embedded into the TMDL Power Query M expression**. It has no machine-specific data path, so no credentials or local CSV connection should be needed for this demo.
4. If the model prompts for **Apply changes** or **Refresh**, accept it. Confirm four KPIs and category chart values agree with notebook values: **1,252,226 points** and **24,986 reaction events**.
5. When satisfied: **File → Save As → Power BI Desktop file (.pbix)**.
6. If it fails to load due to a report format/version incompatibility, follow Option B and rebuild from clean CSV. Microsoft documents PBIP as a project authoring format but Desktop is the actual render/refresh authority.

## Option B: reliable CSV import / build the report manually (recommended if PBIP won't open)

1. Open **Power BI Desktop → Blank report**.
2. Home → **Get Data → Text/CSV** → select `data/processed/fact_reactions.csv`.
3. Select **Transform Data** in Power Query. Rename your table `Reactions`.
4. Set types:
   - `Reaction ID`, `Content ID`, `Category`, `Content Type`, `Reaction Type`, `Sentiment`, `Date`, `Month`, `Month Name`: **Text**.
   - `Score`: **Decimal Number**.
   - `Datetime`: **Date/Time**.
   - `Year`: **Whole Number**.
5. **Close & Apply**. This CSV is *already cleaned and merged by Python*. Don't try to join Content and ReactionTypes again into the fact file; that would double-enrich it.
6. Right-click the Reactions table → New measure. Paste the DAX measures below.
7. Build the visuals in the page plan at the bottom; import `Social_Buzz_Interactive_Dashboard.html` separately to see the intended design.
8. Save as `Social_Buzz_Analytics.pbix`.

### Exact DAX measures

```dax
Total Popularity =
SUM('Reactions'[Score])

Reaction Events =
COUNTROWS('Reactions')

Unique Posts =
DISTINCTCOUNT('Reactions'[Content ID])

Distinct Categories =
DISTINCTCOUNT('Reactions'[Category])

Points per Reaction =
DIVIDE([Total Popularity], [Reaction Events])

Points per Post =
DIVIDE([Total Popularity], [Unique Posts])

Positive Reactions =
CALCULATE(
    [Reaction Events],
    'Reactions'[Sentiment] = "positive"
)

Positive Share =
DIVIDE([Positive Reactions], [Reaction Events])

Share of All Category Points =
DIVIDE(
    [Total Popularity],
    CALCULATE([Total Popularity], REMOVEFILTERS('Reactions'[Category]))
)

Category Score Rank =
RANKX(
    ALLSELECTED('Reactions'[Category]),
    [Total Popularity],
    ,
    DESC,
    DENSE
)
```

### Precisely what each measure does

- `SUM` aggregates **score points**, not likes, views, dollars, or users.
- `COUNTROWS` gives total reaction **events** in the active filter context, not distinct authors or impressions.
- `DISTINCTCOUNT(Content ID)` counts **posts that have at least one clean reaction** (not all posts ever uploaded).
- `DIVIDE(a,b)` safely returns blank if the denominator is zero unless you provide an alternate result.
- `CALCULATE` modifies the filter context (positive sentiment only).
- `REMOVEFILTERS(Category)` computes a category share denominator while preserving other current slicers such as month and format.
- `RANKX(ALLSELECTED(Category))` ranks visible/selected categories, so the rank can change under filters.

**Important model design caveat:** A single reaction-level fact table counts unique posts among posts with retained reactions, not all posted content, and its points-per-post metric excludes content with zero observed reactions. A true all-post denominator needs a separate Content dimension (including zero-reaction posts) and a suitable relationship.

## Executive Dashboard (page 1)

| Visual | Power BI visual type | Axis / Category | Values |
|---|---|---|---|
| KPI 1 | Card | — | `Total Popularity` |
| KPI 2 | Card | — | `Reaction Events` |
| KPI 3 | Card | — | `Unique Posts` |
| KPI 4 | Card | — | `Distinct Categories` |
| Category popularity | Clustered bar | `Category` | `Total Popularity` |
| Monthly score | Line chart | `Month` | `Total Popularity` |
| Sentiment | Donut | `Sentiment` | `Reaction Events` |
| Formats | Column chart | `Content Type` | `Total Popularity` |
| Category selector | Slicer | `Category` | — |

Sort category chart **descending** by `Total Popularity`. For the true top five, use a **Top N filter** on Category by `Total Popularity` (set N=5). A month formatted as `YYYY-MM` sorts lexicographically and chronologically in this single- and multi-year string form; if you build a broader model, use a proper Date dimension and a MonthStart date.

## Content Deep Dive (page 2)

| Visual | Axis | Value |
|---|---|---|
| Points per post | `Category` | `Points per Post` |
| Category event volume | `Category` | `Reaction Events` |
| Format filter | `Content Type` | — |
| KPI cards | — | `Points per Post`, `Points per Reaction`, `Positive Share` |

## Troubleshooting

- **No data after opening `.pbip`:** use CSV import; the TMDL M source may not have loaded or your Desktop may not recognize the authored PBIR schema.
- **Unexpected top category:** check whether your input is the provided synthetic sample versus the original Forage CSVs; check category cleaning and the reaction scoring join.
- **More rows after a join:** verify that Content ID is unique on the Content dimension and reaction Type is unique in ReactionTypes. Enforce 1-to-many relationships.
- **Top five chart shows 16 bars:** add a Top N visual filter. The preauthored source page deliberately displays category comparisons without a hardcoded Top N filter so all category data are visible.
- **Date labels alphabetical:** avoid sorting by month name; use `YYYY-MM` or a Date/MonthStart column.
- **Want the actual original Forage project:** obtain original CSVs via your Forage enrollment and replace the synthetic source files, rerun notebook, then use CSV import (or rerun the Python PBIP generator if you are deliberately maintaining the TMDL project).
