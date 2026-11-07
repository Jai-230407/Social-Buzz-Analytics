import nbformat as nbf
from pathlib import Path

root=Path(__file__).parent
nb=nbf.v4.new_notebook(); nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}}
cells=[]
def md(s): cells.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): cells.append(nbf.v4.new_code_cell(s.strip()))

md('''# Social Buzz | Content Popularity & Business Insights
### Accenture–Forage-inspired end-to-end data analytics case study

**Purpose:** Prepare a defensible portfolio project: business framing → data understanding → cleaning → joins → analytics → visualizations → executive recommendations.

> **DATA PROVENANCE — PLEASE READ:** The data in this package are **deterministically generated synthetic teaching data** using the same three-table design described in public Accenture–Forage Social Buzz walkthroughs. They are **not** a download of the official Forage task files, not verified client results, and not evidence of completing the Accenture simulation. If you get original `Content.csv`, `Reactions.csv`, and `ReactionTypes.csv` from your own enrollment, replace the three files in `data/raw/` and rerun. All actual findings in this notebook refer to the dataset currently loaded.

**Official task sequence:** Project Understanding → Data Cleaning & Modeling → Data Visualization & Storytelling → Present to the Client.

**Client scenario:** Social Buzz needs insights into the **five content categories with the largest aggregate popularity score**, as part of a wider business conversation about data operations and IPO readiness. This notebook implements the **content analytics** workstream; it does *not* pretend to perform a full enterprise data audit or certify IPO readiness.

**Sources:** [Forage](https://www.theforage.com/), [public field explanations](https://github.com/minhaj-313/-Accenture-Data-Analytics-Visualization-Virtual-Internship), [original schema mirrors](https://github.com/iSandeep07/Accenture-Data-Analytics-and-Visualization-).''')

md('''## 1. Business questions and metric definitions

**Q1:** Which content categories produce the most **aggregate engagement points**?  
**Q2:** Do the top-ranked categories have high **reaction counts** or merely high-scoring reactions?  
**Q3:** Which content formats (photo/video/GIF/audio) perform well?  
**Q4:** What sentiment mix is associated with the reactions?  
**Q5:** How do recorded reactions vary by month?  

In this case, each reaction `Type` maps to a predetermined numeric `Score` in `ReactionTypes.csv`. **Popularity Score of a Category** is

$$S_c = \\sum_{i: \\mathrm{category}_i=c} s_i.$$

It is a **weighted reaction sum**, not number of unique people, view-through rate, platform-wide reach, revenue, or a machine-learning prediction. Repeated reactions contribute separately unless the business specifies otherwise. Category-level sums can reward categories with more posts: examine **points per content item** as a complementary descriptive metric. Without impressions/exposure and posting time normalization, do not claim one category is intrinsically more attractive to users.''')

code('''from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

# Works from extracted zip/project folder. Run notebook from the project root.
ROOT = Path.cwd()
if not (ROOT / 'data' / 'raw').exists() and (ROOT / 'Social_Buzz_Project' / 'data' / 'raw').exists():
    ROOT = ROOT / 'Social_Buzz_Project'
RAW = ROOT / 'data' / 'raw'
PROCESSED = ROOT / 'data' / 'processed'
FIGURES = ROOT / 'figures'
PROCESSED.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
print('Project folder:', ROOT.resolve())
print('Raw CSV files:', [p.name for p in RAW.glob('*.csv')])''')

md('''## 2. Data understanding: three related tables

| Table | Unit of observation | Join key | Core fields | Relationship |
|---|---|---|---|---|
| `Content.csv` | A content post | Content ID | Type = **format**, Category | One post → many reactions |
| `Reactions.csv` | A reaction event | Content ID / reaction Type | Reaction Type, Datetime | Many events → one post |
| `ReactionTypes.csv` | A score mapping | Reaction Type | Sentiment, Score | Many events → one reaction definition |

**Critical interview trap:** `Type` in **Content** means photo/video/GIF/audio; `Type` in **Reactions** means like/love/hate etc. Rename both before joining. Neither `User ID` nor content author names are required to answer the top-category question. Avoid merging by user ID; that would cause an incorrect many-to-many join.''')

