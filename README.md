
![Logo](assets/preview1.png)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Streamlit Demo](https://img.shields.io/badge/Streamlit-Demo-orange)](https://nos-tlplot.streamlit.app)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17065214.svg)](https://doi.org/10.5281/zenodo.17065214)
[![JORS](https://img.shields.io/badge/Journal-JORS-blue)](https://doi.org/10.5334/jors.635)


---

**NOS-TLPlot** is an open-source Python tool for **visualising Newcastle–Ottawa Scale (NOS) risk-of-bias assessments**.  
It converts NOS star ratings into **publication-ready traffic-light plots** and **13 specialized visualizations**, enabling reviewers and readers to interpret study-level risk-of-bias results clearly and reproducibly.
 
📂 **Code & Archive (Zenodo DOI):** [10.5281/zenodo.17065214](https://doi.org/10.5281/zenodo.17065214)

📃 **Software Metapaper (Journal of Open Research Software DOI):** [10.5334/jors.635](https://doi.org/10.5334/jors.635)

---

## ✨ Key Features

- **13 Visualization Types**: Traffic-light plots, radar charts, heatmaps, item heatmaps, stacked star profiles, donut charts, lollipop charts, star matrices, and more  
- **Publication-Quality Output**: Export figures in `.png`, `.pdf`, `.svg`, `.eps` formats  
- **Multiple Themes**: Traffic-light, grayscale, ocean-blue, and sage themes for various publication requirements. [See the Themes section](#themes)  
- **Interactive Web App**: Built with Streamlit for simple data upload, preview, and figure export  
- **Command Line Interface**: For batch processing and automated figure generation  
- **Domain-Specific Risk Assessment**: Automatically converts NOS stars (0–9) to categorical RoB (Low/Moderate/High)  
- **Customizable Output**: Adjustable figure sizes, line thickness, and color themes  
- **Scope-Limited**: Designed exclusively for NOS evaluations of non-randomised studies  

---

## USE

- Main web (GitHub Pages) leading to Streamlit → [nos-tlplot.github.io](https://nos-tlplot.github.io)

![Example Result33](example/Screenshot3.png)
Main web user-interface

---

- To directly use it → [nos-tlplot.streamlit.app](https://nos-tlplot.streamlit.app)

![Example Result11](example/Screenshot1.png)

![Example Result22](example/Screenshot2.png)
Streamlit user-interface

---

## 📥 Installation (Optional)

### Prerequisites
- This code is based on Python-3.12.3 (however works with **3.11+**)
- `pip` package manager  

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/aurumz-rgb/NOS-TLPlot.git
cd NOS-TLPlot

# Install dependencies
pip install -r requirements.txt
````

---

## ⚡ Usage (directly via Streamlit web OR)

### 1️⃣ Streamlit Web App (Recommended)

```bash
cd NOS-TLPlot
streamlit run app.py
```

**Features:**

* Upload CSV/Excel files
* Real-time visualization preview
* Choose from 12 plot types
* Download publication-ready figures in multiple formats
* Theme switcher (Traffic-light / Grayscale / Ocean / Sage)

**Steps:**

1. Run the above command
2. Open the local Streamlit URL (default: `http://localhost:8501`)
3. Upload your NOS dataset
4. Choose visualization and theme
5. Preview and download figures

---

### 2️⃣ Python Script (Command Line) (For Reviewers to ensure reproducibility and Transparency)

```bash
cd NOS-TLPlot
# Basic usage
python3 nos_tlplot.py sample.csv output.png

# With theme
python3 nos_tlplot.py sample.csv output-traffic-light.png gray
```

---

### 🧩 Python Sample

![Python Result1](example/python.png)

---

**Parameters:**

| Parameter     | Description                                         |
| ------------- | --------------------------------------------------- |
| `input_file`  | Path to CSV/Excel file containing NOS data          |
| `output_file` | Output file name and extension                      |
| `theme`       | Optional theme: `traffic_light` (default), `gray`, `ocean` or `sage` |

**Generated Outputs:**

| File                 | Description                             |
| -------------------- | --------------------------------------- |
| `_traffic-light.png` | Classic traffic-light bubble plot       |
| `_radar.png`         | Radar chart of domain scores            |
| `_heatmap.png`       | Color heatmap for domain-level bias     |
| `_item_heatmap.png`  | Item-level star heatmap with domain bands |
| `_dot_profile.png`   | Stacked domain stars per study          |
| `_table.png`         | Summary table with domain scores        |
| `_donut.png`         | Donut chart of overall bias levels      |
| `_line_ordered.png`  | Item-level star ratings matrix          |
| `_lollipop.png`      | Lollipop chart for comparative bias     |
| `_pie.png`           | Proportional risk-of-bias pie           |
| `_stacked_area.png`  | Stacked area visualization over domains |
| `_nos_plot.png`      | NOS visualization plot                  |

---

##  Input Data Format

Your file should have these columns:

| Column Name                  | Description      | Valid Range           |
| ---------------------------- | ---------------- | --------------------- |
| `Author, Year`               | Study identifier | Text                  |
| `Representativeness`         | Domain 1         | 0–1                   |
| `Non-exposed Selection`      | Domain 2         | 0–1                   |
| `Exposure Ascertainment`     | Domain 3         | 0–1                   |
| `Outcome Absent at Start`    | Domain 4         | 0–1                   |
| `Comparability (Age/Gender)` | Domain 5         | 0–2                   |
| `Comparability (Other)`      | Domain 6         | 0–2                   |
| `Outcome Assessment`         | Domain 7         | 0–1                   |
| `Follow-up Length`           | Domain 8         | 0–1                   |
| `Follow-up Adequacy`         | Domain 9         | 0–1                   |
| `Total Score`                | Sum of stars     | 0–9                   |
| `Overall RoB`                | Risk of bias     | Low / Moderate / High |

> 💡 *Tip:* Always include your raw NOS scoring table in supplementary materials for reproducibility.

---

## 🎨 Visualization Types

1. **Traffic-Light Bubble Plot** – Classic NOS traffic-light visualization.
2. **Domain Radar Chart** – Domain scores per study as radar polygons.
3. **Theme Radar Chart** – Theme-adapted radar chart.
4. **Domain Heatmap** – Color heatmap for domain-level bias.
5. **Item-Level Star Heatmap** – Item stars grouped into domain bands.
6. **Stacked Domain Stars** – Stacked domain stars for each study.
7. **Score Table** – Summary table of stars and overall risk.
8. **Risk Donut Chart** – Risk proportions per domain.
9. **Star Ratings Matrix** – Item-level star matrix ordered by total score.
10. **Total Score Lollipop** – Total NOS scores per study.
11. **Overall Risk Pie** – Overall risk-of-bias distribution.
12. **Stacked Area Risk Chart** – Risk distribution across domains.
13. **NOS Visualization Grid** – Item-level traffic-light grid with domain bands and totals.

Note: Radar Plots are only limited to 5 studies.

---

## NOS Scoring → Risk-of-Bias Conversion

| Total Stars | Interpretation         | Risk Category    |
| ----------- | ---------------------- | ---------------- |
| 7–9         | High-quality study     | **Low RoB**      |
| 4–6         | Moderate-quality study | **Moderate RoB** |
| 0–3         | Poor-quality study     | **High RoB**     |

> Conversion follows Newcastle–Ottawa Scale standards for cohort/case-control/cross-sectional designs.

---

## 🔧 Technical Details

* **Core Engine:** `matplotlib`, `seaborn`, `numpy`, `pandas`
* **Web UI:** `streamlit`
* **Table Rendering:** `matplotlib.table`
* **Plot Layout Management:** `GridSpec`
* **Color Systems:** Custom mcolors, traffic-light mapping
* **Data Handling:** CSV/Excel file input with automatic parsing
* **Batch Plotting:** Parallel generation for multiple figure types
* **Export Quality:** 300 DPI (default), publication-ready vector output


---

###  Repository Structure

```
NOS-TLPlot/
├── app.py                 # Streamlit web app
├── nos_tlplot.py          # Main plotting engine
├── requirements.txt       # Dependencies
├── README.md              # Project documentation
├── citation.cff           # Citation metadata
├── LICENSE                # Apache 2.0 License
├── examples               # All the Sample outputs

```

---

##  ⭐ Support

*  For usage questions, open a [Discussion](https://github.com/aurumz-rgb/NOS-TLPlot/discussions)
*  For bug reports or feature requests, open an [Issue](https://github.com/aurumz-rgb/NOS-TLPlot/issues)
*  Email: [mail](mailto:pteroisvolitans12@gmail.com)


---


##  Acknowledgment

I sincerely thank the **Journal of Open Research Software (JORS)** for providing a full publication waiver supporting this software.


---

##  🧩 Citation

NOS-TLPlot Software code is cited:

> **Sahu, V. (2025). NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v3.0.0). Zenodo.**
DOI: [10.5281/zenodo.17065214](https://doi.org/10.5281/zenodo.17065214)


NOS-TLPlot Software Metapaper is cited: **[PREFERRED]**

> **Sahu, V. (2026). NOS-TLPlot: A Specialized Python Tool for Visualizing Newcastle–Ottawa Scale Risk-of-Bias Assessments. *Journal of Open Research Software*, 14(1), 7.**
DOI: [10.5334/jors.635](https://doi.org/10.5334/jors.635)

```bibtex
@software{Sahu2025,
  author = {Sahu, Vihaan},
  title = {NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v3.0.0)},
  year = {2025},
  doi = {10.5281/zenodo.17065214},
  url = {https://doi.org/10.5281/zenodo.17065214},
  version = {3.0.0}
}

@article{Sahu2026,
  author = {Sahu, Vihaan},
  title = {NOS-TLPlot: A Specialized Python Tool for Visualizing Newcastle–Ottawa Scale Risk-of-Bias Assessments},
  journal = {Journal of Open Research Software},
  volume = {14},
  number = {1},
  pages = {7},
  year = {2026},
  doi = {10.5334/jors.635},
  url = {https://doi.org/10.5334/jors.635}
}
```

---

# Sample Plots

All the Output Sample plots

![Example NOS Plot](example/nos_plot.png)
NOS visualization plot


![Example Result1](example/output.png)
NOS bubble plot


![Example Result2](example/output_radar.png)
Domain Scores Radar Chart by Study


![Example Result3](example/output_theme_radar.png)
Theme-based Domain Scores Radar Chart


![Example Result4](example/output_line_ordered.png)
NOS star ratings matrix by study (ordered by total score)


![Example Result5](example/output_lollipop.png)
Total NOS Scores by Study (Lollipop Chart)


![Example Result6](example/output_dot_profile.png)
Domain stars by study (stacked)


![Example Result7](example/output_stacked_area.png)
Risk Distribution by Domain (Stacked Area Chart)


![Example Result8](example/output_donut.png)
Risk Donut Distribution by Domain


![Example Result9](example/output_pie.png)
Distribution of Overall Risk of Bias Pie


![Example Result10](example/output_heatmap.png)
Risk of Bias by Domain and Study by heatmap


![Example Result12](example/output_item_heatmap.png)
Item-level NOS star heatmap by domain


![Example Result11](example/output_table.png)
NOS Scores by Study

---

## Themes

NOS-TLPlot ships with four colour themes - `traffic_light` (default), `gray`, `ocean` and `sage` - selectable in the web app or via the optional theme argument on the command line.

| Theme | Low | Moderate | High |
| ----- | --- | -------- | ---- |
| `traffic_light` | `#2E7D32` | `#F9A825` | `#C62828` |
| `gray` | `#D6D6D6` | `#9E9E9E` | `#3C3C3C` |
| `ocean` | `#6BAED6` | `#2171B5` | `#08306B` |
| `sage` | `#63BF93` | `#5B6D80` | `#FF884D` |

![Example NOS plot in the ocean theme](example/nos_plot_ocean.png)
NOS visualization plot in the ocean theme

![Example NOS plot in the sage theme](example/nos_plot_sage.png)
NOS visualization plot in the sage theme
