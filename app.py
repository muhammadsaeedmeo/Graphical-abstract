# streamlit_graphical_abstract_app.py
# Streamlit app to build graphical abstracts for papers: choose dependent/independent variables,
# mark relationships (positive / negative / insignificant), optionally group variables by region,
# and render an arrow diagram. Also includes a small utility to write requirements.txt.

import streamlit as st
import pandas as pd
import io
import base64

st.set_page_config(page_title="Graphical Abstract Builder", layout="wide")

st.title("Graphical Abstract Builder — because figures speak louder than your abstract")
st.markdown("Upload a CSV of your variables or enter them manually. Then pick a dependent variable,\nselect independents, and mark whether each effect is positive, negative or insignificant.")

# Helper: default example dataframe
EXAMPLE_CSV = """variable,region
GDP,Asia
Tourism,Asia
GreenBonds,Asia
Inflation,Asia
FDI,Africa
Trade,Africa
PolicyIndex,Europe
"""

with st.expander("📄 Example CSV / format (variable,region)"):
    st.code(EXAMPLE_CSV)

# Data input: upload or paste or use example
st.sidebar.header("Input")
upload = st.sidebar.file_uploader("Upload variables CSV (columns: variable, optional: region)", type=["csv"]) 
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
            if len(parts) == 1:
                rows.append({"variable": parts[0], "region": ""})
            else:
                rows.append({"variable": parts[0], "region": parts[1]})
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame(columns=["variable", "region"])

if "variable" not in df.columns:
    if df.shape[1] >= 1:
        df = df.rename(columns={df.columns[0]: "variable"})
    else:
        df["variable"] = []

if "region" not in df.columns:
    df["region"] = ""

st.sidebar.markdown(f"**Loaded variables:** {len(df)}")

if df.empty:
    st.warning("No variables provided yet. Paste variables or upload a CSV, or tick 'Use example variables'.")
    st.stop()

cols = st.columns([1,2])
with cols[0]:
    dep = st.selectbox("Choose dependent variable", options=df['variable'].tolist())
    inds = st.multiselect("Choose independent variables", options=[v for v in df['variable'].tolist() if v != dep])
    show_region = st.checkbox("Group variables by region (if region info provided)")
    layout_lr = st.radio("Layout direction", options=["LR (left->right)", "TB (top->bottom)"], index=0)

with cols[1]:
    st.write("**Mark relationships**")
    rel_map = {}
    for iv in inds:
        rel = st.selectbox(f"Effect of {iv} → {dep}", options=["Positive", "Negative", "Insignificant"], index=0, key=f"rel_{iv}")
        rel_map[iv] = rel

st.sidebar.header("Styling & Export")
show_labels = st.sidebar.checkbox("Show sign labels on arrows", value=True)
show_legend = st.sidebar.checkbox("Show legend", value=True)
edge_penwidth = st.sidebar.slider("Arrow thickness", 1, 8, 2)

def build_dot(dep, inds, rel_map, df, show_region, layout):
    lines = []
    lines.append(f"digraph G {{")
    lines.append(f"  rankdir={ 'LR' if layout=='LR (left->right)' else 'TB' };")
    lines.append("  node [shape=box, style=filled, fillcolor=white];")

    if show_region and 'region' in df.columns and df['region'].astype(str).str.strip().any():
        regions = df.set_index('variable')['region'].fillna('').to_dict()
        grouped = {}
        for v, r in regions.items():
            key = r.strip() or 'Other'
            grouped.setdefault(key, []).append(v)
        for i, (rname, vars_) in enumerate(grouped.items()):
            lines.append(f"  subgraph cluster_{i} {{")
            lines.append(f"    label=\"{rname}\";")
            lines.append("    style=dashed;")
            for v in vars_:
                safe = v.replace('"','\\"')
                lines.append(f"    \"{safe}\";")
            lines.append("  }")
    else:
        for v in df['variable'].tolist():
            safe = v.replace('"','\\"')
            lines.append(f"  \"{safe}\";")

    def edge_props(rel):
        if rel == 'Positive':
            return ("green", "+")
        if rel == 'Negative':
            return ("red", "-")
        return ("gray", "ns")

    for iv in inds:
        color, label = edge_props(rel_map.get(iv, 'Insignificant'))
        lbl = f" label=\"{label}\"" if show_labels else ""
        safe_iv = iv.replace('"','\\"')
        safe_dep = dep.replace('"','\\"')
        lines.append(f"  \"{safe_iv}\" -> \"{safe_dep}\" [color={color}, penwidth={edge_penwidth}{lbl}];")

    if show_legend:
        lines.append('  subgraph cluster_legend {')
        lines.append('    label="Legend";')
        lines.append('    key_pos [label="+ : positive\\n- : negative\\nns : insignificant", shape=note];')
        lines.append('  }')

    lines.append('}')
    return "\n".join(lines)

dot = build_dot(dep, inds, rel_map, df, show_region, layout_lr)

st.subheader("Preview")
st.graphviz_chart(dot)

b = dot.encode('utf-8')
st.download_button("Download DOT (Graphviz) file", data=b, file_name="graphical_abstract.dot", mime="text/vnd.graphviz")

try:
    import graphviz
    svg = graphviz.Source(dot).pipe(format='svg')
    st.download_button("Download SVG image", data=svg, file_name="graphical_abstract.svg", mime="image/svg+xml")
except Exception as e:
    st.info("SVG export unavailable. Install the 'graphviz' system package and Python library to enable export.")

REQUIREMENTS = """streamlit
pandas
graphviz
"""

if st.button("Write requirements.txt to disk (useful for virtualenv)"):
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(REQUIREMENTS)
    st.success("requirements.txt written to current working directory")

st.markdown("---")
st.markdown("Notes: If you need more complex layouts or multiple dependent variables, this app can be extended easily.")
