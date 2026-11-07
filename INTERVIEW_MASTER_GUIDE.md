# Social Buzz — Complete Interview Master Guide

**This guide accompanies** `Social_Buzz_End_to_End_Analytics.ipynb`, its executed copy, the synthetic data and the Power BI report project. Every numeric finding below is calculated from the **synthetic practice data**. It is not the official Accenture/Forage result. For genuine Accenture simulation participation, enroll and complete its tasks yourself; a self-built reproduction is a portfolio exercise, not an internship at Accenture.

---

# PART A — What exactly happens, from start to finish?

## Stage 0: A consultant receives a messy business request

**Scenario:** The fictional Social Buzz platform has grown rapidly and is thinking about how to scale. The broader case mentions big-data audit, IPO-related advice and analysis of high-performing content. Our assigned **analytics workstream** is narrower: rank the *five content categories* by **total weighted popularity points** and explain what those rankings could mean for content strategy. We do not claim that these three small CSVs establish enterprise IPO readiness.

**Stakeholders:** Senior product/strategy, analytics and marketing decision makers. They do not primarily care about pandas syntax. They care about whether they should promote more content about animals, science, technology, etc., and what evidence supports the decision.

**KPI agreed in advance:** `Popularity Score = sum of the predefined numeric scores of all valid reaction events associated with posts in a category`. This is **not** click-through rate, number of likes, reach, unique users, sentiment-model output, customer segmentation or revenue.

**What we deliver:** A cleaned analytic dataset, a reproducible notebook, a Power BI-ready event fact table and an executive dashboard/report with recommendations and limitations.

## Stage 1: Understand the normalized data model

### Table 1: Content

Each row is a **post**. Columns `Content ID`, `Type` (photo/video/GIF/audio), `Category` (animals, science, etc.). `User ID` and `URL` may also exist but are not essential for the target KPI.

### Table 2: Reactions

Each row is a **reaction event**. It includes `Content ID` (which post), `Type` (what reaction: like, heart, hate, etc.) and `Datetime`. If available, `Reaction ID` identifies individual reaction events. Importantly, this table is **not** one row per user, and a reaction is not equivalent to a post.

### Table 3: ReactionTypes

One row per reaction type, with `Type`, `Sentiment` (positive/neutral/negative) and `Score` (numerical weight assigned by the case rules).

**Relations:** `Content` **1→many** `Reactions`; `ReactionTypes` **1→many** `Reactions`. To attach scores to posts, join Reactions to Content on `Content ID`, then join Reactions to ReactionTypes on reaction `Type`. Rename the two meanings of `Type` first. Never join both `Type` columns blindly.

### Toy demonstration, fully by hand

Content:

| Content ID | Type (format) | Category |
|---|---|---|
| P1 | photo | animals |
| P2 | video | science |

ReactionTypes:

| Type (reaction) | Sentiment | Score |
|---|---|---:|
| like | positive | 50 |
| love | positive | 65 |
| dislike | negative | 10 |

Reactions:

| Reaction ID | Content ID | Type (reaction) |
|---|---|---|
| R1 | P1 | like |
| R2 | P1 | love |
| R3 | P2 | dislike |

After merging:

| Reaction ID | Category | Format | Reaction Type | Score |
|---|---|---|---|---:|
| R1 | animals | photo | like | 50 |
| R2 | animals | photo | love | 65 |
| R3 | science | video | dislike | 10 |

Now:

- Animals total score = **50 + 65 = 115 points**, two reaction events, one reacting post.
- Science total score = **10 points**, one reaction event, one reacting post.
- Total points = **125**; exactly **3 events**.
- This tells us nothing about whether animal posts outperform science posts per 1,000 impressions because impressions were not provided.

**Why join validation matters:** If ReactionTypes has *two* `like` rows, a single R1 event would become *two* rows after joining; the calculated popularity would silently inflate. The notebook enforces `validate='many_to_one'` and checks row counts.

## Stage 2: Clean the data — understand why each decision matters

