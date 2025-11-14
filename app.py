import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np
from io import BytesIO
import json

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
    .step-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 4px solid #1f77b4;
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
            st.markdown(f"<div class='step-box'>", unsafe_allow_html=True)
            st.markdown(f"**Variable {i+1}:**")
            
            var_name = st.text_input(f"Variable Name:", value=f"Variable {i+1}", key=f"indep_name_{i}")
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                relationship = st.text_input(f"Relationship Type:", value="Positive", 
                                            key=f"rel_{i}",
                                            help="Enter any text: Positive, Negative, Non-linear, U-shaped, Inverted-U, Moderating, etc.")
            with col_b:
                symbol = st.text_input(f"Symbol/Sign:", value="+", 
                                      key=f"symbol_{i}",
                                      help="Enter any symbol: +, -, ±, ∩, ∪, ~, *, etc.")
            
            var_color = st.color_picker(f"Color:", value="#4ECDC4", key=f"indep_color_{i}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            independent_vars.append({
                "name": var_name,
                "relationship": relationship,
                "symbol": symbol,
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
        
        arrow_style = st.selectbox("Arrow Style:", ["->", "-|>", "fancy", "simple", "wedge"], key="arrow_style")
        arrow_width = st.slider("Arrow Width:", 1.0, 5.0, 2.5, key="arrow_width")
        
        show_labels = st.checkbox("Show Relationship Labels on Arrows", value=True, key="show_labels")
        show_symbols = st.checkbox("Show Symbols on Arrows", value=True, key="show_symbols")
        
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
                
                # Determine arrow color based on relationship keyword
                arrow_color = '#2c3e50'  # default
                rel_lower = var['relationship'].lower()
                if 'positive' in rel_lower or '+' in var['symbol']:
                    arrow_color = '#2ecc71'
                elif 'negative' in rel_lower or '-' in var['symbol']:
                    arrow_color = '#e74c3c'
                elif 'non' in rel_lower or '~' in var['symbol']:
                    arrow_color = '#f39c12'
                
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
                
                # Calculate label position
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                
                # Add relationship label and/or symbol
                if show_labels and show_symbols:
                    label_text = f"{var['symbol']}\n{var['relationship']}"
                    fontsize = font_size_indep
                elif show_symbols:
                    label_text = var['symbol']
                    fontsize = font_size_indep + 4
                elif show_labels:
                    label_text = var['relationship']
                    fontsize = font_size_indep - 2
                else:
                    label_text = None
                
                if label_text:
                    ax.text(mid_x, mid_y, label_text, ha='center', va='center',
                           fontsize=fontsize, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                                   edgecolor=arrow_color, linewidth=2),
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
    
    # Initialize session state for steps
    if 'flowchart_steps' not in st.session_state:
        st.session_state.flowchart_steps = [
            {"text": "Data Collection", "shape": "rounded", "color": "#3498db", "level": 0, "parents": []},
            {"text": "Data Preprocessing", "shape": "rectangle", "color": "#9b59b6", "level": 1, "parents": [0]},
            {"text": "Analysis", "shape": "diamond", "color": "#e74c3c", "level": 2, "parents": [1]},
            {"text": "Results", "shape": "oval", "color": "#2ecc71", "level": 3, "parents": [2]}
        ]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Flowchart Steps Management")
        
        # Add new step
        with st.expander("➕ Add New Step", expanded=False):
            new_step_text = st.text_input("Step Text:", value="", key="new_step_text")
            new_step_shape = st.selectbox("Shape:", ["rectangle", "rounded", "oval", "diamond", "parallelogram"], key="new_shape")
            new_step_color = st.color_picker("Color:", value="#3498db", key="new_color")
            
            st.write("**Connect from previous steps:** (Select which steps point to this new step)")
            
            if len(st.session_state.flowchart_steps) > 0:
                parent_options = {f"Step {i+1}: {step['text']}": i for i, step in enumerate(st.session_state.flowchart_steps)}
                selected_parents = st.multiselect(
                    "Parent Steps:",
                    options=list(parent_options.keys()),
                    key="parent_select"
                )
                parent_indices = [parent_options[p] for p in selected_parents]
            else:
                parent_indices = []
                st.info("This will be the first step (no parents)")
            
            if st.button("➕ Add Step", key="add_step_btn"):
                if new_step_text:
                    # Calculate level based on parent levels
                    if parent_indices:
                        max_parent_level = max([st.session_state.flowchart_steps[p]['level'] for p in parent_indices])
                        new_level = max_parent_level + 1
                    else:
                        new_level = 0
                    
                    st.session_state.flowchart_steps.append({
                        "text": new_step_text,
                        "shape": new_step_shape,
                        "color": new_step_color,
                        "level": new_level,
                        "parents": parent_indices
                    })
                    st.success(f"Added: {new_step_text}")
                    st.rerun()
        
        # Display and manage existing steps
        st.markdown("### Current Steps:")
        
        for i, step in enumerate(st.session_state.flowchart_steps):
            with st.expander(f"Step {i+1}: {step['text']}", expanded=False):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    step['text'] = st.text_input("Text:", value=step['text'], key=f"edit_text_{i}")
                with col_b:
                    step['shape'] = st.selectbox("Shape:", ["rectangle", "rounded", "oval", "diamond", "parallelogram"],
                                                 index=["rectangle", "rounded", "oval", "diamond", "parallelogram"].index(step['shape']),
                                                 key=f"edit_shape_{i}")
                
                step['color'] = st.color_picker("Color:", value=step['color'], key=f"edit_color_{i}")
                
                # Show parent connections
                if step['parents']:
                    parent_names = [f"Step {p+1}: {st.session_state.flowchart_steps[p]['text']}" for p in step['parents']]
                    st.info(f"📊 Connected from: {', '.join(parent_names)}")
                else:
                    st.info("📊 Starting step (no parents)")
                
                col_del, col_up, col_down = st.columns(3)
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_{i}"):
                        # Remove this step and update parent references in other steps
                        st.session_state.flowchart_steps.pop(i)
                        # Update parent indices for remaining steps
                        for s in st.session_state.flowchart_steps:
                            s['parents'] = [p if p < i else p-1 for p in s['parents'] if p != i]
                        st.rerun()
                
                with col_up:
                    if i > 0 and st.button("⬆️ Move Up", key=f"up_{i}"):
                        st.session_state.flowchart_steps[i], st.session_state.flowchart_steps[i-1] = \
                            st.session_state.flowchart_steps[i-1], st.session_state.flowchart_steps[i]
                        # Update parent references
                        for s in st.session_state.flowchart_steps:
                            s['parents'] = [i-1 if p == i else i if p == i-1 else p for p in s['parents']]
                        st.rerun()
                
                with col_down:
                    if i < len(st.session_state.flowchart_steps) - 1 and st.button("⬇️ Move Down", key=f"down_{i}"):
                        st.session_state.flowchart_steps[i], st.session_state.flowchart_steps[i+1] = \
                            st.session_state.flowchart_steps[i+1], st.session_state.flowchart_steps[i]
                        # Update parent references
                        for s in st.session_state.flowchart_steps:
                            s['parents'] = [i+1 if p == i else i if p == i+1 else p for p in s['parents']]
                        st.rerun()
        
        if st.button("🔄 Reset to Default", key="reset_steps"):
            st.session_state.flowchart_steps = [
                {"text": "Data Collection", "shape": "rounded", "color": "#3498db", "level": 0, "parents": []},
                {"text": "Data Preprocessing", "shape": "rectangle", "color": "#9b59b6", "level": 1, "parents": [0]},
                {"text": "Analysis", "shape": "diamond", "color": "#e74c3c", "level": 2, "parents": [1]},
                {"text": "Results", "shape": "oval", "color": "#2ecc71", "level": 3, "parents": [2]}
            ]
            st.rerun()
    
    with col2:
        st.subheader("🎨 Flowchart Settings")
        
        fig_width_flow = st.slider("Figure Width (inches):", 10, 30, 20, key="fig_width_flow")
        fig_height_flow = st.slider("Figure Height (inches):", 10, 30, 16, key="fig_height_flow")
        dpi_flow = st.selectbox("Resolution (DPI):", [150, 300, 600, 1200], index=1, key="dpi_flow")
        
        bg_color_flow = st.color_picker("Background Color:", value="#F8F9FA", key="bg_flow")
        font_size_flow = st.slider("Font Size:", 10, 24, 13, key="font_flow")
        
        arrow_style_flow = st.selectbox("Arrow Style:", ["->", "-|>", "fancy", "wedge"], key="arrow_flow")
        arrow_width_flow = st.slider("Arrow Width:", 1.0, 6.0, 3.0, key="arrow_width_flow")
        
        show_step_numbers = st.checkbox("Show Step Numbers", value=True, key="show_nums")
        add_shadow = st.checkbox("Add Shadow Effect", value=True, key="add_shadow")
        
        horizontal_spacing = st.slider("Horizontal Spacing:", 1.0, 4.0, 2.5, key="h_spacing")
        vertical_spacing = st.slider("Vertical Spacing:", 0.5, 2.0, 1.2, key="v_spacing")
        
    if st.button("🎨 Generate Methodology Flowchart", key="gen_flowchart"):
        if len(st.session_state.flowchart_steps) == 0:
            st.error("Please add at least one step to generate the flowchart!")
        else:
            with st.spinner("Creating your methodology flowchart..."):
                fig, ax = plt.subplots(figsize=(fig_width_flow, fig_height_flow), dpi=dpi_flow)
                
                # Calculate positions for each step
                steps = st.session_state.flowchart_steps
                
                # Group steps by level
                levels = {}
                for i, step in enumerate(steps):
                    level = step['level']
                    if level not in levels:
                        levels[level] = []
                    levels[level].append(i)
                
                # Calculate positions
                positions = {}
                max_level = max(levels.keys()) if levels else 0
                
                for level, step_indices in levels.items():
                    num_in_level = len(step_indices)
                    y = max_level - level
                    
                    for idx, step_i in enumerate(step_indices):
                        if num_in_level == 1:
                            x = 0
                        else:
                            x = (idx - (num_in_level - 1) / 2) * horizontal_spacing
                        positions[step_i] = (x, y * vertical_spacing)
                
                # Calculate axis limits
                if positions:
                    all_x = [pos[0] for pos in positions.values()]
                    all_y = [pos[1] for pos in positions.values()]
                    margin = 0.8
                    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
                    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
                
                ax.axis('off')
                fig.patch.set_facecolor(bg_color_flow)
                ax.set_facecolor(bg_color_flow)
                
                box_width = 0.6
                box_height = 0.35
                
                # Draw arrows first (lower z-order)
                for i, step in enumerate(steps):
                    if step['parents']:
                        x, y = positions[i]
                        for parent_i in step['parents']:
                            parent_x, parent_y = positions[parent_i]
                            
                            # Calculate arrow start and end points
                            start_y = parent_y - box_height/2 - 0.05
                            end_y = y + box_height/2 + 0.05
                            
                            arrow = FancyArrowPatch((parent_x, start_y), (x, end_y),
                                                  arrowstyle=arrow_style_flow, mutation_scale=30,
                                                  linewidth=arrow_width_flow, color='#2c3e50', zorder=3,
                                                  connectionstyle="arc3,rad=0.2")
                            ax.add_patch(arrow)
                
                # Draw boxes
                for i, step in enumerate(steps):
                    x, y = positions[i]
                    
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