code('''required = ['Content.csv', 'Reactions.csv', 'ReactionTypes.csv']
missing = [name for name in required if not (RAW/name).exists()]
if missing:
    raise FileNotFoundError(f'Missing files: {missing}. Use the complete ZIP or supply your own official Forage CSVs in data/raw.')
content_raw = pd.read_csv(RAW/'Content.csv')
reactions_raw = pd.read_csv(RAW/'Reactions.csv')
reaction_types_raw = pd.read_csv(RAW/'ReactionTypes.csv')
for name, frame in [('Content',content_raw), ('Reactions',reactions_raw), ('Reaction Types',reaction_types_raw)]:
    print(f'{name}: {len(frame):,} rows x {len(frame.columns)} columns | {frame.columns.tolist()}')
    display(frame.head(3))''')

md('''## 3. Data quality profiling — inspect, don't blindly delete

Checks include missing join keys, duplicate event IDs, dates that cannot be parsed, non-numeric scores, and category labels with inconsistent casing/quotes. Missing `User ID` does **not** invalidate a reaction when we are studying category popularity.

The supplied synthetic sample intentionally contains a few broken records for training; a real dataset requires an approved handling policy and an audit trail.''')

code('''for label,frame in [('Content',content_raw),('Reactions',reactions_raw),('ReactionTypes',reaction_types_raw)]:
    print('\\n',label,'— missing values')
    display(frame.isna().sum().rename('null_count').to_frame())
    print('Exact duplicate rows:',frame.duplicated().sum())
    if 'Reaction ID' in frame.columns:
        print('Duplicate reaction event IDs:',frame['Reaction ID'].duplicated().sum())''')

md('''## 4. Clean each table separately

- Drop CSV export index columns (e.g. `Unnamed: 0`) only when they are truly non-business identifiers.
- Standardize keys to trimmed strings, normalize case and stray quotes in categories/reaction names.
- Preserve original **content format** and **reaction type** in separate fields.
- Validate reaction-score mapping: **one distinct row per reaction type** (otherwise a join multiplies facts).
- Remove only records that cannot contribute to the specified metric: missing/unmatched content ID, unknown reaction type, invalid date for time analysis, or missing category. Keep a count of losses.
- **Do not** fill missing scores with zero; that silently changes the business definition. Investigate and exclude/report unmatched mappings.

The row grain after merging remains **one reaction event per row**.''')

