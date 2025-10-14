---
title: "NOS-TLPlot: A specialized Python tool for visualizing Newcastle-Ottawa Scale risk-of-bias assessments"
tags:
  - Python
  - systematic reviews
  - meta-analysis
  - Newcastle-Ottawa Scale
  - risk-of-bias
  - evidence synthesis
authors:
  - name: Vihaan Sahu
    orcid: 0009-0008-5790-1818
    affiliation: 1
    corresponding: true
affiliations:
  - index: 1
    name: Independent Researcher, India
date: 13 October 2025
bibliography: paper.bib
---

# Summary

NOS-TLPlot is an open-source Python package designed specifically for visualizing **Newcastle–Ottawa Scale (NOS)** risk-of-bias assessments in systematic reviews and meta-analyses. The Newcastle-Ottawa Scale is the most widely used tool for evaluating the quality of non-randomized studies, but creating publication-ready visualizations has traditionally required significant manual effort and specialized technical skills.

This package addresses this critical gap by providing an automated, reproducible framework that transforms NOS star ratings into **11 distinct, publication-ready visualization types**. These include traditional traffic-light plots, radar charts, heatmaps, and specialized formats like dot profiles and lollipop charts. Each visualization is optimized specifically for NOS data structure, ensuring accurate representation of domain-level risk-of-bias assessments across multiple studies.

NOS-TLPlot offers dual interface options: an interactive Streamlit web application for exploratory analysis and a command-line interface for batch processing and workflow integration. The tool automatically converts numerical NOS scores (0-9 stars) into standardized risk categories (Low/Moderate/High) following established guidelines, ensuring consistency across visualizations.

By enabling transparent, reproducible visual summaries, NOS-TLPlot helps systematic reviewers, meta-analysts, and clinical guideline developers communicate study quality effectively to diverse audiences, from specialist researchers to policy makers and clinicians.

# Statement of need

Systematic reviews and meta-analyses of observational studies rely heavily on quality assessment using the Newcastle-Ottawa Scale to evaluate risk of bias. However, the process of creating visual summaries from NOS assessments remains predominantly manual, inconsistent, and time-consuming. Researchers typically face three major challenges:

1. **Technical barriers**: Creating professional visualizations requires programming expertise in tools like Python or R
2. **Time constraints**: Manual figure creation in graphical software can take hours per review
3. **Inconsistency**: Different researchers may create visually dissimilar plots from identical data

Existing solutions are either too general (requiring extensive customization) or too limited (offering only basic traffic-light plots). Popular systematic review tools like RevMan provide limited NOS visualization options, while general plotting libraries demand substantial coding effort.

NOS-TLPlot specifically addresses these challenges by providing:

* A **domain-specific visualization framework** optimized for NOS data structure
* **11 specialized plot types** catering to different analytical perspectives
* **Automated risk categorization** following standard NOS interpretation guidelines
* **Dual interface design** accommodating both interactive exploration and batch processing
* **Publication-ready output** in multiple vector and raster formats

The package fills a critical niche in the evidence synthesis ecosystem, complementing existing tools like ROBVIS [@mcguinness2021] for randomized trials and risk-of-bias visualization. While ROBVIS focuses on Cochrane risk-of-bias tools, NOS-TLPlot specializes exclusively in Newcastle-Ottawa Scale assessments for observational studies.

Researchers using NOS-TLPlot can rapidly generate consistent, high-quality visualizations, standardize reporting across projects and teams, and reduce errors introduced by manual figure creation. The tool is particularly valuable for systematic reviews involving multiple non-randomized studies, where clear communication of study quality is essential for interpreting meta-analysis results.

# Visualization Types

NOS-TLPlot generates 11 distinct visualization types, each offering unique perspectives on NOS assessment data:

