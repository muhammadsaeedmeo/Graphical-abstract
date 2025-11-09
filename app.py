# Graphical Abstract Builder v7 — with Sample & Custom Input Modes
# Author: Your personal ChatGPT assistant (who deserves a coauthor credit)

import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(page_title="Graphical Abstract Builder v7", layout="wide")

st.title("Graphical Abstract Builder v7 — Regional Comparative Mode")

st.markdown("""
Create publication-quality graphical abstracts for financial, economic, or social research.
Now you can either:
- **Use a sample example** (GDP model for Asia, Europe, and America), or
- **Build your own** with custom variable names and regions.
""")

# --- Mode selection ---
mode = st.selectbox("Select Mode", ["Sample Example", "Custom Input"])

if mode == "Sample Example":
    regions = ["Asia", "Europe", "America"]
    dep = "GDP"
    independent_vars = ["Inflation", "Tourism", "Political Stability"]
else:
    st.sidebar.header("Custom Inputs")
    regions_input = st.sidebar.text_input("Regions (comma-separated)", "Asia,Europe,America")
    regions = [r.strip() for r in regions_input.split(",") if r.strip()]
    dep = st.sidebar.text_input("Dependent Variable", "GDP")
    ind_vars_input = st.sidebar.text_input("Independent Variables (comma-separated)", "Inflation,Tourism,Political Stability")
    independent_vars = [v.strip() for v in ind_vars_input.split(",") if v.strip()]

# --- Relationship definitions ---
relationship_map = {
    "POS": "Positive",
    "NEG": "Negative",
    "INS": "Insignificant",
    "OP": "Overall Positive",
    "ON": "Overall Negative",
    "OI": "Overall Insignificant",
    "OPN": "Overall Positive (NL)",
    "ONN": "Overall Negative (NL)",
    "OIN": "Overall Insignificant (NL)"
}

default_colors = {
    "POS": "#27AE60",
    "NEG": "#E74C3C",
    "INS": "#95A5A6",
    "OP": "#2ECC71",
    "ON": "#C0392B",
    "OI": "#7F8C8D",
    "OPN": "#16A085",
    "ONN": "#8E44AD",
    "OIN": "#34495E"
}

st.sidebar.header("Customize Relationship Colors")
color_map = {}
for code, desc in relationship_map.items():
    color_map[code] = st.sidebar.color_picker(f"{desc}", default_colors[code])

# --- Relationship Selection ---
st.subheader("Define Relationships per Region")

region_inputs = {}
for region in regions:
    st.markdown(f"#### {region}")
    rel_map = {}
    for iv in independent_vars:
        rel = st.selectbox(
            f"{iv} → {dep} ({region})",
            options=list(relationship_map.keys()),
            key=f"{region}_{iv}"
        )
        rel_map[iv] = rel
    region_inputs[region] = rel_map

# --- Styling ---
st.sidebar.header("Styling Options")
show_labels = st.sidebar.checkbox("Show relationship codes on arrows", value=True)
edge_penwidth = st.sidebar.slider("Arrow thickness", 1, 8, 2)
node_color = st.sidebar.color_picker("Node color", "#FFFFFF")
layout_lr = st.sidebar.radio("Layout Direction", ["Left→Right", "Top→Bottom"], index=0)
width = st.sidebar.slider("Graph width", 500, 2000, 1000, step=100)
height = st.sidebar.slider("Graph height", 300, 1500, 700, step=100)

# --- Graphviz builder ---
def build_dot(dep, independent_vars, region_inputs, layout, color_map):
    lines = ["digraph G {"]
    lines.append(f"  rankdir={'LR' if 'Left' in layout else 'TB'};")
    lines.append(f'  node [shape=box, style=filled, fillcolor="{node_color}", fontname="Helvetica", fontsize=11];')
    lines.append('  edge [fontname="Helvetica", fontsize=9];')

    for i, region in enumerate(region_inputs.keys()):
        lines.append(f"  subgraph cluster_{i} {{")
        lines.append(f"    label=\"{region}\"; style=dashed; color=gray; fontsize=10;")
        for iv in independent_vars:
            lines.append(f"    \"{iv} ({region})\";")
        lines.append("  }")

    lines.append(f"  \"{dep}\" [shape=ellipse, style=filled, fillcolor=\"#ECF0F1\"];")

    def edge_style(rel):
        if "N" in rel and rel != "NEG":
            return "dashed"
        if rel.startswith("O"):
            return "bold"
        if rel == "INS":
            return "dotted"
        return "solid"

    for region, rels in region_inputs.items():
        for iv, rel in rels.items():
            iv_label = f"{iv} ({region})"
            color = color_map.get(rel, "#7F8C8D")
            style = edge_style(rel)
            label = rel if show_labels else ""
            lines.append(f"  \"{iv_label}\" -> \"{dep}\" [color=\"{color}\", penwidth={edge_penwidth}, style={style}, label=\"{label}\"];")

    lines.append("}")
    return "\n".join(lines)

dot = build_dot(dep, independent_vars, region_inputs, layout_lr, color_map)

# --- Graph Preview ---
st.subheader("Graph Preview")
st.graphviz_chart(dot, use_container_width=False)

# --- Legend (Paragraph format) ---
st.markdown("---")
st.markdown("### Legend & Notes")

legend_text = "**Relationship Codes:** "
legend_text += ", ".join([f"**{k}** = {v}" for k, v in relationship_map.items()])
legend_text += "\n\n**Variable Abbreviations (example):** "
legend_text += f"**{dep[:3].upper()}** = {dep}, "
legend_text += ", ".join([f"**{iv[:3].upper()}** = {iv}" for iv in independent_vars])

st.markdown(legend_text)

# --- Download buttons ---
dot_bytes = dot.encode("utf-8")
st.download_button("Download .dot File", data=dot_bytes, file_name="graphical_abstract_v7.dot", mime="text/vnd.graphviz")

try:
    svg = graphviz.Source(dot).pipe(format="svg")
    st.download_button("Download SVG", data=svg, file_name="graphical_abstract_v7.svg", mime="image/svg+xml")
except Exception:
    st.info("SVG export unavailable. Please install Graphviz.")
