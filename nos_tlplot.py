import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors
from matplotlib.patches import Patch, Rectangle, Circle
import numpy as np
import matplotlib as mpl
import matplotlib.patheffects as path_effects
from matplotlib.collections import LineCollection
from matplotlib.transforms import ScaledTranslation

try:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
except ImportError:
    print("⚠️ Warning: Pillow (PIL) not found. Image size limits may apply.")

THEME_OPTIONS = {
    "traffic_light": {"Low":"#2E7D32", "Moderate":"#F9A825", "High":"#C62828"},  
    "gray": {"Low":"#C7D5E2", "Moderate":"#8B98A1", "High":"#5F6770"},            
    "ocean": {"Low":"#6BAED6", "Moderate":"#2171B5", "High":"#08306B"},
    "sage": {"Low":"#63BF93", "Moderate":"#5B6D80", "High":"#FF884D"},
}

plt.style.use('seaborn-v0_8-whitegrid')
mpl.rcParams['font.family'] = 'DejaVu Sans'
mpl.rcParams['font.weight'] = 'bold'
mpl.rcParams['axes.labelweight'] = 'bold'
mpl.rcParams['axes.titleweight'] = 'bold'
mpl.rcParams['figure.titlesize'] = 16
mpl.rcParams['axes.titlesize'] = 14
mpl.rcParams['axes.labelsize'] = 12
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['legend.fontsize'] = 10
mpl.rcParams['legend.title_fontsize'] = 11
mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.pad_inches'] = 0.3
mpl.rcParams['savefig.transparent'] = False

def get_theme_colors(theme):
    if theme not in THEME_OPTIONS:
        raise ValueError(f"Theme {theme} not available. Choose from {list(THEME_OPTIONS.keys())}")
    return THEME_OPTIONS[theme]

def compact_legend_fontsize(fig):
    return min(11.0, max(8.5, 0.65 * fig.get_size_inches()[0]))

def add_compact_legend(ax, handles, title, anchor_x=1.02, fontsize=None):
    fs = fontsize if fontsize is not None else compact_legend_fontsize(ax.get_figure())
    leg = ax.legend(handles=handles, title=title, fontsize=fs, title_fontsize=fs + 0.5,
                    loc='upper left', bbox_to_anchor=(anchor_x, 1.0), frameon=True,
                    edgecolor='black', facecolor='white', framealpha=1,
                    labelspacing=0.5, borderpad=0.6, handlelength=1.7,
                    handletextpad=0.6, borderaxespad=0.0)
    for text in leg.get_texts():
        text.set_fontweight('normal')
    leg.get_title().set_fontweight('bold')
    return leg

def add_radar_note(fig, ax):
    bold_text = "Note:"
    normal_text = "Scores are normalized to domain maxima (Selection ÷4, Comparability ÷2, Outcome/Exposure ÷3);"
    ax_box = ax.get_position()
    center_x = (ax_box.x0 + ax_box.x1) / 2
    y = ax_box.y0 - 0.055
    bold = fig.text(center_x, y, bold_text, ha='left', fontsize=12, fontweight='bold')
    normal = fig.text(center_x, y, normal_text, ha='left', fontsize=12, fontweight='normal')
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bold_w = bold.get_window_extent(renderer).width / fig.bbox.width
    normal_w = normal.get_window_extent(renderer).width / fig.bbox.width
    gap = 0.0025
    start_x = center_x - (bold_w + gap + normal_w) / 2
    bold.set_position((start_x, y))
    normal.set_position((start_x + bold_w + gap, y))