1. Remove meaningless CSV export-index columns if found (`Unnamed: 0`). This is metadata, not necessarily data.
2. Standardize join keys to trimmed strings. A `Content ID` with trailing spaces might otherwise not match its post record.
3. Standardize category labels to lowercase and remove stray quotation marks. For example, `"Animals"`, `ANIMALS`, `animals ` should aggregate under one category.
4. Rename `Type` in Content to `content_type`; rename `Type` in Reactions to `reaction_type`. These columns have different business meanings.
5. Parse reaction `Datetime` as an actual datetime. Invalid dates must be investigated; the notebook excludes them from a consistent all-purpose analysis table.
6. Make `Score` numeric; check the lookup has exactly one mapping per reaction type.
7. If a stable Reaction ID is supplied, remove duplicated event IDs. If not supplied, don't assume identical values are necessarily duplicate events; the notebook assigns row identifiers instead.
8. Flag unmatched content IDs and unmapped reaction types; never fill missing reaction scores with zero as that changes the metric.
9. Exclude rows lacking required join information and record how many were removed.
10. Reconcile event counts and popularity totals after grouping.

### Demonstrate the actual practice-data QA audit

| Step | Synthetic practice result |
|---|---:|
| Raw reaction CSV rows | 25,001 |
| Rows after removing duplicate event ID | 25,000 |
| Unmatched content-ID references | 1 |
| Unmatched reaction types | 2 |
| Missing category after attaching Content | 11 (includes one unmatched content reference) |
| Invalid/missing timestamps | 1 |
| **Clean, joined reaction events** | **24,986** |
| **Rows rejected following event-ID dedup** | **14** |

**Interview subtlety:** These error categories **overlap**. The sum of unmatched IDs, missing categories, missing types and invalid dates is *not* necessarily the number of excluded records. Always calculate excluded rows from the final row count or distinct invalid-row indicators; do not sum overlapping issue counters.

## Stage 3: Engineer the business metrics

For each clean event `i`, the lookup supplies the score `s_i`. For each category `c`,

**Aggregate popularity:**  
`S(c) = Σ score_i` over events whose related content belongs to `c`.

**Reaction count:**  
`N(c) = number of retained reaction event rows in category c`.

**Score per reaction:**  
`S(c) / N(c)`, a mixture/weight diagnostic, *not* engagement rate.

**Distinct reacting posts:**  
`P(c) = nunique(Content ID)` among *retained reaction rows*.

**Points per reacting post:**  
`S(c) / P(c)`. **Beware:** this is not per *all* posted content; posts with zero reactions are not present in the fact table. Use the full Content dimension for that denominator.

**Share of points:**  
`S(c) / Σ_k S(k) × 100%`.

**Monthly score:**  
`S(m) = Σ score_i` over reaction events with timestamp in month `m`.

**Positive reaction share:**  
`# events mapped to positive / # all retained events × 100%`.

## Stage 4: Analyze actual outputs from the synthetic dataset

| Rank | Category | Popularity points | Reaction events | Points share |
|---:|---|---:|---:|---:|
| 1 | animals | 233,200 | 4,629 | 18.62% |
| 2 | science | 159,316 | 3,187 | 12.72% |
| 3 | technology | 141,884 | 2,816 | 11.33% |
| 4 | healthy eating | 137,260 | 2,759 | 10.96% |
| 5 | food | 116,390 | 2,328 | 9.29% |

**Together they account for 62.93% of popularity points** in this generated practice sample.

Additional synthetic observations:

- **Photo** posts account for **689,953** points; video **374,332**, GIF **165,419**, audio **22,522**. A larger total may be partly because more posts of that type exist.
- **Positive** labels account for **21,078 of 24,986 events (84.36%)**, based on lookup labels rather than text classification.
- **October 2025** has **130,728** weighted points in this generated data, the highest observed month.

These are *practice data characteristics*, not verified claims about the real Social Buzz case. The Forage dataset might produce different counts, time periods and rankings.

## Stage 5: Visualize, then make business recommendations

**Page 1, Executive Overview:** Cards for weighted points, event count, distinct reacting posts, categories; chart ranked by category popularity; month trend; format comparison; sentiment breakdown; category slicer.

**Page 2, Content Deep Dive:** Rank normalized `points per reacting post`; compare category event volume; filter to a content format; cards for average points per event and share of positive-labeled reaction events.

**Business recommendations:**

- Pilot more high-scoring category content, but **validate impact through controlled testing**, not an assumed causal lift.
- Experiment with **category × format combinations** because a category's audience may respond differently to photo versus video content.
- Capture **impressions, viewer counts, content age, region and audience cohorts** so future teams can compute rates, not just totals.
- Add data-quality monitoring, uniqueness guarantees and reproducible transformations before scaling analytics pipelines.
- Keep an IPO/big-data audit as a **separate workstream**, requiring security, data governance, reliability, controls and financial processes well beyond this dashboard.

