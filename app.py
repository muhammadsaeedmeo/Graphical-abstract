import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np
from io import BytesIO
import colorsys

# Set page configuration
st.set_page_config(page_title="Academic Research Visualizer", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🎓 Academic Research Visualization Tool</p>', unsafe_allow_html=True)
st.markdown("**Professional Graphical Abstracts & Methodology Flowcharts for Financial Economics Research**")

# Sidebar for tool selection
st.sidebar.title("📊 Visualization Tools")
tool_choice = st.sidebar.radio("Select Tool:", ["Graphical Abstract Generator", "Methodology Flowchart Designer"])

# ==================== GRAPHICAL ABSTRACT GENERATOR ====================
if tool_choice == "Graphical Abstract Generator":
    st.markdown('<p class="sub-header">📈 Graphical Abstract Generator</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎯 Dependent Variable")
        dependent_var = st.text_input("Dependent Variable Name:", value="Stock Returns", key="dep_var")
        dep_color = st.color_picker("Dependent Variable Color:", value="#FF6B6B", key="dep_color")
        dep_shape = st.selectbox("Dependent Variable Shape:", ["circle", "rectangle", "hexagon"], key="dep_shape")
        
        st.subheader("📊 Independent Variables")
        num_independent = st.number_input("Number of Independent Variables:", min_value=1, max_value=10, value=4, key="num_indep")
        
        independent_vars = []
        for i in range(num_independent):
            st.markdown(f"**Variable {i+1}:**")
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                var_name = st.text_input(f"Name:", value=f"Variable {i+1}", key=f"indep_name_{i}", label_visibility="collapsed")
            with col_b:
                relationship = st.selectbox("Effect:", ["Positive", "Negative"], key=f"rel_{i}", label_visibility="collapsed")
            with col_c:
                var_color = st.color_picker("Color:", value="#4ECDC4" if relationship == "Positive" else "#FF8B94", key=f"indep_color_{i}", label_visibility="collapsed")
            
            independent_vars.append({
                "name": var_name,
                "relationship": relationship,
                "color": var_color
            })
    
    with col2:
        st.subheader("🎨 Visualization Settings")
        
        figure_width = st.slider("Figure Width (inches):", 8, 20, 16, key="fig_width")
        figure_height = st.slider("Figure Height (inches):", 6, 16, 12, key="fig_height")
        dpi_setting = st.selectbox("Resolution (DPI):", [150, 300, 600, 1200], index=1, key="dpi")
        
        bg_color = st.color_picker("Background Color:", value="#FFFFFF", key="bg_color")
        font_size_dep = st.slider("Dependent Variable Font Size:", 12, 32, 20, key="font_dep")
        font_size_indep = st.slider("Independent Variables Font Size:", 8, 24, 14, key="font_indep")
        
        arrow_style = st.selectbox("Arrow Style:", ["->", "-|>", "fancy", "simple"], key="arrow_style")
        arrow_width = st.slider("Arrow Width:", 1.0, 5.0, 2.5, key="arrow_width")
        
        show_labels = st.checkbox("Show Relationship Labels on Arrows", value=True, key="show_labels")
        
    if st.button("🎨 Generate Graphical Abstract", key="gen_abstract"):
        with st.spinner("Creating your graphical abstract..."):
            fig, ax = plt.subplots(figsize=(figure_width, figure_height), dpi=dpi_setting)
            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.axis('off')
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
            
            # Draw dependent variable in center
            center_x, center_y = 0, 0
            
            if dep_shape == "circle":
                dep_patch = Circle((center_x, center_y), 0.15, facecolor=dep_color, edgecolor='black', linewidth=3, zorder=10)
            elif dep_shape == "rectangle":
                dep_patch = FancyBboxPatch((center_x-0.15, center_y-0.1), 0.3, 0.2, 
                                          boxstyle="round,pad=0.01", facecolor=dep_color, 
                                          edgecolor='black', linewidth=3, zorder=10)
            else:  # hexagon
                hex_points = np.array([
                    [center_x + 0.15*np.cos(np.pi/3*i), center_y + 0.15*np.sin(np.pi/3*i)] 
                    for i in range(6)
                ])
                dep_patch = mpatches.Polygon(hex_points, facecolor=dep_color, edgecolor='black', linewidth=3, zorder=10)
            
            ax.add_patch(dep_patch)
            ax.text(center_x, center_y, dependent_var, ha='center', va='center', 
                   fontsize=font_size_dep, fontweight='bold', zorder=11)
            
            # Draw independent variables in a circle around dependent variable
            radius = 0.55
            angles = np.linspace(0, 2*np.pi, num_independent, endpoint=False)
            
            for i, (angle, var) in enumerate(zip(angles, independent_vars)):
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                
                # Draw independent variable box
                box = FancyBboxPatch((x-0.12, y-0.08), 0.24, 0.16, 
                                    boxstyle="round,pad=0.01", 
                                    facecolor=var['color'], 
                                    edgecolor='black', linewidth=2, zorder=5)
                ax.add_patch(box)
                ax.text(x, y, var['name'], ha='center', va='center', 
                       fontsize=font_size_indep, fontweight='bold', zorder=6)
                
                # Draw arrow from independent to dependent
                start_x = x * 0.75
                start_y = y * 0.75
                end_x = center_x + 0.18 * np.cos(angle + np.pi)
                end_y = center_y + 0.18 * np.sin(angle + np.pi)
                
                arrow_color = '#2ecc71' if var['relationship'] == 'Positive' else '#e74c3c'
                
                if arrow_style == "fancy":
                    arrow = FancyArrowPatch((start_x, start_y), (end_x, end_y),
                                          arrowstyle='-|>', mutation_scale=30, 
                                          linewidth=arrow_width, 
                                          color=arrow_color, zorder=3,
                                          connectionstyle="arc3,rad=0.1")
                else:
                    arrow = FancyArrowPatch((start_x, start_y), (end_x, end_y),
                                          arrowstyle=arrow_style, mutation_scale=20, 
                                          linewidth=arrow_width, 
                                          color=arrow_color, zorder=3)
                ax.add_patch(arrow)
                
                # Add relationship label
                if show_labels:
                    mid_x = (start_x + end_x) / 2
                    mid_y = (start_y + end_y) / 2
                    label = "+" if var['relationship'] == 'Positive' else "−"
                    ax.text(mid_x, mid_y, label, ha='center', va='center',
                           fontsize=font_size_indep+2, fontweight='bold',
                           bbox=dict(boxstyle='circle,pad=0.3', facecolor='white', edgecolor=arrow_color, linewidth=2),
                           zorder=7)
            
            plt.tight_layout()
            
            # Display the figure
            st.pyplot(fig)
            
            # Download button
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=dpi_setting, bbox_inches='tight', facecolor=bg_color)
            buf.seek(0)
            
            st.download_button(
                label="📥 Download Graphical Abstract (PNG)",
                data=buf,
                file_name="graphical_abstract.png",
                mime="image/png"
            )
            
            # Also save as PDF
            buf_pdf = BytesIO()
            fig.savefig(buf_pdf, format='pdf', bbox_inches='tight', facecolor=bg_color)
            buf_pdf.seek(0)
            
            st.download_button(
                label="📥 Download Graphical Abstract (PDF)",
                data=buf_pdf,
                file_name="graphical_abstract.pdf",
                mime="application/pdf"
            )
            
            plt.close()

# ==================== METHODOLOGY FLOWCHART DESIGNER ====================
else:
    st.markdown('<p class="sub-header">🔄 Methodology Flowchart Designer</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Flowchart Steps")
        
        num_steps = st.number_input("Number of Steps:", min_value=2, max_value=15, value=5, key="num_steps")
        
        steps = []
        for i in range(num_steps):
            st.markdown(f"**Step {i+1}:**")
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                step_text = st.text_input(f"Text:", value=f"Step {i+1}", key=f"step_text_{i}", label_visibility="collapsed")
            with col_b:
                step_shape = st.selectbox("Shape:", ["rectangle", "rounded", "oval", "diamond", "parallelogram"], 
                                         key=f"step_shape_{i}", label_visibility="collapsed")
            with col_c:
                step_color = st.color_picker("Color:", value="#3498db", key=f"step_color_{i}", label_visibility="collapsed")
            
            steps.append({
                "text": step_text,
                "shape": step_shape,
                "color": step_color
            })
    
    with col2:
        st.subheader("🎨 Flowchart Settings")
        
        fig_width_flow = st.slider("Figure Width (inches):", 8, 24, 14, key="fig_width_flow")
        fig_height_flow = st.slider("Figure Height (inches):", 10, 30, 18, key="fig_height_flow")
        dpi_flow = st.selectbox("Resolution (DPI):", [150, 300, 600, 1200], index=1, key="dpi_flow")
        
        bg_color_flow = st.color_picker("Background Color:", value="#F8F9FA", key="bg_flow")
        font_size_flow = st.slider("Font Size:", 10, 24, 14, key="font_flow")
        
        layout_style = st.selectbox("Layout Style:", ["vertical", "horizontal"], key="layout_style")
        arrow_style_flow = st.selectbox("Arrow Style:", ["->", "-|>", "fancy", "wedge"], key="arrow_flow")
        arrow_width_flow = st.slider("Arrow Width:", 1.0, 6.0, 3.0, key="arrow_width_flow")
        
        show_step_numbers = st.checkbox("Show Step Numbers", value=True, key="show_nums")
        add_shadow = st.checkbox("Add Shadow Effect", value=True, key="add_shadow")
        
    if st.button("🎨 Generate Methodology Flowchart", key="gen_flowchart"):
        with st.spinner("Creating your methodology flowchart..."):
            fig, ax = plt.subplots(figsize=(fig_width_flow, fig_height_flow), dpi=dpi_flow)
            
            if layout_style == "vertical":
                ax.set_xlim(-1, 1)
                ax.set_ylim(-0.5, num_steps + 0.5)
            else:
                ax.set_xlim(-0.5, num_steps + 0.5)
                ax.set_ylim(-1, 1)
            
            ax.axis('off')
            fig.patch.set_facecolor(bg_color_flow)
            ax.set_facecolor(bg_color_flow)
            
            box_width = 0.6
            box_height = 0.35
            
            for i, step in enumerate(steps):
                if layout_style == "vertical":
                    x = 0
                    y = num_steps - i
                else:
                    x = i
                    y = 0
                
                # Add shadow if enabled
                if add_shadow:
                    shadow_offset = 0.02
                    if step['shape'] == "rectangle":
                        shadow = FancyBboxPatch((x - box_width/2 + shadow_offset, y - box_height/2 - shadow_offset), 
                                               box_width, box_height,
                                               boxstyle="square,pad=0.05", 
                                               facecolor='gray', alpha=0.3, zorder=1)
                    elif step['shape'] == "rounded":
                        shadow = FancyBboxPatch((x - box_width/2 + shadow_offset, y - box_height/2 - shadow_offset), 
                                               box_width, box_height,
                                               boxstyle="round,pad=0.05", 
                                               facecolor='gray', alpha=0.3, zorder=1)
                    elif step['shape'] == "oval":
                        shadow = mpatches.Ellipse((x + shadow_offset, y - shadow_offset), 
                                                 box_width, box_height,
                                                 facecolor='gray', alpha=0.3, zorder=1)
                    elif step['shape'] == "diamond":
                        diamond_points = np.array([
                            [x + shadow_offset, y + box_height/2 - shadow_offset],
                            [x + box_width/2 + shadow_offset, y - shadow_offset],
                            [x + shadow_offset, y - box_height/2 - shadow_offset],
                            [x - box_width/2 + shadow_offset, y - shadow_offset]
                        ])
                        shadow = mpatches.Polygon(diamond_points, facecolor='gray', alpha=0.3, zorder=1)
                    elif step['shape'] == "parallelogram":
                        para_points = np.array([
                            [x - box_width/2 + 0.1 + shadow_offset, y + box_height/2 - shadow_offset],
                            [x + box_width/2 + 0.1 + shadow_offset, y + box_height/2 - shadow_offset],
                            [x + box_width/2 - 0.1 + shadow_offset, y - box_height/2 - shadow_offset],
                            [x - box_width/2 - 0.1 + shadow_offset, y - box_height/2 - shadow_offset]
                        ])
                        shadow = mpatches.Polygon(para_points, facecolor='gray', alpha=0.3, zorder=1)
                    
                    ax.add_patch(shadow)
                
                # Draw main shape
                if step['shape'] == "rectangle":
                    box = FancyBboxPatch((x - box_width/2, y - box_height/2), box_width, box_height,
                                        boxstyle="square,pad=0.05", 
                                        facecolor=step['color'], edgecolor='black', linewidth=2.5, zorder=5)
                elif step['shape'] == "rounded":
                    box = FancyBboxPatch((x - box_width/2, y - box_height/2), box_width, box_height,
                                        boxstyle="round,pad=0.05", 
                                        facecolor=step['color'], edgecolor='black', linewidth=2.5, zorder=5)
                elif step['shape'] == "oval":
                    box = mpatches.Ellipse((x, y), box_width, box_height,
                                          facecolor=step['color'], edgecolor='black', linewidth=2.5, zorder=5)
                elif step['shape'] == "diamond":
                    diamond_points = np.array([
                        [x, y + box_height/2],
                        [x + box_width/2, y],
                        [x, y - box_height/2],
                        [x - box_width/2, y]
                    ])
                    box = mpatches.Polygon(diamond_points, facecolor=step['color'], 
                                          edgecolor='black', linewidth=2.5, zorder=5)
                elif step['shape'] == "parallelogram":
                    para_points = np.array([
                        [x - box_width/2 + 0.1, y + box_height/2],
                        [x + box_width/2 + 0.1, y + box_height/2],
                        [x + box_width/2 - 0.1, y - box_height/2],
                        [x - box_width/2 - 0.1, y - box_height/2]
                    ])
                    box = mpatches.Polygon(para_points, facecolor=step['color'], 
                                          edgecolor='black', linewidth=2.5, zorder=5)
                
                ax.add_patch(box)
                
                # Add text
                step_label = f"{i+1}. {step['text']}" if show_step_numbers else step['text']
                ax.text(x, y, step_label, ha='center', va='center',
                       fontsize=font_size_flow, fontweight='bold', zorder=6, wrap=True)
                
                # Draw arrow to next step
                if i < len(steps) - 1:
                    if layout_style == "vertical":
                        start_y = y - box_height/2 - 0.05
                        end_y = y - 1 + box_height/2 + 0.05
                        arrow = FancyArrowPatch((x, start_y), (x, end_y),
                                              arrowstyle=arrow_style_flow, mutation_scale=30,
                                              linewidth=arrow_width_flow, color='#2c3e50', zorder=3)
                    else:
                        start_x = x + box_width/2 + 0.05
                        end_x = x + 1 - box_width/2 - 0.05
                        arrow = FancyArrowPatch((start_x, y), (end_x, y),
                                              arrowstyle=arrow_style_flow, mutation_scale=30,
                                              linewidth=arrow_width_flow, color='#2c3e50', zorder=3)
                    
                    ax.add_patch(arrow)
            
            plt.tight_layout()
            
            # Display the figure
            st.pyplot(fig)
            
            # Download button
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=dpi_flow, bbox_inches='tight', facecolor=bg_color_flow)
            buf.seek(0)
            
            st.download_button(
                label="📥 Download Flowchart (PNG)",
                data=buf,
                file_name="methodology_flowchart.png",
                mime="image/png"
            )
            
            # Also save as PDF
            buf_pdf = BytesIO()
            fig.savefig(buf_pdf, format='pdf', bbox_inches='tight', facecolor=bg_color_flow)
            buf_pdf.seek(0)
            
            st.download_button(
                label="📥 Download Flowchart (PDF)",
                data=buf_pdf,
                file_name="methodology_flowchart.pdf",
                mime="application/pdf"
            )
            
            plt.close()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 20px;'>
    <p><strong>Academic Research Visualization Tool</strong></p>
    <p>Designed for Financial Economics Researchers | High-Resolution Outputs for Publications</p>
</div>
""", unsafe_allow_html=True)
