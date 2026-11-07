# Social Buzz — Data Analytics & Visualization Portfolio Project

**Type:** Independent project inspired by the Accenture North America Data Analytics & Visualization Forage job simulation.  
**Client:** Social Buzz — *fictional case-study platform*.  
**Data:** **SYNTHETIC** and deterministic practice files with the same core three-table structure used in the public case study. No real user data.  
**Status:** Jupyter notebook has been executed and its calculations checked. Power BI PBIP source is generated but **not verified by opening in Microsoft Power BI Desktop** in this environment. Standalone HTML dashboard is generated and embeds Plotly, although a browser test was blocked by this environment's navigation restrictions.

## Your project files

- `Social_Buzz_End_to_End_Analytics.ipynb`: clean, fully executable, explanatory notebook (29 cells).
- `Social_Buzz_Executed.ipynb`: same notebook with charts, tables and output saved.
- `data/raw/Content.csv`, `Reactions.csv`, `ReactionTypes.csv`: synthetic source tables; replace with the official files if you enroll in the actual Forage exercise.
- `data/processed/fact_reactions.csv`: 24,986 cleaned reaction-event rows for immediate Power BI import.
- `data/processed/{category_summary,top5_categories,monthly_trend,sentiment_summary,format_summary,top_posts,category_format}.csv`: outputs for validation and direct import.
- `data/processed/quality_report.json`: transparent join/cleaning counts.
- `figures/*.png`: plots created by the notebook.
- `Social_Buzz_Interactive_Dashboard.html`: interactive, standalone dashboard. Open in Chrome/Edge, with dropdown filters. Chart library and data are embedded; no internet should be needed.
- `powerbi/Social_Buzz_Dashboard/Social_Buzz_Dashboard.pbip`: editable **Power BI Project** entry point. **Not** the same file type as a `.pbix` binary.
- `POWER_BI_SETUP_AND_DAX.md`: exact instructions for Power BI Desktop, rebuilding if necessary, and measures.
- `INTERVIEW_MASTER_GUIDE.md`: explanations, 10–15 minute speaking script, and technical questions.
- `requirements.txt`: Python packages.

## Run it in VS Code / Jupyter / Colab

**Easiest method: download the ZIP, extract it, and keep the folder structure intact.**

1. Open a terminal at the extracted `Social_Buzz_Project` folder.
2. If needed run `python -m pip install -r requirements.txt`.
3. Run `jupyter notebook` or open `Social_Buzz_End_to_End_Analytics.ipynb` using VS Code's Notebook view.
4. Select a Python kernel and run all cells, top to bottom. The notebook re-creates the `data/processed` tables and plots.
5. Open `Social_Buzz_Interactive_Dashboard.html` separately in a browser to practice explaining the plots.

Power BI Desktop is Windows software: see `POWER_BI_SETUP_AND_DAX.md` for the `.pbip` project and the clean import fallback.

### Data provenance and real Forage CSV option

The original three tables from the actual simulation are linked through public community examples, such as:
- https://github.com/iSandeep07/Accenture-Data-Analytics-and-Visualization-
- https://github.com/minhaj-313/-Accenture-Data-Analytics-Visualization-Virtual-Internship

They are third-party mirrors, **not independently verified original source files**. For the most authentic version, enroll in Forage and obtain the official three tables. Replace the files in `data/raw/` **using the exact base names** and rerun the notebook. Confirm the actual column headers. If your download has different headers, adjust the rename mappings in section 4 of the notebook. Don't relabel synthetic results as official data or suggest Accenture employed you because you completed this project.

## What this case does and does not establish

**Does establish:** Ability to identify necessary datasets, profile and clean data, join many events to lookup tables without inflating rows, define defensible business KPIs, analyze top categories, examine time trends and sentiment mappings, produce visualizations and recommendations.

**Does not establish:** Real data from a live customer; independent sentiment model training; a measured campaign lift; one-click IPO readiness; actual revenue or retention; audited corporate governance; completion of Accenture's Forage simulation; verified PBIX output. This project focuses on a demonstration of the *content category analysis* workstream.

## Synthetic example results (this exact build, seed 2026)

- Raw reaction-event rows: **25,001**, including a deliberately duplicated event.
- Rows after event-ID deduplication: **25,000**.
- Clean matched rows: **24,986**, after excluding 14 rows with missing/unmatched data (counted in `quality_report.json`).
- Weighted popularity points: **1,252,226**.
- Top five scored categories: **animals, science, technology, healthy eating, food**.
- Top five cumulative share of points: **62.93%**.

These outputs are simulated, not the official Accenture rankings or client facts. Re-run on actual source data before quoting any numbers from the original simulation.

## A recommended accurate resume description after you have personally rebuilt and reviewed the project

**Social Media Content Analytics | Power BI & Python (Self Project)**  
- Analyzed reaction-level social-media engagement data, joining content, reaction and scoring tables to identify high-performing content categories.  
- Built Python data-quality checks and Power BI-ready reporting datasets; visualized weighted popularity, content-format performance, sentiment and time trends.  
- Developed a simulated client-facing dashboard and recommended content experiments and stronger engagement measurement practices.

If you do not complete the enrolled Forage programme, avoid calling it "Accenture virtual internship" or saying you worked at Accenture. Use "Accenture–Forage-inspired self project" instead.