---

# PART B — Your interview speaking script (about 10–15 minutes)

Read conversationally, not mechanically. Adjust first-person verbs to accurately match what **you** personally executed. Do not claim synthetic results are from Accenture's official dataset.

### 1. Project introduction (about 1 minute)

"I built an independent social-media content analytics project inspired by the Accenture North America Data Analytics and Visualization simulation on Forage. The fictional client in the case, Social Buzz, was a fast-growing social platform looking for stronger data-driven business decisions. The core analytical question was to identify the five categories of content with the highest aggregate popularity.

What interested me was that the question initially sounds very simple—just find the top five categories—but it actually involves several important choices: understanding what a reaction represents, defining popularity correctly, handling multiple data tables, validating the joins and then explaining what the resulting rankings can and cannot establish. My project combined Python data cleaning and analysis with a Power BI-style executive dashboard and recommendations for content strategy. For my portfolio reproduction, I used a clearly identified synthetic dataset based on the public three-table structure, rather than asserting that I analyzed proprietary client data."

### 2. Business framing and dataset overview (about 1.5 minutes)

"I started by translating the request into a measurable KPI. In this case, popularity is not simply the number of users or posts. Different reaction types have predefined numeric scores, so aggregate popularity is the sum of reaction scores for events associated with each content category.

To calculate it, I needed three tables. The Content table contained posts, their category and their format, such as photo, video, GIF or audio. The Reactions table contained reaction events, including the content identifier, reaction type and timestamp. And the ReactionTypes table mapped each reaction type to a sentiment label and a numeric score.

The key modeling point was granularity. The Content table had one row per post, whereas Reactions had one row per reaction event. If one post had hundreds of reactions, its content ID could appear hundreds of times in the reaction table. The scoring lookup contained only one definition per reaction type.

That leads to two many-to-one joins: Reactions to Content using the content ID, and Reactions to ReactionTypes using reaction type. I also explicitly renamed the two different 'Type' fields, because one meant content format and the other meant the audience's reaction. Mixing them would give an incorrect analysis."

### 3. Cleaning and joins (about 2 minutes)

"I treated data cleaning as an important analytical step rather than an afterthought. The pipeline checked missing values, inconsistent formatting, duplicated event IDs, timestamps and reference integrity.

For example, if the category names 'Animals', 'animals', and 'animals ' were not standardized, a group-by could split the same logical category into separate results. I normalized the category and reaction-type strings before aggregation.

I also converted the reaction timestamps into a datetime type because the monthly analysis depends on chronological ordering and valid dates. Scores were converted into a numeric type, and I checked that the reaction scoring table had unique reaction types.

One subtle risk is a many-to-many merge. If a lookup table contains duplicate keys and we join it against events, one event could create multiple output rows and artificially increase the calculated popularity score. To guard against that, the pandas merges used many-to-one validation, and I checked that the final event IDs were unique.

In the synthetic practice dataset, there were 25,001 input reaction rows, including a repeated event ID. After deduplication, 25,000 remained. Additional checks flagged an unmatched content ID, an unmapped reaction type, missing category values and an invalid date. Some of those issue flags overlapped, so the final clean event table had 24,986 records—not the result of simply summing all issue counts.

I retained an audit summary so that someone reviewing the report could see how raw rows became validated business data. That is important because if the original records disappear without explanation, executives may question whether the KPI is reliable."

### 4. Core popularity calculation (about 1.5 minutes)

"Once the data was modeled, I calculated aggregate popularity by grouping the enriched reaction events by category and summing their predefined scores.

Mathematically, for a category c, I calculated the sum of scores over all reaction events linked to posts belonging to that category. As a simple example, if a post received one like worth 50 points and one love worth 65 points, that post contributed 115 popularity points. If several posts belonged to the same category, their event scores were added together.

I then ranked the categories in descending order and selected the top five. In my synthetic sample, the five categories were animals, science, technology, healthy eating and food. Together they accounted for about 62.9% of all weighted points in the dataset.

But an important analytical limitation is that total popularity points are affected by how many posts and reactions a category has. So I also calculated event counts, distinct content posts, points per reaction and points per reacting post.

For instance, a large category may rank first simply because it contains many posts, whereas a smaller category might have stronger average engagement. Without impressions, content age and a full posting denominator, I would not interpret the weighted score as a causal or normalized engagement rate."

