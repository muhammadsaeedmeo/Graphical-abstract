# streamlit_graphical_abstract_app_v2.py
# Streamlit app for graphical abstracts with richer relationships (overall effects & nonlinear)

import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Graphical Abstract Builder v2", layout="wide")

st.title("Graphical Abstract Builder v2 — more powerful, more nonlinear")
st.markdown("""
Use this app to visualize variable relationships for your paper.  
Now includes **Overall Positive / Negative / Insignificant** and **Nonlinear** relationship options.
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

st.sidebar.header("Input")
upload = st.sidebar.file_uploader("Upload variables CSV (columns: variable, optional region)", type=["csv"])
use_example = st.sidebar.checkbox("Use example variables", value=False)

if upload is not None:
    df = pd.read_csv(upload)
elif use_example:
    df = pd.read_csv(io.StringIO(EXAMPLE_CSV))
else:
    manual = st.sidebar.text_area("Or paste variables (one per line, optional: comma region)", height=120)
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
    dep = st.selectbox("Choose dependent variable", options=df["variable"].tolist())
    inds = st.multiselect("Choose independent variables", [v for v in df["variable"].tolist() if v != dep])
    show_region = st.checkbox("Group variables by region (if available)")
    layout_lr = st.radio("Layout", ["LR (left→right)", "TB (top→bottom)"], index=0)

relationship_options = [
    "Positive", "Negative", "Insignificant",
    "Overall Positive", "Overall Negative", "Overall Insignificant",
    "Nonlinear Relationship"
]

with cols[1]:
    st.write("**Define relationships**")
    rel_map = {}
    for iv in inds:
        rel = st.selectbox(f"Effect of {iv} → {dep}", options=relationship_options, key=f"rel_{iv}")
        rel_map[iv] = rel

st.sidebar.header("Styling & Export")
show_labels = st.sidebar.checkbox("Show arrow labels", value=True)
show_legend = st.sidebar.checkbox("Show legend", value=True)
edge_penwidth = st.sidebar.slider("Arrow thickness", 1, 8, 2)
node_color = st.sidebar.color_picker("Node color", "#FFFFFF")

def build_dot(dep, inds, rel_map, df, show_region, layout):
    lines = ["digraph G {"]
    lines.append(f"  rankdir={'LR' if 'LR' in layout else 'TB'};")
    lines.append("  node [shape=box, style=filled, color=gray, fillcolor=\"{}\", penwidth=1.5, fontname=\"Helvetica\", fontsize=12];".format(node_color))
    lines.append("  edge [fontname=\"Helvetica\", fontsize=10];")

    # Subgraphs by region
    if show_region and df["region"].astype(str).str.strip().any():
        regions = df.set_index("variable")["region"].fillna("").to_dict()
        grouped = {}
        for v, r in regions.items():
            grouped.setdefault(r or "Other", []).append(v)
        for i, (rname, vars_) in enumerate(grouped.items()):
            lines.append(f"  subgraph cluster_{i} {{")
            lines.append(f"    label=\"{rname}\";")
            lines.append("    style=dashed; color=gray;")
            for v in vars_:
                lines.append(f"    \"{v}\";")
            lines.append("  }")
    else:
        for v in df["variable"].tolist():
            lines.append(f"  \"{v}\";")

    def edge_props(rel):
        if rel == "Positive":
            return ("green", "+", "solid")
        if rel == "Negative":
            return ("red", "-", "solid")
        if rel == "Insignificant":
            return ("gray", "ns", "dotted")
        if rel == "Overall Positive":
            return ("darkgreen", "Overall +", "bold")
        if rel == "Overall Negative":
            return ("darkred", "Overall -", "bold")
        if rel == "Overall Insignificant":
            return ("black", "Overall ns", "dashed")
        if rel == "Nonlinear Relationship":
            return ("orange", "Nonlinear", "dashed")
        return ("gray", "?", "dotted")

    for iv in inds:
        color, label, style = edge_props(rel_map.get(iv, "Insignificant"))
        lbl = f" label=\"{label}\"" if show_labels else ""
        lines.append(f"  \"{iv}\" -> \"{dep}\" [color={color}, penwidth={edge_penwidth}, style={style}{lbl}];")

    if show_legend:
        lines.append("  subgraph cluster_legend {")
        lines.append("    label=\"Legend\";")
        lines.append("    key [shape=note, label=\""
                     "+ : Positive\\n- : Negative\\nns : Insignificant\\nOverall +/- : Aggregate Effect\\nNonlinear : Curved/Complex Relation\", fontsize=10];")
        lines.append("  }")

    lines.append("}")
    return "\n".join(lines)

dot = build_dot(dep, inds, rel_map, df, show_region, layout_lr)

st.subheader("Graph Preview")
st.graphviz_chart(dot)

b = dot.encode("utf-8")
st.download_button("Download .dot file", data=b, file_name="graphical_abstract_v2.dot", mime="text/vnd.graphviz")

try:
    import graphviz
    svg = graphviz.Source(dot).pipe(format="svg")
    st.download_button("Download SVG", data=svg, file_name="graphical_abstract_v2.svg", mime="image/svg+xml")
    png = graphviz.Source(dot).pipe(format="png")
    st.download_button("Download PNG", data=png, file_name="graphical_abstract_v2.png", mime="image/png")
except Exception:
    st.info("SVG/PNG export unavailable. Install 'graphviz' system package and Python library.")

st.markdown("---")
st.caption("Graphical Abstract Builder v2 — because regression tables deserve prettier friends.")