code('''def drop_export_indexes(frame):
    return frame.loc[:, ~frame.columns.str.match(r'^Unnamed:')].copy()

def norm_text(series):
    # Pandas nullable strings maintain true missing values.
    return series.astype('string').str.strip()

def norm_category(series):
    return norm_text(series).str.replace('"','',regex=False).str.replace("'",'',regex=False).str.strip().str.lower()

content = drop_export_indexes(content_raw)
content = content.rename(columns={'Content ID':'content_id', 'Type':'content_type', 'Category':'category'})
assert {'content_id','content_type','category'}.issubset(content.columns)
content = content[['content_id','content_type','category']].copy()
content['content_id'] = norm_text(content['content_id'])
content['content_type'] = norm_text(content['content_type']).str.lower()
content['category'] = norm_category(content['category'])
content = content.dropna(subset=['content_id']).drop_duplicates(subset=['content_id'],keep='first')

reaction_types = drop_export_indexes(reaction_types_raw)
reaction_types = reaction_types.rename(columns={'Type':'reaction_type', 'Sentiment':'sentiment', 'Score':'score'})
assert {'reaction_type','sentiment','score'}.issubset(reaction_types.columns)
reaction_types = reaction_types[['reaction_type','sentiment','score']].copy()
reaction_types['reaction_type'] = norm_text(reaction_types['reaction_type']).str.lower()
reaction_types['sentiment'] = norm_text(reaction_types['sentiment']).str.lower()
reaction_types['score'] = pd.to_numeric(reaction_types['score'],errors='coerce')
reaction_types = reaction_types.dropna(subset=['reaction_type','score']).drop_duplicates(subset=['reaction_type'],keep='first')
assert reaction_types['reaction_type'].is_unique

reactions = drop_export_indexes(reactions_raw)
reactions = reactions.rename(columns={'Reaction ID':'reaction_id','Content ID':'content_id','Type':'reaction_type','Datetime':'datetime'})
assert {'content_id','reaction_type','datetime'}.issubset(reactions.columns)
if 'reaction_id' not in reactions.columns:
    # A sequence key represents row identity, not deduplication evidence.
    reactions['reaction_id'] = [f'ROW-{i:08d}' for i in range(len(reactions))]
reactions = reactions[['reaction_id','content_id','reaction_type','datetime']].copy()
reactions['reaction_id']=norm_text(reactions['reaction_id'])
reactions['content_id']=norm_text(reactions['content_id'])
reactions['reaction_type']=norm_text(reactions['reaction_type']).str.lower()
reactions['datetime']=pd.to_datetime(reactions['datetime'],errors='coerce')
# If a stable reaction ID exists, duplicates are duplicates of the event.
if 'Reaction ID' in reactions_raw.columns:
    reactions = reactions.drop_duplicates(subset=['reaction_id'],keep='first')
print('Unique content IDs:',content['content_id'].nunique())
print('Known reaction types:',reaction_types['reaction_type'].nunique())
print('Reaction events after ID deduplication:',len(reactions))''')

md('''## 5. Data modeling: two many-to-one joins

`Reactions` is the **fact table**; `Content` and `ReactionTypes` are lookup/dimension tables.

```text
Content [content_id]  1  ──────────────── *  Reactions [content_id]
ReactionTypes [reaction_type]  1  ─────── *  Reactions [reaction_type]
```

We first enrich each reaction with its post's category/format, then attach the reaction's weighted score. `validate='many_to_one'` makes pandas raise an error if the lookup contains duplicate keys—this prevents accidentally inflating scores by row multiplication. Preserve unmatched-join counts for QA.''')

code('''stage1 = reactions.merge(content, on='content_id',how='left',validate='many_to_one',indicator='_content_join')
stage2 = stage1.merge(reaction_types,on='reaction_type',how='left',validate='many_to_one',indicator='_score_join')
qa = {
    'raw_reaction_rows': int(len(reactions_raw)),
    'after_reaction_id_dedup': int(len(reactions)),
    'unmatched_content_ids': int((stage2['_content_join']!='both').sum()),
    'unmatched_reaction_types': int((stage2['_score_join']!='both').sum()),
    'missing_category_after_join': int(stage2['category'].isna().sum()),
    'invalid_datetimes': int(stage2['datetime'].isna().sum())
}
display(pd.Series(qa,name='row_count').to_frame())
required_fields=['content_id','category','content_type','reaction_type','score','datetime']
clean = stage2.dropna(subset=required_fields).copy()
clean['score']=clean['score'].astype(float)
clean['month']=clean['datetime'].dt.to_period('M').astype(str)
clean['date']=clean['datetime'].dt.strftime('%Y-%m-%d')
clean['year']=clean['datetime'].dt.year.astype(int)
clean['month_name']=clean['datetime'].dt.strftime('%b')
clean=clean[['reaction_id','content_id','category','content_type','reaction_type','sentiment','score','datetime','date','month','month_name','year']]
qa['clean_reaction_rows']=int(len(clean))
qa['excluded_after_joins']=int(len(reactions)-len(clean))
assert clean['reaction_id'].is_unique
assert clean[['content_id','category','score','datetime']].notna().all().all()
print('Clean fact-table rows:',len(clean))
display(clean.head())''')