### 5. Additional content and sentiment analysis (about 1.5 minutes)

"I extended the analysis beyond the top-five ranking to understand the drivers behind the results. First, I compared content formats. The Content table labeled each post as photo, video, GIF or audio. By grouping reaction events according to their linked post format, I could calculate the total score and the number of reacting posts for each format.

In the practice data, photo content generated the largest total score. But my recommendation would not be to declare photos inherently superior. I would first compare the number of posts and impressions to see whether that result reflected exposure or actual engagement quality.

Second, I looked at sentiment. The scoring lookup already included a sentiment tag for each reaction type. So I used those predefined labels to calculate the share of positive, negative and neutral reaction events.

This is worth emphasizing: the project does not train an NLP sentiment model. It simply uses the existing reaction-type metadata. In the synthetic data, about 84.4% of valid events carried a positive label. That summarizes recorded reaction choices, but it doesn't necessarily prove that 84.4% of all users felt positively about the platform.

Finally, I grouped reaction timestamps by year and month. This revealed when engagement events were concentrated, which could inform scheduling analysis. But a spike in one month might be explained by higher posting volume, a campaign or simply the way the sample was generated, so I avoided making unsupported causal claims."

### 6. Power BI dashboard design (about 1.5 minutes)

"For the reporting layer, I created an executive overview with four KPI cards: total weighted popularity, number of reaction events, distinct reacting posts and number of categories represented.

I used a horizontal bar chart to rank categories because comparisons are easier to read when category labels are long. I used a line chart to display popularity over time, since chronological data should appear in a logical sequence. I also included a chart for media-format comparison and a donut visualization to summarize the sentiment distribution.

The interactive element is important. When a stakeholder filters to a content format or category, measures in Power BI should recalculate in the current filter context. In DAX, I would define total popularity as SUM of Score, the number of events as COUNTROWS, and distinct reacting posts using DISTINCTCOUNT of Content ID. For safe ratios such as points per post, I would use DIVIDE to handle a zero denominator.

I kept the reporting table at reaction-event grain so the aggregation logic remained consistent. I also included reconciliation checks so the category scores summed back to the unfiltered total. This helps prevent attractive visualizations from giving misleading business results."

### 7. Recommendations and project limitations (about 1.5 minutes)

"The first recommendation was to prioritize testing content in categories with strong observed popularity, while treating those rankings as a hypothesis rather than proof of future performance.

The second was to examine category-format combinations. For example, within a science category, videos might work better for certain audiences, whereas photos might work better within a food category. That needs a controlled comparison rather than a blanket recommendation.

The third recommendation concerned data infrastructure and measurement. To calculate actual engagement rates, I would want impressions, unique exposed users, posting times, audience segments and experiment assignments. I would also introduce automated data quality checks to make the metric reliable as the system scales.

I made a clear distinction between analyzing content popularity and certifying IPO readiness. The broader Social Buzz case includes questions about data operations and IPO preparation, but these three tables alone cannot establish whether a company meets security, financial reporting, governance or listing requirements.

The biggest thing I learned is that an analytics project is not primarily about making charts. It is about defining business metrics, validating the data model and explaining conclusions at the right level of confidence so that decision makers can act responsibly."

### 8. Closing (about 30 seconds)

"Overall, the project gave me a complete analyst workflow—from turning a stakeholder question into a measurable KPI, through cleaning and joining event data, to building Power BI reporting and presenting recommendations. It is distinct from a machine-learning clustering project because its focus is descriptive business intelligence, metric governance and executive communication."

---

# PART C — Technical interview drill (questions + defensible answers)

**1. Is it a machine learning project?**  
No. It is descriptive analytics and BI. The reaction scores are predefined lookup values, not predictions made by an ML model.

**2. Why do we need three tables?**  
A reaction event alone doesn't contain the post category or reaction score. Category comes from Content; numerical score and sentiment come from ReactionTypes. Joining enriches each event with those attributes.

**3. Why is one post associated with multiple reaction rows?**  
Because each event is recorded separately. That is the fact-table grain. Aggregating reactions per post or category requires a group-by.

**4. What is a foreign key here?**  
`Reactions[Content ID]` references `Content[Content ID]`; `Reactions[Type]` references `ReactionTypes[Type]`.

**5. What is a fact table and a dimension table?**  
A fact records measured events. A dimension describes entities such as content posts or reaction categories. The facts can be sliced by the dimensions.

