import streamlit as st
import graphviz

# ========================
# Academic Conceptual Framework
# ========================

st.set_page_config(page_title="Quantile Regression Conceptual Framework", layout="wide")

st.title("📘 Conceptual Framework: Quantile Regression for Tourism Demand")

st.markdown("""
This figure visualizes the hypothesized structure of the quantile regression model,
emphasizing heterogeneous effects of macroeconomic and environmental variables on tourism demand across quantiles.
""")

# --- Graphviz Setup ---
dot = graphviz.Digraph(format='png')
dot.attr(rankdir='LR', bgcolor='white', splines='curved', nodesep='1.0', ranksep='1.2')
dot.attr('node', shape='box', style='rounded,filled', fontname='Helvetica', fontsize='12')

# --- Core Variables ---
dot.node('Y', 'Tourism Demand\n(Dependent Variable)', fillcolor='#003366', fontcolor='white', penwidth='2')

independent_vars = [
    ('X1', 'Real Effective Exchange Rate'),
    ('X2', 'Green Bond Issuance'),
    ('X3', 'GDP Growth'),
    ('X4', 'Environmental Policy Index'),
    ('X5', 'Financial Development'),
]

for code, label in independent_vars:
    dot.node(code, label, fillcolor='#e8f1f9', fontcolor='#002b36', penwidth='1')

# --- Quantile Layers ---
quantiles = ['τ=0.1', 'τ=0.25', 'τ=0.5', 'τ=0.75', 'τ=0.9']
for q in quantiles:
    dot.node(q, q, shape='circle', fillcolor='#a7c6e5', style='filled', width='0.4')

# --- Edges: Predictors → Quantiles ---
for code, _ in independent_vars:
    for q in quantiles:
        dot.edge(code, q, color='#6699cc', penwidth='1.2')

# --- Edges: Quantiles → Dependent Variable ---
for q in quantiles:
    dot.edge(q, 'Y', color='#003366', penwidth='1.5')

# --- Equation Node ---
dot.node('EQ', 'Quantile Process:\nQτ(Y|X) = X′β(τ)', shape='note', fillcolor='#f5f5f5', fontcolor='#003366', fontsize='11')
dot.edge('Y', 'EQ', style='dashed', color='gray', penwidth='1')

# --- Render in Streamlit ---
st.graphviz_chart(dot, use_container_width=True)

# --- Academic Note ---
st.markdown("""
#### Notes:
- Blue gradient circles denote conditional quantiles (τ = 0.1–0.9).  
- Directed edges represent the heterogeneous marginal impact of predictors on tourism demand across quantiles.  
- The specification aligns with **Koenker & Bassett (1978)** and panel extensions by **Canay (2011)** and **Powell (2020)**.  
""")