md('''## 6. Main deliverable — top five content categories

For category $c$, score is $S_c=\\sum_{i\\in c} s_i$. The output ranks **total score**, not raw reaction count. We also compute `reaction_events`, `unique_posts`, `score_per_reaction`, and `score_per_post` for context. A high `score_per_post` does not establish causal superiority because impressions, post age and audience size are unavailable.''')

code('''categories = (clean.groupby('category',as_index=False)
              .agg(popularity_score=('score','sum'),reaction_events=('reaction_id','size'),unique_posts=('content_id','nunique')))
categories['score_per_reaction']=categories['popularity_score']/categories['reaction_events']
categories['score_per_post']=categories['popularity_score']/categories['unique_posts']
categories['share_of_points_pct']=100*categories['popularity_score']/categories['popularity_score'].sum()
categories=categories.sort_values(['popularity_score','category'],ascending=[False,True]).reset_index(drop=True)
top5=categories.head(5).copy()
display(top5.round(2))
print('Top category:',top5.iloc[0]['category'])
print('Top-five combined share of points: %.1f%%' % top5['share_of_points_pct'].sum())''')

code('''plt.figure(figsize=(10,5.4))
ordered=top5.sort_values('popularity_score')
plt.barh(ordered['category'],ordered['popularity_score'],color='#0F766E')
plt.title('Top five categories • aggregate reaction score',loc='left',fontweight='bold')
plt.xlabel('Sum of weighted reaction scores (points)')
plt.grid(axis='x',alpha=.18)
plt.tight_layout();plt.savefig(FIGURES/'01_top_categories.png',dpi=180,bbox_inches='tight');plt.show()''')

md('''## 7. Reaction counts vs weighted popularity

A reaction event is counted once. A popularity point equals the **numeric weight** of its reaction type. Two categories can have the same number of events but different total popularity points if their reaction mixes differ.

- Ranking by `reaction_events` answers: "Where were most reaction events recorded?"
- Ranking by `popularity_score` answers: "Where did the largest cumulative weighted score arise?"

Importantly, `reaction_events` is **not** unique viewers or unique users; this schema can contain repeated events per user.''')

code('''comparison=categories[['category','reaction_events','popularity_score','score_per_reaction','unique_posts','score_per_post']].copy()
display(comparison.head(10).round(2))
fig,axs=plt.subplots(1,2,figsize=(13,4.7))
plot_data=comparison.head(8).iloc[::-1]
axs[0].barh(plot_data['category'],plot_data['reaction_events'],color='#2563EB');axs[0].set_title('Number of reactions')
axs[1].barh(plot_data['category'],plot_data['popularity_score'],color='#0F766E');axs[1].set_title('Sum of popularity scores')
for ax in axs: ax.grid(axis='x',alpha=.15)
plt.tight_layout();plt.savefig(FIGURES/'02_count_vs_score.png',dpi=180,bbox_inches='tight');plt.show()''')

md('''## 8. How content formats perform

A **content_type** (photo, video, GIF, audio) is the format of the post, not its category. The same category may contain multiple formats. Count events and total points by format. Be careful with "best-performing": a larger total may simply reflect that more of that format was posted.''')

code('''formats=(clean.groupby('content_type',as_index=False)
         .agg(reactions=('reaction_id','size'),popularity_score=('score','sum'),posts=('content_id','nunique'))
         .sort_values('popularity_score',ascending=False))
formats['score_per_post']=formats['popularity_score']/formats['posts']
display(formats.round(2))
plt.figure(figsize=(8,4.7));plt.bar(formats['content_type'],formats['popularity_score'],color='#6366F1')
plt.title('Popularity points by content format',loc='left',fontweight='bold');plt.ylabel('Points');plt.tight_layout()
plt.savefig(FIGURES/'03_formats.png',dpi=180,bbox_inches='tight');plt.show()''')