**6. What does `validate='many_to_one'` accomplish?**  
It checks that every fact row matches no more than one lookup row. Without it, duplicates in a dimension can multiply event rows and inflate sums.

**7. Why not join on `User ID`?**  
Because the business question is about content categories. User IDs in content and reactions can represent different roles (content authors versus reacting users); joining them would usually be semantically wrong and could create a many-to-many explosion.

**8. What is the biggest ambiguity in 'most popular category'?**  
Whether it means raw reaction count, weighted score, unique reactors, impressions-adjusted engagement rate or something else. We need a metric definition before calculating rankings. The simulation uses weighted reaction scores.

**9. Why can score and event count rankings differ?**  
A category with fewer high-scoring reaction types can have more points than a category with many low-scoring reactions.

**10. What does a missing Content ID imply?**  
You can't allocate that reaction to a known category. Investigate the pipeline's referential integrity; exclude it from category analysis if unresolved, but report the volume.

**11. Should a missing reaction score equal zero?**  
Not automatically. Zero has substantive meaning as a score and would bias totals. An unknown reaction type must be examined or excluded with an audit record.

**12. Why retain missing User ID rows?**  
Because customer identity is not required for category-level score aggregation. Dropping otherwise valid events would reduce totals unnecessarily.

**13. What is the difference between sentiment and sentiment analysis by ML?**  
We have predefined labels in the reaction lookup. An NLP model would infer sentiment from free text. This project doesn't do that.

**14. Is points per post a true engagement rate?**  
No. It lacks an impression denominator and, in a reaction-only fact table, excludes posts with no reaction events. It is at best weighted points per *reacting* post.

**15. How to calculate engagement rate properly?**  
Define the event numerator (e.g., likes + comments + shares) and divide by impressions or reach under matched time windows and population definitions. Handle repeated events and the desired user-level metric explicitly.

**16. What does `COUNTROWS` do in Power BI?**  
Counts rows in the filtered table. In this model, that equals the number of retained reaction events under the current slicers.

**17. What is DAX filter context?**  
Filters from slicers, visual axes and interactions determine which data rows contribute to a measure. The same `SUM(Score)` measure can calculate total points or points for only videos without editing its definition.

**18. Why `DIVIDE` instead of `/`?**  
`DIVIDE` conveniently returns blank or a specified fallback when the denominator is zero, avoiding problematic divide-by-zero behavior.

**19. Why use a bar chart for categories?**  
Because it's easy to compare numeric magnitudes across labeled groups; long category names are especially readable horizontally.

**20. Why use a line chart for time?**  
Because chronological ordering and movement between periods matter. A line emphasizes temporal change.

**21. What was the hardest part?**  
Designing a metric and validating join cardinality. Without those, ranking data could look plausible but be mathematically wrong.

**22. How would you make this production-grade?**  
Schema contracts, automated null/duplicate/referential integrity tests, versioned mapping tables, incremental ingestion, BI lineage, observability, a separate calendar dimension and maintained data privacy controls.

**23. Could you calculate user retention or a customer segment from these tables?**  
Not faithfully from this analytics model alone. You would need stable, permissioned user identities, cohort definitions, full activity windows and retention logic. This project intentionally avoids duplicating an RFM/K-Means project.

**24. Did the analysis prove that business KPIs improved?**  
No. It generates decision-support evidence and testable hypotheses. A measured impact requires implementation with appropriate experimental or quasi-experimental evaluation.

**25. Why not claim you 'worked at Accenture'?**  
Because an independent case reproduction or even a Forage job simulation does not constitute employment at Accenture. Describe the work as a self project unless you've actually completed the official Forage simulation, and even then label it a simulation.

---

# PART D — Compact interview checklist

Before putting this on the resume, make sure you can answer, without opening the code:

- What does one row represent in Content vs Reactions?
- What are the two join keys, and which keys must be unique?
- What is the difference between `content_type` and `reaction_type`?
- How is one category's popularity score computed by hand?
- Why did 25,001 practice rows become 24,986 clean rows?
- Why must missing issue counts not simply be summed?
- Why do totals not establish causal content preference?
- What is the difference between positive sentiment labels and NLP classification?
- Which Power BI slicer changes which DAX measures?
- How do you explain a recommendation without inventing uplift, revenue or impressions?

The notebook's `data/processed/quality_report.json` and eight summary tables allow you to check every numerical claim. Replace synthetic inputs with official CSVs and rerun before discussing official simulation findings.
