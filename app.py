# streamlit_GA_v4.py

import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Graphical Abstract Builder v4", layout="wide")

st.title("Graphical Abstract Builder v4 — regional smart layout")

st.markdown("""
This version adds:
- Short relationship codes (no more label clutter)
- Paragraph-style legend (bottom of the graph)
- Regional differentiation (same variable name, different region)
- Color customization for all relationships
""")

# --- Example CSV ---
EXAMPLE_CSV = """variable,region
GDP,Asia
GDP,Africa
Tourism,Asia
Tourism,Africa
GreenBonds,Asia
Inflation,Europe
FDI,Africa
Trade,Europe
"""

with st.expander("📄 Example CSV format (variable,region)"):
    st.code(EXAMPLE_CSV)

# --- Sidebar Input ---
st.sidebar.header("Input Data")
upload = st.sidebar.file_uploader("Upload CSV (variable, region)", type=["csv"])
use_example = st.sidebar.checkbox("Use example variables", value=True)

if upload is not None:
    df = pd.read_csv(upload)
elif use_example:
    df = pd.read_csv(io.StringIO(EXAMPLE_CSV))
else:
    manual = st.sidebar.text_area("Or paste variables (comma-separated: var,region)", height=120)
    if manual.strip():
        rows = []
        for line in manual.splitlines():
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(",")]
            rows.append({"variable": parts[0], "region": parts[1] if len(parts) > 1 else ""})
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame(columns=["variable", "region"])

if "variable" not in df.columns:
    df["variable"] = []
if "region" not in df.columns:
    df["region"] = ""

if df.empty:
    st.warning("Please upload or input variables first.")
    st.stop()

# --- Variable + Region Control ---
df["unique_name"] = df.apply(lambda x: f"{x['variable']} ({x['region']})" if pd.notnull(x["region"]) and x["region"] else x["variable"], axis=1)

cols = st.columns([1.2, 1.8])
with cols[0]:
    dep = st.selectbox("Dependent Variable", options=df["unique_name"].tolist())
    inds = st.multiselect("Independent Variables", [v for v in df["unique_name"].tolist() if v != dep])
    show_region = st.checkbox("Show regions as subclusters", value=True)
    layout_lr = st.radio("Layout Direction", ["Left→Right", "Top→Bottom"], index=0)

# --- Relationship Types (short labels) ---
relationship_map = {
    "POS": "Positive relationship",
    "NEG": "Negative relationship",
    "INS": "Insignificant relationship",
    "OP": "Overall Positive",
    "ON": "Overall Negative",
    "OI": "Overall Insignificant",
    "NL": "Nonlinear relationship",
    "OPN": "Overall Positive (Nonlinear)",
    "ONN": "Overall Negative (Nonlinear)",
    "OIN": "Overall Insignificant (Nonlinear)"
}

default_colors = {
    "POS": "#27AE60",
    "NEG": "#E74C3C",
    "INS": "#95A5A6",
    "OP": "#2ECC71",
    "ON": "#C0392B",
    "OI": "#7F8C8D",
    "NL": "#F39C12",
    "OPN": "#16A085",
    "ONN": "#8E44AD",
    "OIN": "#34495E"
}

st.sidebar.header("Customize Relationship Colors")
color_map = {}
for code, desc in relationship_map.items():
    color_map[code] = st.sidebar.color_picker(f"{desc}", default_colors[code])

# --- Define Relationships ---
with cols[1]:
    st.write("**Define Relationships**")
    rel_map = {}
    for iv in inds:
        rel = st.selectbox(f"Effect of {iv} → {dep}", options=list(relationship_map.keys()), key=f"rel_{iv}")
        rel_map[iv] = rel

# --- Styling ---
st.sidebar.header("Styling Options")
show_labels = st.sidebar.checkbox("Show relationship codes on arrows", value=True)
edge_penwidth = st.sidebar.slider("Arrow thickness", 1, 8, 2)
node_color = st.sidebar.color_picker("Node color", "#FFFFFF")

# --- Graphviz Builder ---
def build_dot(dep, inds, rel_map, df, show_region, layout, color_map):
    lines = ["digraph G {"]
    lines.append(f"  rankdir={'LR' if 'Left' in layout else 'TB'};")
    lines.append(f'  node [shape=box, style=filled, fillcolor="{node_color}", fontname="Helvetica", fontsize=11];')
    lines.append('  edge [fontname="Helvetica", fontsize=9];')

    # Subgraph per region
    if show_region and df["region"].astype(str).str.strip().any():
        grouped = df.groupby("region")["unique_name"].apply(list).to_dict()
        for i, (region, vars_) in enumerate(grouped.items()):
            if not region or region.strip() == "":
                continue
            lines.append(f"  subgraph cluster_{i} {{")
            lines.append(f"    label=\"{region}\"; style=dashed; color=gray; fontsize=10;")
            for v in vars_:
                lines.append(f"    \"{v}\";")
            lines.append("  }")
    else:
        for v in df["unique_name"].tolist():
            lines.append(f"  \"{v}\";")

    # Edge style logic
    def edge_style(rel):
        if "N" in rel and rel != "NEG":
            return "dashed"
        if rel.startswith("O"):
            return "bold"
        if rel == "INS":
            return "dotted"
        return "solid"

    for iv in inds:
        rel = rel_map.get(iv, "INS")
        color = color_map.get(rel, "#7F8C8D")
        label = rel if show_labels else ""
        style = edge_style(rel)
        lines.append(f"  \"{iv}\" -> \"{dep}\" [color=\"{color}\", penwidth={edge_penwidth}, style={style}, label=\"{label}\"];")

    lines.append("}")
    return "\n".join(lines)

dot = build_dot(dep, inds, rel_map, df, show_region, layout_lr, color_map)

st.subheader("Graph Preview")
st.graphviz_chart(dot)

# --- Legend Paragraph ---
legend_text = "### Legend\n"
legend_text += "Below are the short relationship codes used:\n\n"
for code, desc in relationship_map.items():
    legend_text += f"**{code}** = {desc}\n\n"

st.markdown("---")
st.markdown(legend_text)

# --- Download options ---
dot_bytes = dot.encode("utf-8")
st.download_button("Download .dot File", data=dot_bytes, file_name="graphical_abstract_v4.dot", mime="text/vnd.graphviz")

try:
    import graphviz
    svg = graphviz.Source(dot).pipe(format="svg")
    st.download_button("Download SVG", data=svg, file_name="graphical_abstract_v4.svg", mime="image/svg+xml")
except Exception:
    st.info("SVG export unavailable. Install system graphviz + Python graphviz package.")
