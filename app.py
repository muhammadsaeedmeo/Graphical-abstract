# streamlit_graphical_abstract_app_v3.py
# Extended version with nonlinear overall relationships, custom color pickers, and improved legend

import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Graphical Abstract Builder v3", layout="wide")

st.title("Graphical Abstract Builder v3 — nonlinear elegance meets control")
st.markdown("""
Now with:
- Distinct colors for each relationship type  
- Custom color pickers  
- Legend aligned horizontally at the bottom  
- New nonlinear overall relationship types
""")

EXAMPLE_CSV = """variable,region
GDP,Asia
Tourism,Asia
GreenBonds,Asia
Inflation,Asia
FDI,Africa
Trade,Africa
PolicyIndex,Europe
"""

with st.expander("📄 Example CSV format (variable,region)"):
    st.code(EXAMPLE_CSV)

# --- Sidebar Input ---
st.sidebar.header("Input")
upload = st.sidebar.file_uploader("Upload CSV (columns: variable, optional region)", type=["csv"])
use_example = st.sidebar.checkbox("Use example variables", value=False)

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

cols = st.columns([1.2, 1.8])
with cols[0]:
    dep = st.selectbox("Dependent Variable", options=df["variable"].tolist())
    inds = st.multiselect("Independent Variables", [v for v in df["variable"].tolist() if v != dep])
    show_region = st.checkbox("Group variables by region (if available)")
    layout_lr = st.radio("Layout", ["LR (left→right)", "TB (top→bottom)"], index=0)

relationship_options = [
    "Positive", "Negative", "Insignificant",
    "Overall Positive", "Overall Negative", "Overall Insignificant",
    "Nonlinear Relationship",
    "Overall Positive but Nonlinear",
    "Overall Negative but Nonlinear",
    "Overall Insignificant but Nonlinear"
]

# Default color dictionary
default_colors = {
    "Positive": "#2ECC71",
    "Negative": "#E74C3C",
    "Insignificant": "#95A5A6",
    "Overall Positive": "#27AE60",
    "Overall Negative": "#C0392B",
    "Overall Insignificant": "#7F8C8D",
    "Nonlinear Relationship": "#F39C12",
    "Overall Positive but Nonlinear": "#16A085",
    "Overall Negative but Nonlinear": "#8E44AD",
    "Overall Insignificant but Nonlinear": "#34495E"
}

# --- Relationship color customization ---
st.sidebar.header("Customize Relationship Colors")
color_map = {}
for rel in relationship_options:
    color_map[rel] = st.sidebar.color_picker(f"{rel} Color", default_colors[rel])

with cols[1]:
    st.write("**Define Relationships**")
    rel_map = {}
    for iv in inds:
        rel = st.selectbox(f"Effect of {iv} → {dep}", options=relationship_options, key=f"rel_{iv}")
        rel_map[iv] = rel

st.sidebar.header("Styling & Export")
show_labels = st.sidebar.checkbox("Show arrow labels", value=True)
edge_penwidth = st.sidebar.slider("Arrow thickness", 1, 8, 2)
node_color = st.sidebar.color_picker("Node fill color", "#FFFFFF")

# --- DOT Builder Function ---
def build_dot(dep, inds, rel_map, df, show_region, layout, color_map):
    lines = ["digraph G {"]
    lines.append(f"  rankdir={'LR' if 'LR' in layout else 'TB'};")
    lines.append('  node [shape=box, style=filled, color=gray, fillcolor="{}", fontname="Helvetica", fontsize=12];'.format(node_color))
    lines.append('  edge [fontname="Helvetica", fontsize=10];')

    # Regions
    if show_region and df["region"].astype(str).str.strip().any():
        regions = df.set_index("variable")["region"].fillna("").to_dict()
        grouped = {}
        for v, r in regions.items():
            grouped.setdefault(r or "Other", []).append(v)
        for i, (rname, vars_) in enumerate(grouped.items()):
            lines.append(f"  subgraph cluster_{i} {{")
            lines.append(f"    label=\"{rname}\"; style=dashed; color=gray;")
            for v in vars_:
                lines.append(f"    \"{v}\";")
            lines.append("  }")
    else:
        for v in df["variable"].tolist():
            lines.append(f"  \"{v}\";")

    # Arrow style logic
    def edge_style(rel):
        if "Nonlinear" in rel:
            return "dashed"
        if "Overall" in rel:
            return "bold"
        if rel == "Insignificant":
            return "dotted"
        return "solid"

    for iv in inds:
        rel = rel_map.get(iv, "Insignificant")
        color = color_map.get(rel, "#7F8C8D")
        label = rel if show_labels else ""
        style = edge_style(rel)
        lines.append(f"  \"{iv}\" -> \"{dep}\" [color=\"{color}\", penwidth={edge_penwidth}, style={style}, label=\"{label}\"];")

    # Bottom legend (horizontal)
    lines.append("  { rank=sink;")
    lines.append("    LegendNode [shape=none, margin=0, label=<")
    lines.append("    <TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\" CELLPADDING=\"4\">")
    lines.append("      <TR><TD COLSPAN=\"2\"><B>Legend</B></TD></TR>")
    for rel, color in color_map.items():
        lines.append(f"      <TR><TD BGCOLOR=\"{color}\"></TD><TD>{rel}</TD></TR>")
    lines.append("    </TABLE>>]; }")

    lines.append("}")
    return "\n".join(lines)

dot = build_dot(dep, inds, rel_map, df, show_region, layout_lr, color_map)

# --- Display Graph ---
st.subheader("Graph Preview")
st.graphviz_chart(dot)

b = dot.encode("utf-8")
st.download_button("Download .dot file", data=b, file_name="graphical_abstract_v3.dot", mime="text/vnd.graphviz")

try:
    import graphviz
    svg = graphviz.Source(dot).pipe(format="svg")
    st.download_button("Download SVG", data=svg, file_name="graphical_abstract_v3.svg", mime="image/svg+xml")
except Exception:
    st.info("SVG export unavailable. Install 'graphviz' system package and Python library.")

st.markdown("---")
st.caption("Graphical Abstract Builder v3 — where your regressions finally get some visual respect.")
