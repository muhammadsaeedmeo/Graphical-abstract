# Graphical Abstract Builder v12 — Radial Plotly Version (No Graphviz)
# Author: ChatGPT & Dr. Meo

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math
from io import BytesIO

st.set_page_config(page_title="Graphical Abstract Builder v12", layout="wide")

# --- Password Gate ---
st.markdown("### 🔒 Secure Access")
password = st.text_input("Enter password to access the app:", type="password")

if password != "1992":
    st.warning("Access Denied. Please enter the correct password.")
    st.stop()

st.success("Access Granted — Welcome to the Graphical Abstract Builder v12!")

st.title("Graphical Abstract Builder v12 — Radial Layout (No Graphviz)")

st.markdown("""
Create professional **radial graphical abstracts** for research.
This version:
- Doesn't need Graphviz  
- Central dependent variable layout  
- 360° independent variable links  
- Downloadable as **PNG or SVG**  
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

# --- Background & style ---
bg_color = st.sidebar.color_picker("Background Color", "#FFFFFF")
show_labels = st.sidebar.checkbox("Show relationship codes on arrows", value=True)
edge_width = st.sidebar.slider("Arrow thickness", 1, 8, 2)
node_color = st.sidebar.color_picker("Node color", "#FFFFFF")
text_color = st.sidebar.color_picker("Text color", "#000000")

# --- Relationship input ---
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

# --- Compute radial coordinates ---
radius = 2.5
num_points = len(independent_vars) * len(regions)
angle_step = 2 * math.pi / num_points

nodes = []
edges = []
idx = 0

# Central dependent variable
nodes.append({
    "x": 0,
    "y": 0,
    "label": dep,
    "color": "#ECF0F1",
    "size": 20
})

for region, rels in region_inputs.items():
    for iv, rel in rels.items():
        angle = idx * angle_step
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        color = color_map.get(rel, "#7F8C8D")
        label = rel if show_labels else ""
        nodes.append({
            "x": x, "y": y, "label": f"{iv} ({region})",
            "color": node_color, "size": 14
        })
        edges.append({
            "x0": x, "y0": y, "x1": 0, "y1": 0,
            "color": color, "width": edge_width, "label": label
        })
        idx += 1

# --- Build Plotly figure ---
fig = go.Figure()

# Edges
for e in edges:
    fig.add_trace(go.Scatter(
        x=[e["x0"], e["x1"]],
        y=[e["y0"], e["y1"]],
        mode="lines+text" if e["label"] else "lines",
        line=dict(color=e["color"], width=e["width"]),
        text=[None, e["label"]],
        textposition="middle left",
        hoverinfo="none"
    ))

# Nodes
for n in nodes:
    fig.add_trace(go.Scatter(
        x=[n["x"]],
        y=[n["y"]],
        mode="markers+text",
        marker=dict(size=n["size"], color=n["color"], line=dict(width=1, color="#34495E")),
        text=[n["label"]],
        textposition="bottom center",
        textfont=dict(color=text_color),
        hoverinfo="text"
    ))

fig.update_layout(
    showlegend=False,
    plot_bgcolor=bg_color,
    paper_bgcolor=bg_color,
    xaxis=dict(showgrid=False, zeroline=False, visible=False),
    yaxis=dict(showgrid=False, zeroline=False, visible=False),
    width=900, height=700,
    margin=dict(l=10, r=10, t=20, b=10)
)

st.subheader("Radial Abstract Preview")
st.plotly_chart(fig, use_container_width=False)

# --- Downloads ---
from PIL import Image
import io

st.markdown("### Download Options")

# Save Plotly as PNG
png_buf = io.BytesIO()
fig.write_image(png_buf, format="png")
st.download_button("📥 Download as PNG", data=png_buf.getvalue(),
                   file_name="graphical_abstract_v12.png", mime="image/png")

# Save Plotly as SVG
svg_buf = io.BytesIO()
fig.write_image(svg_buf, format="svg")
st.download_button("📥 Download as SVG", data=svg_buf.getvalue(),
                   file_name="graphical_abstract_v12.svg", mime="image/svg+xml")

st.success("✓ No Graphviz required. PNG/SVG downloads are live.")
