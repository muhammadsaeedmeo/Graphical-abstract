# Graphical Abstract Builder v11 — Radial Layout + PNG Download
# Author: ChatGPT & Dr. Meo

import streamlit as st
import pandas as pd
import graphviz
from io import BytesIO
import os

# --- FIX: Add Graphviz to PATH ---
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

st.set_page_config(page_title="Graphical Abstract Builder v11", layout="wide")

# --- Password Gate ---
st.markdown("### 🔒 Secure Access")
password = st.text_input("Enter password to access the app:", type="password")

if password != "1992":
    st.warning("Access Denied. Please enter the correct password.")
    st.stop()

st.success("Access Granted — Welcome to the Graphical Abstract Builder v11!")

st.title("Graphical Abstract Builder v11 — 360° Radial Mode with PNG Download")

st.markdown("""
Create professional **radial graphical abstracts** for research.
Now includes:
- Password protection  
- Central dependent variable layout  
- 360° connections from independent variables  
- Gradient or solid background  
- Real **SVG/PNG/DOT** export  
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
width = st.sidebar.slider("Graph width", 500, 2000, 1000, step=100)
height = st.sidebar.slider("Graph height", 300, 1500, 700, step=100)

# --- Graphviz builder (Radial) ---
def build_radial_dot(dep, independent_vars, region_inputs, color_map):
    lines = ['graph [layout=neato, overlap=false, outputorder=edgesfirst, splines=true];']
    lines.append('digraph G {')
    lines.append(f'  layout=neato;')
    lines.append(f'  node [shape=box, style=filled, fillcolor="{node_color}", fontname="Helvetica", fontsize=11];')
    lines.append('  edge [fontname="Helvetica", fontsize=9];')

    # Background
    if bg_mode == "Gradient":
        lines.append(f'  graph [style=filled, fillcolor="{bg_color1}:{bg_color2}", gradientangle=270];')
    else:
        lines.append(f'  graph [style=filled, fillcolor="{bg_color1}"];')

    # Central node
    lines.append(f'  "{dep}" [shape=ellipse, width=2.5, height=1.2, style=filled, fillcolor="#ECF0F1", pos="0,0!"];')

    # Place independent variables radially
    import math
    total_vars = len(independent_vars) * len(region_inputs)
    radius = 4.0

    idx = 0
    for r_i, (region, rels) in enumerate(region_inputs.items()):
        angle_offset = (2 * math.pi / len(region_inputs)) * r_i
        for iv_i, iv in enumerate(independent_vars):
            angle = angle_offset + (2 * math.pi / len(independent_vars)) * iv_i / len(region_inputs)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            node_name = f"{iv} ({region})"
            lines.append(f'  "{node_name}" [pos="{x},{y}!", shape=box];')

    # Arrows from IVs to Dependent
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
            color = color_map.get(rel, "#7F8C8D")
            style = edge_style(rel)
            label = rel if show_labels else ""
            lines.append(f'  "{iv} ({region})" -> "{dep}" [color="{color}", penwidth={edge_penwidth}, style={style}, label="{label}"];')

    lines.append("}")
    return "\n".join(lines)

dot = build_radial_dot(dep, independent_vars, region_inputs, color_map)

# --- Graph Preview ---
st.subheader("Radial Graph Preview")
st.graphviz_chart(dot, use_container_width=False)

# --- Legend ---
st.markdown("---")
st.markdown("### Legend & Notes")

legend_text = "**Relationship Codes:** "
legend_text += ", ".join([f"**{k}** = {v}" for k, v in relationship_map.items()])
legend_text += "\n\n**Variable Abbreviations (example):** "
legend_text += f"**{dep[:3].upper()}** = {dep}, "
legend_text += ", ".join([f"**{iv[:3].upper()}** = {iv}" for iv in independent_vars])
st.markdown(legend_text)

# --- Download buttons ---
try:
    graph_obj = graphviz.Source(dot, engine="neato")
    svg_data = graph_obj.pipe(format='svg')
    png_data = graph_obj.pipe(format='png')

    st.download_button("📥 Download .SVG", data=svg_data, file_name="graphical_abstract_v11.svg", mime="image/svg+xml")
    st.download_button("📥 Download .PNG", data=png_data, file_name="graphical_abstract_v11.png", mime="image/png")

    st.success("✓ PNG/SVG downloads are fully operational!")

except Exception as e:
    st.error(f"Download error: {e}")
    st.info("Ensure Graphviz (neato) is correctly installed and added to PATH.")

# Always allow DOT download
dot_bytes = dot.encode("utf-8")
st.download_button("📄 Download .DOT", data=dot_bytes, file_name="graphical_abstract_v11.dot", mime="text/vnd.graphviz")
