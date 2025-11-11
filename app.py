# Graphical Abstract Builder v10 — Password Protected + Viewing Mode
# Author: ChatGPT & Dr. Meo

import streamlit as st
import pandas as pd
import graphviz
from io import BytesIO
import os

# --- FIX: Add Graphviz to PATH ---
# Note: This line is platform-specific and might need adjustment for users without Graphviz installed locally.
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

st.set_page_config(page_title="Graphical Abstract Builder v10", layout="wide")

# --- Password Gate ---
st.markdown("### 🔒 Secure Access")
password = st.text_input("Enter password to access the app:", type="password")

if password != "1992":
    st.warning("Access Denied. Please enter the correct password.")
    st.stop()

st.success("Access Granted — Welcome to the Graphical Abstract Builder v10!")

st.title("Graphical Abstract Builder v10 — Regional Comparative Mode with Centralized DV")

st.markdown("""
Create professional graphical abstracts for research.
This version features a **centralized Dependent Variable (DV)** with surrounding **Independent Variables (IVs)** for a visually appealing, radial layout.
""")

# --- Mode selection ---
mode = st.selectbox("Select Mode", ["Sample Example", "Custom Input"])

if mode == "Sample Example":
    regions = ["Asia", "Europe", "America"]
    dep = "GDP"
    independent_vars = ["Inflation", "Tourism", "Political Stability", "Trade Openness", "Exchange Rate"] # Added more for better center effect
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

# --- Background Controls ---
st.sidebar.header("Background Settings")
bg_mode = st.sidebar.radio("Background Type", ["Solid", "Gradient"], index=0)
bg_color1 = st.sidebar.color_picker("Primary Background Color", "#FFFFFF")
if bg_mode == "Gradient":
    bg_color2 = st.sidebar.color_picker("Secondary Background Color (for gradient)", "#F0F3F4")
else:
    bg_color2 = bg_color1

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
# Removed layout_lr radio since the layout is now forced to be radial/TB for centering.
# Removed width/height sliders to let Graphviz handle best fit for the radial layout.

# --- Graphviz builder (MODIFIED) ---
def build_dot(dep, independent_vars, region_inputs, color_map):
    lines = ["digraph G {"]
    # Force layout to Top-Bottom for central DV placement
    lines.append("  rankdir=TB;") 
    # Use splines=curved or ortho to improve pathing around the central node
    lines.append("  splines=curved;")
    lines.append(f'  node [shape=box, style=filled, fillcolor="{node_color}", fontname="Helvetica", fontsize=11];')
    lines.append('  edge [fontname="Helvetica", fontsize=9];')

    if bg_mode == "Gradient":
        lines.append(f'  graph [style=filled, fillcolor="{bg_color1}:{bg_color2}", gradientangle=270, nodesep=0.6];')
    else:
        lines.append(f'  graph [style=filled, fillcolor="{bg_color1}", nodesep=0.6];')
    
    # 1. Place Independent Variables (IVs) in one rank/cluster (Top Rank)
    iv_nodes = []
    for iv in independent_vars:
        # Create a single node for the IV name, which will link to the DV
        iv_nodes.append(f'"{iv}" [label="{iv}"];')
    lines.append("  subgraph cluster_IVs {")
    lines.append("    rank=min;") # Pushes IVs to the top/outer edge
    lines.append("    style=invis;")
    lines.extend([f"    {node}" for node in iv_nodes])
    lines.append("  }")

    # 2. Place Dependent Variable (DV) in a separate central rank
    lines.append(f"  \"{dep}\" [shape=ellipse, style=filled, fillcolor=\"#ECF0F1\", label=\"{dep}\"];")
    lines.append(f"  {{rank=same; \"{dep}\";}}") # Explicitly define the rank for centrality (optional, but helps)

    # 3. Create regional subgraphs (for IV labels)
    for i, region in enumerate(region_inputs.keys()):
        # We use 'subgraph' for the label/box, but the actual IV nodes are outside for the central flow
        lines.append(f"  subgraph cluster_region_{i} {{")
        lines.append(f"    label=\"{region}\"; style=dashed; color=gray; fontsize=10;")
        # Link the regional IV nodes to the central DV node
        for iv in independent_vars:
            lines.append(f"    \"Region_{region}_{iv}\" [label=\"{region} {iv}\", shape=plaintext, style=invis, width=0.1, height=0.1];")
            # Connect the IV node to the hidden regional node to help group/organize.
            lines.append(f'"{iv}" -> "Region_{region}_{iv}" [style=invis];')
        lines.append("  }")

    def edge_style(rel):
        if "N" in rel and rel != "NEG":
            return "dashed"
        if rel.startswith("O"):
            return "bold"
        if rel == "INS":
            return "dotted"
        return "solid"

    # 4. Draw edges from IVs to DV
    for region, rels in region_inputs.items():
        for iv, rel in rels.items():
            color = color_map.get(rel, "#7F8C8D")
            style = edge_style(rel)
            label = rel if show_labels else ""
            # Draw edge from IV to DV
            lines.append(f"  \"{iv}\" -> \"{dep}\" [color=\"{color}\", penwidth={edge_penwidth}, style={style}, label=\"{label}\", headlabel=\"{region}\"];")
            # Use headlabel or taillabel to put the region text on the edge, or keep it in the cluster label.
            # Using headlabel in this way might clutter it; sticking to the cluster label is usually cleaner.

    lines.append("}")
    return "\n".join(lines)

# --- Update build_dot call ---
dot = build_dot(dep, independent_vars, region_inputs, color_map)

# --- Graph Preview ---
st.subheader("Graph Preview (Centralized Layout)")
# Use the full width for the centralized plot
st.graphviz_chart(dot, use_container_width=True)

# --- Instructions for Screenshot ---
st.markdown("""
<br>
### 📸 Screenshot Instructions
To save the graph, you can use your operating system's built-in screenshot tool (Snipping Tool on Windows, Screenshot on macOS) to capture the preview above.
""", unsafe_allow_html=True)


# --- Legend ---
st.markdown("---")
st.markdown("### Legend & Notes")

legend_text = "**Relationship Codes:** "
legend_text += ", ".join([f"**{k}** = {v}" for k, v in relationship_map.items()])
legend_text += "\n\n**Variable Abbreviations (example):** "
legend_text += f"**{dep[:3].upper()}** = {dep}, "
legend_text += ", ".join([f"**{iv[:3].upper()}** = {iv}" for iv in independent_vars])

st.markdown(legend_text)

# --- Removed Download buttons as requested ---
st.markdown("---")
st.info("Download functionality has been removed as requested. Please use a screenshot tool.")