md('''## 9. Sentiment analysis — but not NLP

The `ReactionTypes` lookup already labels reaction types as positive / negative / neutral. This is a **rule-based category lookup**, not an ML sentiment classifier. If a user chooses "like", the row inherits its preassigned sentiment; there is no unstructured text sentiment inference.

Count reactions by label to describe composition. Total positive reaction scores reflect the chosen weights, not independently calibrated emotional intensity.''')

code('''sentiment=(clean.groupby('sentiment',as_index=False).agg(reactions=('reaction_id','size'),popularity_score=('score','sum')))
sentiment['reaction_pct']=100*sentiment['reactions']/sentiment['reactions'].sum()
display(sentiment.round(2))
fig,ax=plt.subplots(figsize=(7.5,4.7))
colors=[{'positive':'#0F766E','negative':'#DC2626','neutral':'#9CA3AF'}.get(x,'#7C3AED') for x in sentiment['sentiment']]
ax.bar(sentiment['sentiment'],sentiment['reaction_pct'],color=colors)
ax.set_ylabel('% of reaction events');ax.set_title('Reaction sentiment mix',loc='left',fontweight='bold')
plt.tight_layout();plt.savefig(FIGURES/'04_sentiment.png',dpi=180,bbox_inches='tight');plt.show()''')

md('''## 10. Month-by-month activity trends

Use the **reaction timestamp**, not content-creation time (not supplied), to understand when engagements happened. Group by `YYYY-MM` rather than month names alone, so two different years do not get mixed and chronological sorting works correctly. Without an exposure denominator or complete observation windows, trends are descriptive, not evidence of algorithmic causation.''')

code('''monthly=clean.groupby('month',as_index=False).agg(reactions=('reaction_id','size'),popularity_score=('score','sum'))
monthly=monthly.sort_values('month')
display(monthly)
plt.figure(figsize=(11,4.6));plt.plot(monthly['month'],monthly['popularity_score'],marker='o',color='#2563EB',linewidth=2)
plt.xticks(rotation=45);plt.ylabel('Weighted popularity points');plt.title('Monthly popularity trend',loc='left',fontweight='bold');plt.grid(alpha=.2)
plt.tight_layout();plt.savefig(FIGURES/'05_monthly.png',dpi=180,bbox_inches='tight');plt.show()''')

md('''## 11. Additional analytical cuts (portfolio extensions)

**Top content posts:** Which individual posts had the highest total scored interactions? **Category × format:** Within which categories did photo/video/GIF gather most observed points? Neither analysis appears as a mandatory machine learning task; these are simple descriptive extensions useful for a more substantial Power BI dashboard.''')

code('''top_posts=(clean.groupby(['content_id','category','content_type'],as_index=False)
          .agg(reactions=('reaction_id','size'),popularity_score=('score','sum'))
          .sort_values('popularity_score',ascending=False).head(15))
category_format=(clean.groupby(['category','content_type'],as_index=False)
                 .agg(reactions=('reaction_id','size'),popularity_score=('score','sum')))
display(top_posts.head(10));display(category_format.sort_values('popularity_score',ascending=False).head(10))''')

md('''## 12. Reliability checks, leakage and interpretation

- **Join multiplication check:** every kept reaction should appear once, never once per duplicate lookup key.
- **Score reconciliation:** sum of category points equals the complete fact table's weighted score.
- **Count reconciliation:** category-level event counts equal total clean reaction events.
- **Data lineage:** all exported files derive from the *same* cleaned dataset.
- **Scope guardrails:** sample engagement **is not 500 million users**, true audience exposure, unique reach, retention, causal engagement lift, revenue, or an IPO readiness assessment. This analysis does not train any ML model.
- **Business decision:** prioritizing categories should consider totals **and** normalized performance before scheduling experiments.''')