def process_detailed_nos(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        "Author, Year",
        "Representativeness", "Non-exposed Selection", "Exposure Ascertainment", "Outcome Absent at Start",
        "Comparability (Age/Gender)", "Comparability (Other)",
        "Outcome Assessment", "Follow-up Length", "Follow-up Adequacy",
        "Total Score", "Overall RoB"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    numeric_cols = required_columns[1:-2]  
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column {col} must be numeric.")
        if df[col].min() < 0 or df[col].max() > 5:
            raise ValueError(f"Column {col} contains invalid star values (0-5 allowed).")

    df["Selection"] = df["Representativeness"] + df["Non-exposed Selection"] + df["Exposure Ascertainment"] + df["Outcome Absent at Start"]
    df["Comparability"] = df["Comparability (Age/Gender)"] + df["Comparability (Other)"]
    df["Outcome/Exposure"] = df["Outcome Assessment"] + df["Follow-up Length"] + df["Follow-up Adequacy"]

    df["ComputedTotal"] = df["Selection"] + df["Comparability"] + df["Outcome/Exposure"]
    mismatches = df[df["ComputedTotal"] != df["Total Score"]]
    if not mismatches.empty:
        print("⚠️ Warning: Total Score mismatches detected:")
        print(mismatches[["Author, Year", "Total Score", "ComputedTotal"]])

    return df

def stars_to_rob(stars, domain):
    if domain == "Selection":
        return "Low" if stars >= 3 else "Moderate" if stars == 2 else "High"
    elif domain == "Comparability":
        return "Low" if stars == 2 else "Moderate" if stars == 1 else "High"
    elif domain == "Outcome/Exposure":
        return "Low" if stars == 3 else "Moderate" if stars == 2 else "High"
    elif domain == "Overall Risk":
        return stars
    return "High"

def map_color(stars, domain, colors):
    risk = stars_to_rob(stars, domain)
    return colors.get(risk, "grey")

def professional_plot(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors = get_theme_colors(theme)
    line_width = 1.5
    
    fig_height = max(7.5, 0.55 * len(df) + 3)
    fig = plt.figure(figsize=(20, fig_height))

    gs = GridSpec(1, 1, left=0.08, right=0.75, top=0.95, bottom=0.08)

    ax = fig.add_subplot(gs[0])
    
    domains = ["Selection", "Comparability", "Outcome/Exposure", "Overall Risk"]
    max_scores = {"Selection": 4, "Comparability": 2, "Outcome/Exposure": 3, "Overall Risk": 1}
    
    
    domain_positions = {"Selection": 0, "Comparability": 7, "Outcome/Exposure": 14, "Overall Risk": 21}
    
    bubble_data = []
    for _, row in df.iterrows():
        for domain in domains:
            if domain == "Overall Risk":
                stars = 1 if row["Overall RoB"] == "Low" else (0.67 if row["Overall RoB"] == "Moderate" else 0.33)
                risk = row["Overall RoB"]
            else:
                stars = row[domain]
                risk = stars_to_rob(stars, domain)
            
            normalized_size = stars / max_scores[domain]
            bubble_data.append({
                "Author, Year": row["Author, Year"],
                "Domain": domain,
                "Stars": stars,
                "NormalizedSize": normalized_size,
                "Risk": risk,
                "Color": colors[risk]
            })
    
    bubble_df = pd.DataFrame(bubble_data)
    
    bubble_df["X"] = bubble_df["Domain"].map(domain_positions)
    
    studies = df["Author, Year"].unique()
    study_positions = {study: i * 1.8 for i, study in enumerate(studies)}
    bubble_df["Y"] = bubble_df["Author, Year"].map(study_positions)
    
    min_size, max_size = 610, 1680
    bubble_df["Size"] = min_size + (max_size - min_size) * bubble_df["NormalizedSize"]
    
    for _, row in bubble_df.iterrows():
        glow = Circle((row["X"], row["Y"]), radius=row["Size"]/2000, 
                     facecolor=row["Color"], alpha=0.4, zorder=2)
        ax.add_patch(glow)
        
        bubble = Circle((row["X"], row["Y"]), radius=row["Size"]/2000, 
                       facecolor=row["Color"], alpha=0.9, edgecolor='black', linewidth=1.0, zorder=3)
        ax.add_patch(bubble)
        
        if row["Domain"] == "Overall Risk":
            ax.text(row["X"], row["Y"], row["Risk"][0], ha='center', va='center', 
                    color='white', fontsize=18, fontweight='bold',
                    path_effects=[path_effects.withStroke(linewidth=2, foreground='black')], zorder=4)
        else:
            ax.text(row["X"], row["Y"], str(int(row["Stars"])), ha='center', va='center', 
                    color='white', fontsize=17, fontweight='bold',
                    path_effects=[path_effects.withStroke(linewidth=2, foreground='black')], zorder=4)
    
    for study in studies:
        study_data = bubble_df[bubble_df["Author, Year"] == study].sort_values("X")
        x_vals = study_data["X"].values
        y_vals = study_data["Y"].values
        
        for i in range(len(x_vals) - 1):
            segment = [(x_vals[i], y_vals[i]), (x_vals[i+1], y_vals[i+1])]
            color = colors[stars_to_rob(study_data.iloc[i]["Stars"], study_data.iloc[i]["Domain"])]
            lc = LineCollection([segment], colors=[color], linewidth=3, alpha=0.7, zorder=1)
            ax.add_collection(lc)
    
    ax.set_title("NOS Risk Assessment Bubble Chart", fontsize=20, pad=34, fontweight='bold')
    ax.set_xlabel("")
    ax.set_ylabel("Study", fontsize=14, labelpad=22, fontweight='bold')
    
    ax.set_xticks([0, 7, 14, 21])
    ax.set_xticklabels(domains, fontsize=16)
    
    ax.set_yticks([i * 1.8 for i in range(len(studies))])
    ax.set_yticklabels(studies, fontsize=14)
    ax.set_xlim(-1.05, 23)
    ax.set_ylim(-1.15, (len(studies) - 1) * 1.8 + 0.85)
    ax.grid(False)
    
    ax.set_aspect('equal', adjustable='box')
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    ax.grid(axis='x', linestyle='--', alpha=0.55, color='#70767E')
    
    fs = min(14.0, compact_legend_fontsize(fig) + 2.5)
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Low Risk',
                markerfacecolor=colors["Low"], markersize=fs * 0.9, markeredgewidth=0.8, markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', label='Moderate Risk',
                markerfacecolor=colors["Moderate"], markersize=fs * 0.9, markeredgewidth=0.8, markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', label='High Risk',
                markerfacecolor=colors["High"], markersize=fs * 0.9, markeredgewidth=0.8, markeredgecolor='black')
    ]
    add_compact_legend(ax, legend_elements, "Risk Level", fontsize=fs)
    
    note_parts = [
        ("Note: ", True),
        ("In Overall Risk column, ", False),
        ("H", True),
        (" = High Risk, ", False),
        ("M", True),
        (" = Moderate Risk, ", False),
        ("L", True),
        (" = Low Risk", False),
    ]
    note_y = -0.01
    note_texts = [fig.text(0.5, note_y, text, ha='left', va='center', fontsize=16, style='italic',
                           fontweight='bold' if bold else 'normal')
                  for text, bold in note_parts]
    fig.canvas.draw()
    fig_px = fig.get_figwidth() * fig.dpi
    widths = [text.get_window_extent(renderer=fig.canvas.get_renderer()).width for text in note_texts]
    x = (fig_px - sum(widths)) / 2 / fig_px
    for text, width in zip(note_texts, widths):
        text.set_position((x, note_y))
        x += width / fig_px


    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Professional combined plot saved to {output_file}")