| Visualization Type | Primary Use Case | Key Features |
|-------------------|------------------|--------------|
| Traffic-light Plot | Standard risk presentation | Color-coded domains, intuitive interpretation |
| Radar Chart | Multi-domain comparison | Circular display of all domains per study |
| Heatmap | Pattern identification | Color intensity shows bias levels across studies |
| Dot Profile | Compact overview | Minimalist representation of domain scores |
| Donut Chart | Proportion visualization | Circular display of risk category distribution |
| Lollipop Plot | Score comparison | Combines categorical and numerical representation |
| Stacked Area Chart | Distribution analysis | Shows risk proportions across domains |
| Pie Chart | Quick summary | Basic proportional representation |
| Line Ordered Plot | Sequential analysis | Connects domain scores within studies |
| Table View | Detailed examination | Color-coded tabular data presentation |
| Thematic Radar | Styled comparison | Theme-adapted radar visualization |

# Input Data Format

NOS-TLPlot requires input data in a structured format with specific columns corresponding to NOS domains:

**Table 1: Required input columns and specifications**

| Column Name | Description | Valid Range | Domain Category |
|-------------|-------------|-------------|-----------------|
| Author, Year | Study identifier | Text | Metadata |
| Representativeness | Selection bias assessment | 0–1 | Selection |
| Non-exposed Selection | Selection of comparison group | 0–1 | Selection |
| Exposure Ascertainment | Exposure measurement | 0–1 | Exposure |
| Outcome Absent at Start | Baseline outcome status | 0–1 | Exposure |
| Comparability (Age/Gender) | Confounding control | 0–2 | Comparability |
| Comparability (Other) | Additional confounding control | 0–2 | Comparability |
| Outcome Assessment | Outcome measurement | 0–1 | Outcome |
| Follow-up Length | Adequacy of follow-up duration | 0–1 | Outcome |
| Follow-up Adequacy | Completeness of follow-up | 0–1 | Outcome |
| Total Score | Sum of domain scores | 0–9 | Summary |
| Overall RoB | Risk of bias category | Low/Moderate/High | Summary |

**Example input data structure:**
```csv
Author,Year,Representativeness,Non-exposed Selection,Exposure Ascertainment,Outcome Absent at Start,Comparability (Age/Gender),Comparability (Other),Outcome Assessment,Follow-up Length,Follow-up Adequacy,Total Score,Overall RoB
Smith 2019,1,1,1,1,1,0,1,1,1,8,Low
Jones 2020,1,1,1,1,1,0,1,1,0,7,Moderate
Brown 2021,0,1,1,1,0,1,1,0,1,6,Moderate
```

## NOS Scoring Interpretation

The package automatically converts total NOS scores to standardized risk categories:

**Table 2: NOS score to risk category conversion**

| Total Stars | Interpretation | Risk Category |
|-------------|----------------|---------------|
| 7–9 | High-quality study | Low RoB |
| 4–6 | Moderate-quality study | Moderate RoB |
| 0–3 | Poor-quality study | High RoB |


# Figures

Below are example visualizations generated by NOS-TLPlot with different themes:

![Example Result1](example/output.png)
NOS bubble plot

![Example Result2](example/output_radar.png)
Domain Scores Radar Chart by Study

![Example Result3](example/output_theme_radar.png)
Theme-based Domain Scores Radar Chart

![Example Result4](example/output_line_ordered.png)
Domain Scores Ordered by Total Score

![Example Result5](example/output_lollipop.png)
Total NOS Scores by Study (Lollipop Chart)

![Example Result6](example/output_dot_profile.png)
Domain Score Profiles by Study

![Example Result7](example/output_stacked_area.png)
Risk Distribution by Domain (Stacked Area Chart)

![Example Result8](example/output_donut.png)
Risk Donut Distribution by Domain

![Example Result9](example/output_pie.png)
Distribution of Overall Risk of Bias Pie

![Example Result10](example/output_heatmap.png)
Risk of Bias by Domain and Study by heatmap

![Example Result11](example/output_table.png)
NOS Scores by Study


# Acknowledgements

The author acknowledges the contributions of open-source software developers whose work underpins this package. Special thanks to the developers of Matplotlib, Pandas, and Streamlit for providing the foundational tools that make this package possible. No external funding was used in this work.


# References