code('''assert len(clean) <= len(reactions)
assert clean['reaction_id'].nunique() == len(clean)
assert np.isclose(categories['popularity_score'].sum(),clean['score'].sum())
assert categories['reaction_events'].sum() == len(clean)
assert set(clean['reaction_type']).issubset(set(reaction_types['reaction_type']))
assert set(clean['content_id']).issubset(set(content['content_id']))
assert top5['popularity_score'].is_monotonic_decreasing
print('ALL CHECKS PASSED')
print('Rows in original Reactions CSV:',len(reactions_raw))
print('Rows in validated analytics table:',len(clean))
print('Total measured popularity points:',f"{clean['score'].sum():,.0f}")''')

md('''## 13. Export consistent tables for Power BI

**`fact_reactions.csv`** contains one row per cleaned reaction event with category, content format, sentiment, score and time fields; import this single table if you want a beginner-friendly Power BI dashboard. It is already denormalized by the notebook's **validated joins**.

**Why one table?** The raw three-table relationship is important to understand, but a single cleaned event table is easier to use for a report. In a production dimensional model, you might keep separate Content, ReactionTypes, Calendar and Facts tables instead.

The files below are automatically refreshed when you rerun the notebook. If you replace input CSVs with official task data, the dashboard values will update after Power BI data refresh/re-import.''')

code('''out_fact = clean.rename(columns={
    'reaction_id':'Reaction ID','content_id':'Content ID','category':'Category',
    'content_type':'Content Type','reaction_type':'Reaction Type',
    'sentiment':'Sentiment','score':'Score','datetime':'Datetime',
    'date':'Date','month':'Month','month_name':'Month Name','year':'Year'
})
out_fact.to_csv(PROCESSED/'fact_reactions.csv',index=False)
categories.to_csv(PROCESSED/'category_summary.csv',index=False)
top5.to_csv(PROCESSED/'top5_categories.csv',index=False)
monthly.to_csv(PROCESSED/'monthly_trend.csv',index=False)
sentiment.to_csv(PROCESSED/'sentiment_summary.csv',index=False)
formats.to_csv(PROCESSED/'format_summary.csv',index=False)
top_posts.to_csv(PROCESSED/'top_posts.csv',index=False)
category_format.to_csv(PROCESSED/'category_format.csv',index=False)
qa['total_popularity_points']=float(clean['score'].sum())
qa['top_category']=str(top5.iloc[0]['category'])
qa['top5_score_share_pct']=float(top5['share_of_points_pct'].sum())
(PROCESSED/'quality_report.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
print('Saved outputs:')
for p in sorted(PROCESSED.iterdir()): print(' •',p.name,p.stat().st_size,'bytes')''')

md('''## 14. Executive recommendations (suitably qualified)

1. **Prioritize a controlled content experiment** in high-scoring categories rather than declaring causality from rankings. Use engagement-per-impression and comparable posting windows.
2. **Test content formats within each category:** photo/video mix could vary significantly; run A/B tests and compare engagement rate, not only total points.
3. **Improve measurement readiness:** capture impressions, unique exposed users, content age, actual engagement rate and retention so strategic decisions are based on denominators.
4. **Prepare for larger-scale analytics:** establish data contracts, unique event IDs, referential integrity checks, reliable ingestion SLAs and repeatable dashboards; a dashboard is not a complete IPO data audit.

### 30-second interview summary

"I developed an Accenture–Forage-inspired Social Buzz content analytics case. I structured the problem around finding the top five categories by aggregate popularity score, used three related datasets—posts, reactions, and a lookup of reaction scores—and built a validated many-to-one data pipeline. I cleaned missing keys and inconsistent labels, prevented join duplication, ranked categories by weighted scores, and created Power BI-ready datasets and additional visualizations for trends, sentiment and content formats. I then translated the analysis into recommendations for content testing and more reliable engagement measurement. The dataset used for this portfolio build is synthetic, rather than actual Social Buzz client data."''')

nb.cells=cells
nbf.write(nb,root/'Social_Buzz_End_to_End_Analytics.ipynb')
print('Notebook created with',len(cells),'cells')