def plot_domain_radar(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    if len(df) > 5:
        print(f"⚠️ Skipping radar chart: {len(df)} studies exceed the maximum of 5 for radar visualization")
        return
    

    colors_map = get_theme_colors(theme)

    max_scores = {"Selection": 4, "Comparability": 2, "Outcome/Exposure": 3}
    domains = list(max_scores.keys())

    fig_width = max(14, 10 + len(df) * 0.2)
    fig_height = max(10, 8 + len(df) * 0.15)
    fig = plt.figure(figsize=(fig_width, fig_height))
    ax = fig.add_subplot(111, polar=True)
    
    angles = np.linspace(0, 2 * np.pi, len(domains), endpoint=False).tolist()
    angles += angles[:1] 
    
    
    hardcoded_study_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    study_colors = [hardcoded_study_colors[i] for i in range(len(df))]
    
    for idx, row in df.iterrows():
        values = [row[domain] / max_scores[domain] for domain in domains]
        values += values[:1] 
        
        ax.plot(angles, values, 'o-', linewidth=3.0, color=study_colors[idx], alpha=0.8, 
                markeredgecolor='black', markeredgewidth=0.8, markersize=10)
        ax.fill(angles, values, alpha=0.2, color=study_colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(["A", "B", "C"], fontsize=15)
    ax.set_title("Domain Scores Radar Chart by Study", size=18, pad=34)
    ax.set_ylim(0, 1.08)
    
    ax.tick_params(axis='y', labelsize=14)
    ax.grid(True, linestyle='-', alpha=0.7, linewidth=1.5)
    

    fs = min(13.0, compact_legend_fontsize(fig) + 3.0)
    study_legend_elements = [Line2D([0], [0], color=study_colors[i], lw=2.0, label=row['Author, Year'])
                             for i, (_, row) in enumerate(df.iterrows())]
    leg = add_compact_legend(ax, study_legend_elements, "Study", anchor_x=1.22, fontsize=fs)

    plt.subplots_adjust(bottom=0.22)

    domain_mapping = {"A": "Selection", "B": "Comparability", "C": "Outcome / Exposure"}

    ax_h_in = ax.get_position().height * fig.get_size_inches()[1]
    row_h = (fs * 1.6 / 72) / ax_h_in

    labels = [f"$\\mathbf{{{letter}}}$ : {domain}" for letter, domain in domain_mapping.items()]
    row_texts = [ax.text(0.985, 0.02 + (len(labels) - 1 - i) * row_h, label,
                         transform=ax.transAxes, fontsize=fs, color='black',
                         verticalalignment='bottom', horizontalalignment='left',
                         fontweight='normal')
                 for i, label in enumerate(labels)]

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transAxes.inverted()
    lbox = leg.get_window_extent(renderer=renderer).transformed(inv)
    boxes = [t.get_window_extent(renderer=renderer).transformed(inv) for t in row_texts]
    x0 = min(b.x0 for b in boxes) - 0.015
    x1 = max(b.x1 for b in boxes) + 0.015
    y0 = min(b.y0 for b in boxes) - 0.012
    y1 = max(b.y1 for b in boxes) + 0.012
    title = ax.text((x0 + x1) / 2, y1 + 0.005, "Domain", transform=ax.transAxes,
                    fontsize=fs + 0.5, color='black', verticalalignment='bottom',
                    horizontalalignment='center', fontweight='bold')
    tbox = title.get_window_extent(renderer=renderer).transformed(inv)
    y1 = max(y1, tbox.y1) + 0.012
    dx = lbox.x0 - x0
    dy = (lbox.y0 - 0.02) - y1
    for t in row_texts + [title]:
        x, y = t.get_position()
        t.set_position((x + dx, y + dy))
    rect = Rectangle((x0 + dx, y0 + dy), x1 - x0, y1 - y0,
                     transform=ax.transAxes, facecolor='white',
                     edgecolor='black', alpha=1.0, linewidth=0.8, zorder=2, clip_on=False)
    ax.add_patch(rect)

    add_radar_note(fig, ax)

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Domain radar chart saved to {output_file}")




def plot_theme_radar(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    if len(df) > 5:
        print(f"⚠️ Skipping theme radar chart: {len(df)} studies exceed the maximum of 5 for radar visualization")
        return
    
    colors_map = get_theme_colors(theme)
    
    max_scores = {"Selection": 4, "Comparability": 2, "Outcome/Exposure": 3}
    domains = list(max_scores.keys())
    
    fig_width = max(14, 10 + len(df) * 0.2)
    fig_height = max(10, 8 + len(df) * 0.15)
    fig = plt.figure(figsize=(fig_width, fig_height))
    ax = fig.add_subplot(111, polar=True)
    
    angles = np.linspace(0, 2 * np.pi, len(domains), endpoint=False).tolist()
    angles += angles[:1] 
    
    for idx, row in df.iterrows():
        values = [row[domain] / max_scores[domain] for domain in domains]
        values += values[:1] 
        
        color = colors_map.get(row["Overall RoB"], "grey")
        ax.plot(angles, values, 'o-', linewidth=3.0, color=color, alpha=0.8, 
                markeredgecolor='black', markeredgewidth=0.8, markersize=10)
        ax.fill(angles, values, alpha=0.2, color=color)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(["A", "B", "C"], fontsize=15)
    ax.set_title("Theme-based Domain Scores Radar Chart", size=19, pad=34)
    ax.set_ylim(0, 1.08)
    
    ax.tick_params(axis='y', labelsize=14)
    ax.grid(True, linestyle='-', alpha=0.7, linewidth=1.5)
    
    fs = min(13.0, compact_legend_fontsize(fig) + 3.0)
    legend_elements = [Line2D([0], [0], color=colors_map[rob], lw=2.0, label=f"{rob} Risk") for rob in ["Low", "Moderate", "High"]]
    risk_legend = add_compact_legend(ax, legend_elements, "Overall Risk", anchor_x=1.22, fontsize=fs)

    domain_mapping = {"A": "Selection", "B": "Comparability", "C": "Outcome / Exposure"}

    ax_h_in = ax.get_position().height * fig.get_size_inches()[1]
    row_h = (fs * 1.6 / 72) / ax_h_in

    labels = [f"$\\mathbf{{{letter}}}$ : {domain}" for letter, domain in domain_mapping.items()]
    row_texts = [ax.text(0.985, 0.02 + (len(labels) - 1 - i) * row_h, label,
                         transform=ax.transAxes, fontsize=fs, color='black',
                         verticalalignment='bottom', horizontalalignment='left',
                         fontweight='normal')
                 for i, label in enumerate(labels)]

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transAxes.inverted()
    lbox = risk_legend.get_window_extent(renderer=renderer).transformed(inv)
    boxes = [t.get_window_extent(renderer=renderer).transformed(inv) for t in row_texts]
    x0 = min(b.x0 for b in boxes) - 0.015
    x1 = max(b.x1 for b in boxes) + 0.015
    y0 = min(b.y0 for b in boxes) - 0.012
    y1 = max(b.y1 for b in boxes) + 0.012
    title = ax.text((x0 + x1) / 2, y1 + 0.005, "Domain", transform=ax.transAxes,
                    fontsize=fs + 0.5, color='black', verticalalignment='bottom',
                    horizontalalignment='center', fontweight='bold')
    tbox = title.get_window_extent(renderer=renderer).transformed(inv)
    y1 = max(y1, tbox.y1) + 0.012
    dx = lbox.x0 - x0
    dy = (lbox.y0 - 0.02) - y1
    for t in row_texts + [title]:
        x, y = t.get_position()
        t.set_position((x + dx, y + dy))
    rect = Rectangle((x0 + dx, y0 + dy), x1 - x0, y1 - y0,
                     transform=ax.transAxes, facecolor='white',
                     edgecolor='black', alpha=1.0, linewidth=0.8, zorder=2, clip_on=False)
    ax.add_patch(rect)

    add_radar_note(fig, ax)
    

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Theme-based radar chart saved to {output_file}")

def plot_domain_heatmap(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    
    heatmap_df = df[["Author, Year", "Selection", "Comparability", "Outcome/Exposure", "Overall RoB"]].set_index("Author, Year")
    risk_df = heatmap_df.copy()
    
    for domain in ["Selection", "Comparability", "Outcome/Exposure"]:
        risk_df[domain] = risk_df[domain].apply(lambda x: stars_to_rob(x, domain))
    
    risk_map = {"High":0, "Moderate":1, "Low":2}
    numeric_df = risk_df.map(lambda x: risk_map[x])
    
    cmap = mcolors.ListedColormap([colors_map["High"], colors_map["Moderate"], colors_map["Low"]])
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
   
    fig_height = max(5, 0.8 * len(df))
    fig, ax = plt.subplots(figsize=(8, fig_height))
    
    sns.heatmap(numeric_df, cmap=cmap, norm=norm, linewidths=2.5, linecolor='white', ax=ax, cbar=False)
    

    ax.set_yticklabels(heatmap_df.index, fontsize=8)
    ax.set_xticklabels(heatmap_df.columns, rotation=45, ha='right', fontsize=8.5)
    

    ax.set_ylabel("Author, Year", fontsize=12, labelpad=20)
    
    fs = compact_legend_fontsize(fig)
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=colors_map[rob],
                              markeredgecolor='black', markersize=fs * 0.85, markeredgewidth=0.8, label=f"{rob} Risk")
                       for rob in ["High", "Moderate", "Low"]]

    add_compact_legend(ax, legend_elements, "Overall Risk")

    ax.set_title("Risk of Bias by Domain and Study", fontsize=15, pad=12)
    

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Domain heatmap plot saved to {output_file}")

def plot_star_distribution(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    domains = ["Selection", "Comparability", "Outcome/Exposure"]
    
    plot_data = []
    for domain in domains:
        for stars in range(0, 6):
            count = (df[domain] == stars).sum()
            plot_data.append({"Domain": domain, "Stars": stars, "Count": count})
    
    plot_df = pd.DataFrame(plot_data)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    domain_order = ["Selection", "Comparability", "Outcome/Exposure"]
    palette_list = [colors_map["Low"], colors_map["Moderate"], colors_map["High"]]
    
    sns.barplot(data=plot_df, x="Stars", y="Count", hue="Domain", 
                hue_order=domain_order, palette=palette_list,
                ax=ax, edgecolor='black', linewidth=0.8, alpha=0.9)
    
    ax.set_title("Distribution of Star Ratings by Domain", fontsize=16, pad=12)
    ax.set_xlabel("Star Rating", fontsize=12)
    ax.set_ylabel("Number of Studies", fontsize=12)
    handles, _ = ax.get_legend_handles_labels()
    add_compact_legend(ax, handles, "Domain")
    ax.grid(axis='y', linestyle='--', alpha=0.7)


    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Star distribution plot saved to {output_file}")

def plot_dot_profile(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    if len(df) > 5:
        print("❌ Cannot generate plot: Maximum 5 studies allowed")
        return
    
    colors_map = get_theme_colors(theme)
    domains = ["Selection", "Comparability", "Outcome/Exposure"]
    
    num_studies = len(df)
    base_width = 10
    base_height = 5
    width_per_study = 0.4
    height_per_study = 0.15
    
    fig_width = base_width + (num_studies * width_per_study)
    fig_height = base_height + (num_studies * height_per_study)
    
    offsets = np.linspace(-0.2, 0.2, num_studies) if num_studies > 1 else [0.0]
    jitter_dict = {idx: offsets[i] for i, idx in enumerate(df.index)}

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    for idx, row in df.iterrows():
        scores = [row[domain] for domain in domains]
        color = colors_map.get(row["Overall RoB"], "grey")
        jitter = jitter_dict[idx]
        
        x_coords = [i + jitter for i in range(len(domains))]
        
        ax.plot(x_coords, scores, 'o-', color=color, alpha=0.8, linewidth=3.5, 
                markersize=8, markeredgecolor='black', markeredgewidth=0.8)
    
    for domain in domains:
        max_score = 4 if domain == "Selection" else (2 if domain == "Comparability" else 3)
        ax.axhline(y=max_score, color='gray', linestyle='--', alpha=0.5, linewidth=1.0)
    
    ax.set_title("Domain Score Profiles by Study", fontsize=16, pad=12)
    ax.set_xlabel("Domain", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.xaxis.grid(False)
    
    ax.set_xticks(range(len(domains)))
    ax.set_xticklabels(domains)
    ax.set_xlim(-0.3, len(domains)-0.3)
    
    legend_elements = [Line2D([0], [0], color=colors_map[rob], lw=2.0, label=f"{rob} Risk") for rob in ["Low", "Moderate", "High"]]
    add_compact_legend(ax, legend_elements, "Overall Risk")
    

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Dot profile plot saved to {output_file}")

def plot_score_table(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)


    table_df = df[["Author, Year", "Selection", "Comparability", "Outcome/Exposure", "Total Score", "Overall RoB"]].copy()
    table_df = table_df.sort_values("Overall RoB", ascending=False)
    
    fig_width = max(12, 5 + len(table_df.columns) * 1.63)
    fig_height = max(5, 0.4 * len(table_df) + 1.2)
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')
    

    def tint(hex_color, factor=0.0):
        r, g, b, _ = mcolors.to_rgba(hex_color)
        return (r + (1 - r) * factor, g + (1 - g) * factor, b + (1 - b) * factor)

    row_fills = [colors_map.get(row["Overall RoB"], "white") for _, row in table_df.iterrows()]

    table = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        cellColours=[[tint(fill, 0.45) for _ in range(len(table_df.columns))] for fill in row_fills],
        loc='top left',
        bbox=[0, 0, 1, 1],
        cellLoc='center'
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(15)
    
    for key, cell in table.get_celld().items():
        cell.get_text().set_transform(
            cell.get_text().get_transform()
            + ScaledTranslation(0, -2.5 / 72, fig.dpi_scale_trans)
        )
        if key[0] > 0:
            cell.set_text_props(weight='bold', color='black')
        else:
            cell.set_text_props(weight='bold')
        cell.set_edgecolor('white')
    
    table.scale(1.0, 1.2)
    
    for (i, j), cell in table.get_celld().items():
        if i == 0:  
            cell.set_facecolor('#f0f0f0')
            cell.set_edgecolor('white')
            cell.set_linewidth(2.5)
        else:
            cell.set_edgecolor('white')
            cell.set_linewidth(2.5)
    
    plt.subplots_adjust(left=0.05, right=0.95)
    
    fs = min(12.5, compact_legend_fontsize(fig) + 2.5)
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=colors_map[rob],
                              markeredgecolor='black', markersize=fs * 0.85, markeredgewidth=0.8, label=f"{rob} Risk")
                       for rob in ["High", "Moderate", "Low"]]
    add_compact_legend(ax, legend_elements, "Overall Risk", fontsize=fs)
    

    plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"✅ Score table plot saved to {output_file}")

def plot_donut_domain_risk(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    
    domains = ["Selection", "Comparability", "Outcome/Exposure"]
    
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    
    for i, domain in enumerate(domains):
        risk_counts = df[domain].apply(lambda x: stars_to_rob(x, domain)).value_counts()
        order = ["High", "Moderate", "Low"]
        risk_counts = risk_counts.reindex(order, fill_value=0)
        
        wedge_labels = [name if count > 0 else "" for name, count in risk_counts.items()]
        wedges, texts, autotexts = axs[i].pie(risk_counts, labels=wedge_labels,
                                            autopct=lambda pct: f"{pct:.1f}%" if pct > 0 else "",
                                            colors=[colors_map[rob] for rob in risk_counts.index],
                                            startangle=90, wedgeprops={'linewidth': 0.8, 'edgecolor': 'black'})
        

        center_circle = plt.Circle((0,0), 0.70, fc='white', edgecolor='black', linewidth=0.8)
        axs[i].add_artist(center_circle)
        
        for j, autotext in enumerate(autotexts):
            autotext.set_color('black')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
         
            autotext.set_position((autotext.get_position()[0] * 0.75, autotext.get_position()[1] * 0.75))
        
        for j, text in enumerate(texts):
            text.set_fontweight('bold')
            text.set_fontsize(10)
 
            text.set_position((text.get_position()[0] * 1.05, text.get_position()[1] * 1.05))
        
        axs[i].set_title(f"{domain} Domain", fontsize=12)
    
    fig.suptitle("Risk Distribution by Domain", fontsize=16, y=1.05, fontweight='bold')
    
    fs = compact_legend_fontsize(fig)
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=colors_map[rob],
                              markeredgecolor='black', markersize=fs * 0.85, markeredgewidth=0.8, label=f"{rob} Risk")
                       for rob in ["High", "Moderate", "Low"]]
    fig_legend = fig.legend(handles=legend_elements, title="Overall Risk", fontsize=fs, title_fontsize=fs + 0.5,
                            loc='upper left', bbox_to_anchor=(1.01, 1.0), frameon=True, edgecolor='black',
                            facecolor='white', framealpha=1, labelspacing=0.5, borderpad=0.6,
                            handlelength=1.7, handletextpad=0.6, borderaxespad=0.0)
    for text in fig_legend.get_texts():
        text.set_fontweight('normal')
    fig_legend.get_title().set_fontweight('bold')
    
   
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Donut chart saved to {output_file}")

def plot_line_ordered_scores(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    domain_colors = {
        "Selection": "#1f77b4",  
        "Comparability": "#ff7f0e",  
        "Outcome/Exposure": "#2ca02c" 
    }

    df_sorted = df.sort_values("Total Score")
    
    plot_df = df_sorted.melt(id_vars=["Author, Year", "Overall RoB"], 
                            value_vars=["Selection", "Comparability", "Outcome/Exposure"],
                            var_name="Domain", value_name="Score")
    
    fig_width = max(16, 8 + len(df) * 0.3)
    fig_height = max(8, 6 + len(df) * 0.05)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    for domain in ["Selection", "Comparability", "Outcome/Exposure"]:
        domain_data = plot_df[plot_df["Domain"] == domain]
        ax.plot(domain_data["Author, Year"], domain_data["Score"], 
               'o-', label=domain, linewidth=2.0, markersize=6, 
               markeredgecolor='black', markeredgewidth=0.8, color=domain_colors[domain])
    
    ax.set_title("Domain Scores Ordered by Total Score", fontsize=19, pad=19)
    ax.set_xlabel("Study (Ordered by Total Score)", fontsize=14, labelpad=18)
    ax.set_ylabel("Score", fontsize=14, labelpad=20)
    ax.grid(alpha=0.7)
    
    if len(df) > 50:
        plt.xticks(rotation=90, ha='center')
        ax.tick_params(axis='x', labelsize=7)
    else:
        plt.xticks(rotation=45, ha='right')
        if len(df) > 20:
            ax.tick_params(axis='x', labelsize=11)
        elif len(df) > 10:
            ax.tick_params(axis='x', labelsize=12)
    
    handles, _ = ax.get_legend_handles_labels()
    add_compact_legend(ax, handles, "Domain")
    

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Line plot saved to {output_file}")

def plot_lollipop_total(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    
    df_sorted = df.sort_values("Total Score")
    
    fig_height = max(6, 0.3 * len(df) + 2)
    fig, ax = plt.subplots(figsize=(8, fig_height))
    
    
    y_positions = range(len(df_sorted))
    

    ax.hlines(y=y_positions, xmin=0, xmax=df_sorted["Total Score"], 
             colors=df_sorted["Overall RoB"].map(colors_map), alpha=0.8, linewidth=2.0)
    

    ax.scatter(df_sorted["Total Score"], y_positions, 
              color=df_sorted["Overall RoB"].map(colors_map), alpha=0.9, s=80, 
              edgecolor='black', linewidth=0.8)
    

    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        ax.text(row["Total Score"] + 0.18, i, str(row["Total Score"]),
               va='center', fontsize=10, fontweight='bold')


    ax.set_yticks(y_positions)
    ax.set_yticklabels(df_sorted["Author, Year"])
    ax.set_xlim(-0.3, df_sorted["Total Score"].max() + 0.9)
    
    ax.set_title("Total NOS Scores by Study (Lollipop Chart)", fontsize=16, pad=15)
    ax.set_xlabel("Total Score", fontsize=12)
    ax.set_ylabel("Study", fontsize=12, labelpad=20)
    ax.grid(axis='x', alpha=0.7)
    
    legend_elements = [Line2D([0], [0], color=colors_map[rob], lw=2.0, label=f"{rob} Risk") for rob in ["Low", "Moderate", "High"]]
    add_compact_legend(ax, legend_elements, "Overall Risk")

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Lollipop chart saved to {output_file}")

def plot_pie_overall_rob(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    
    counts = df["Overall RoB"].value_counts()
    order = ["High", "Moderate", "Low"]
    counts = counts.reindex(order, fill_value=0)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    ax.set_position([0.1, 0.1, 0.65, 0.65])
    
    total = counts.sum()
    wedges, texts, autotexts = ax.pie(counts, labels=counts.index, autopct='%1.1f%%',
                                      colors=[colors_map[rob] for rob in counts.index],
                                      startangle=90, wedgeprops={'linewidth': 4, 'edgecolor': 'white'})
    
    for rob, autotext, text in zip(counts.index, autotexts, texts):
        pct = counts[rob] / total * 100 if total else 0
        autotext.set_fontweight('bold')
        autotext.set_fontsize(13)
        if pct == 0:
            autotext.set_text("")
        elif pct < 5:
            autotext.set_text("")
            text.set_text(f"{text.get_text()} ({pct:.1f}%)")
        else:
            autotext.set_color(_contrast_text(colors_map[rob]))
    
    for text in texts:
        text.set_fontweight('bold')
        text.set_fontsize(12)
    
    ax.set_title("Distribution of Overall Risk of Bias", fontsize=16, pad=12)
    
    fs = compact_legend_fontsize(fig)
    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=colors_map[rob],
                              markeredgecolor='black', markersize=fs * 0.85, markeredgewidth=0.8, label=f"{rob} Risk")
                       for rob in ["High", "Moderate", "Low"]]
    add_compact_legend(ax, legend_elements, "Overall Risk")


    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Pie chart saved to {output_file}")

def plot_stacked_area_risk(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    
    domains = ["Selection", "Comparability", "Outcome/Exposure"]
    risk_categories = ["High", "Moderate", "Low"]
    
    counts = {}
    for domain in domains:
        risk_counts = df[domain].apply(lambda x: stars_to_rob(x, domain)).value_counts()
        counts[domain] = [risk_counts.get(cat, 0) for cat in risk_categories]
    
    plot_df = pd.DataFrame(counts, index=risk_categories)
    
    plot_df_percent = plot_df.div(plot_df.sum(axis=0), axis=1) * 100
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.stackplot(domains, plot_df_percent.loc[risk_categories], 
                colors=[colors_map[cat] for cat in risk_categories],
                labels=[f"{cat} Risk" for cat in risk_categories],
                alpha=0.8,
                edgecolor='black',
                linewidth=0.8)

    ax.set_title("Risk Distribution by Domain (Stacked Area Chart)", fontsize=16, pad=12)
    ax.set_xlabel("Domain", fontsize=12)
    ax.set_ylabel("Percentage of Studies (%)", fontsize=12)

    handles, _ = ax.get_legend_handles_labels()
    add_compact_legend(ax, handles, "Overall Risk")
    

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Stacked area chart saved to {output_file}")

NOS_ITEMS = [
    ("Representativeness", "D1", "Representativeness of the exposed cohort"),
    ("Non-exposed Selection", "D2", "Selection of the non-exposed cohort"),
    ("Exposure Ascertainment", "D3", "Ascertainment of exposure"),
    ("Outcome Absent at Start", "D4", "Outcome not present at start of study"),
    ("Comparability (Age/Gender)", "D5", "Comparability - most important factor"),
    ("Comparability (Other)", "D6", "Comparability - additional factor"),
    ("Outcome Assessment", "D7", "Assessment of outcome"),
    ("Follow-up Length", "D8", "Follow-up long enough for outcomes to occur"),
    ("Follow-up Adequacy", "D9", "Adequacy of follow-up"),
]

NOS_DOMAINS = [("SELECTION", 0, 3), ("COMPARABILITY", 4, 5), ("OUTCOME / EXPOSURE", 6, 8)]

NOS_SYMBOLS = {"Low": "+", "Moderate": "?", "High": "−"}


def _contrast_text(color):
    r, g, b = mcolors.to_rgb(color)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "white" if luminance < 0.55 else "#1A1A1A"


def plot_nos_visualization(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors = get_theme_colors(theme)
    n = len(df)

    x_total, x_overall = 9.59, 10.80
    grid_l, grid_r = -0.55, 11.40
    box_l, box_r = grid_l + 0.02, grid_r
    strip_y0, strip_y1 = n + 0.14, n + 0.66
    band_y0, band_y1 = strip_y1, strip_y1 + 0.52
    code_y = n + 0.40
    grid_top, grid_bot = strip_y0, -0.49

    ax_w = (grid_r - grid_l) * 0.95
    ax_h = (band_y1 + 0.10 - grid_bot) * 0.62
    fig_w = ax_w + 2.2
    footer_h = 2.70
    fig_h = 0.95 + ax_h + footer_h + 0.55

    fig = plt.figure(figsize=(fig_w, fig_h))
    ax = fig.add_axes([0.35 / fig_w, (footer_h + 0.55) / fig_h, ax_w / fig_w, ax_h / fig_h])

    y_of = {i: n - 0.675 - i for i in range(n)}

    for rx in [0.5, 1.5, 2.5, 4.5, 6.5, 7.5]:
        ax.vlines(rx, grid_bot, strip_y1, color="#9AA1AA", lw=0.8, zorder=6)
    for rx in [3.5, 5.5, 8.98, 10.20]:
        ax.vlines(rx, grid_bot, strip_y1, color="#6E767F", lw=1.6, zorder=6)
    ax.add_patch(Rectangle((box_l, grid_bot), box_r - box_l, strip_y1 - grid_bot,
                           fill=False, edgecolor="#6E767F", lw=0.9, zorder=6))
    ax.hlines(grid_top, box_l, box_r, color="#9AA1AA", lw=1.0, zorder=1)
    ax.hlines(grid_bot, box_l, box_r, color="#9AA1AA", lw=1.0, zorder=1)

    item_pts, item_cols, item_syms = [], [], []
    overall_pts, overall_cols, overall_syms = [], [], []
    for i, (_, row) in enumerate(df.iterrows()):
        r = y_of[i]
        for c, (col, _, _) in enumerate(NOS_ITEMS):
            risk = "Low" if int(row[col]) == 1 else "High"
            item_pts.append((c, r))
            item_cols.append(colors[risk])
            item_syms.append(NOS_SYMBOLS[risk])
        overall_pts.append((x_overall, r))
        overall_cols.append(colors.get(row["Overall RoB"], "#888888"))
        overall_syms.append(NOS_SYMBOLS.get(row["Overall RoB"], "?"))

    ax.scatter(*zip(*item_pts), s=1150, c=item_cols, edgecolors="none", zorder=3)
    ax.scatter(*zip(*overall_pts), s=1500, c=overall_cols, edgecolors="none", zorder=3)
    force_white_symbols = theme == "traffic_light"
    for (x, y), sym, col in zip(item_pts, item_syms, item_cols):
        ax.text(x, y, sym, ha="center", va="center", fontsize=16, fontweight="bold",
                color="white" if force_white_symbols else _contrast_text(col), zorder=4)
    for (x, y), sym, col in zip(overall_pts, overall_syms, overall_cols):
        ax.text(x, y, sym, ha="center", va="center", fontsize=18, fontweight="bold",
                color="white" if force_white_symbols else _contrast_text(col), zorder=4)

    for i, (_, row) in enumerate(df.iterrows()):
        ax.scatter([x_total], [y_of[i]], s=1600, c=["#E9EDF1"], edgecolors="none", zorder=3)
        ax.text(x_total, y_of[i], f"{int(row['Total Score'])}/9", ha="center", va="center",
                fontsize=12, fontweight="bold", color="#37414B", zorder=4)

    ax.add_patch(Rectangle((box_l, band_y0), box_r - box_l, band_y1 - band_y0,
                           facecolor="#3A3F4A", edgecolor="none", zorder=5))
    for name, c0, c1 in NOS_DOMAINS:
        ax.text((c0 + c1) / 2.0 + 0.02, (band_y0 + band_y1) / 2.0, name, ha="center",
                va="center", fontsize=11, fontweight="bold", color="white", zorder=6)
    ax.text(x_total, (band_y0 + band_y1) / 2.0, "TOTAL", ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", zorder=6)
    ax.text(x_overall, (band_y0 + band_y1) / 2.0, "OVERALL", ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", zorder=6)

    ax.add_patch(Rectangle((box_l, strip_y0), box_r - box_l, strip_y1 - strip_y0,
                           facecolor="#D7DBE0", edgecolor="none", zorder=4))
    for c, (_, code, _) in enumerate(NOS_ITEMS):
        ax.text(c, code_y, code, ha="center", va="center", fontsize=11.5,
                fontweight="bold", color="#1A1A1A", zorder=6)

    ax.set_xlim(grid_l, grid_r + 0.04)
    ax.set_ylim(grid_bot, band_y1 + 0.10)
    ax.set_yticks([y_of[i] for i in range(n)])
    ax.set_yticklabels(df["Author, Year"], fontsize=11.5)
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", length=0, pad=8)

    fig.text(0.52, (fig_h - 0.525) / fig_h, "Newcastle-Ottawa Scale (NOS) Visualization Plot",
             ha="center", va="center", fontsize=18, fontweight="bold", color="#1A1A1A")

    key_ax = fig.add_axes([0.35 / fig_w, 0.20 / fig_h, ax_w / fig_w, footer_h / fig_h])
    key_ax.set_xlim(0, 1)
    key_ax.set_ylim(0, 1)
    key_ax.axis("off")

    key_ax.text(0.02, 0.95, "Domains:", ha="left", va="center", fontsize=14,
                fontweight="bold", color="#1A1A1A")
    y = 0.82
    for _, code, desc in NOS_ITEMS:
        key_ax.text(0.02, y, code, ha="left", va="center", fontsize=14,
                    fontweight="bold", color="#1A1A1A")
        key_ax.text(0.075, y, desc, ha="left", va="center", fontsize=14,
                    fontweight="normal", color="#333333")
        y -= 0.092

    key_ax.add_patch(Rectangle((0.78, 0.40), 0.19, 0.58,
                               facecolor='white', edgecolor='black', linewidth=0.8, zorder=1))
    key_ax.text(0.80, 0.89, "Judgement", ha="left", va="center", fontsize=14,
                fontweight="bold", color="#1A1A1A")
    y = 0.76
    for risk in ["Low", "Moderate", "High"]:
        face = colors[risk]
        key_ax.scatter([0.812], [y], s=500, c=[face], edgecolors="none", zorder=3)
        key_ax.text(0.812, y, NOS_SYMBOLS[risk], ha="center", va="center", fontsize=13,
                    fontweight="bold", color="white" if force_white_symbols else _contrast_text(face), zorder=4)
        key_ax.text(0.845, y, f"{risk} risk", ha="left", va="center", fontsize=13,
                    fontweight="normal", color="#333333")
        y -= 0.14

    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ NOS plot saved to {output_file}")

def read_input_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".csv"]:
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Provide a CSV or Excel file.")

if __name__ == "__main__":
    if len(sys.argv) not in [3,4]:
        print("Usage: python3 nos_tlplot.py input_file output_file.(png|pdf|svg|eps) [theme]")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) == 4 else "traffic_light"

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    df = read_input_file(input_file)
    df = process_detailed_nos(df)
    
    base, ext = os.path.splitext(output_file)
    
    professional_plot(df, output_file, theme)
    plot_domain_radar(df, f"{base}_radar{ext}", theme)
    plot_theme_radar(df, f"{base}_theme_radar{ext}", theme)
    plot_domain_heatmap(df, f"{base}_heatmap{ext}", theme)
    plot_dot_profile(df, f"{base}_dot_profile{ext}", theme)
    plot_score_table(df, f"{base}_table{ext}", theme)
    plot_donut_domain_risk(df, f"{base}_donut{ext}", theme)
    plot_line_ordered_scores(df, f"{base}_line_ordered{ext}", theme)
    plot_lollipop_total(df, f"{base}_lollipop{ext}", theme)
    plot_pie_overall_rob(df, f"{base}_pie{ext}", theme)
    plot_stacked_area_risk(df, f"{base}_stacked_area{ext}", theme)
    plot_nos_visualization(df, f"{base}_nos_plot{ext}", theme)