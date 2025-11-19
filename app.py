import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="Academic Infographic Generator",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2C3E50;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #34495E;
        margin-bottom: 1rem;
    }
    .infographic-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .step-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def create_professional_infographic(methodology_steps, title, colors):
    """Create a professional infographic using matplotlib"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Set background
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#f8f9fa')
    
    # Remove axes
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    title_box = FancyBboxPatch((0.5, 9), 15, 0.8, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['primary'], 
                              edgecolor='white', linewidth=3)
    ax.add_patch(title_box)
    ax.text(8, 9.4, title, ha='center', va='center', 
            fontsize=24, weight='bold', color='white',
            fontfamily='sans-serif')
    
    # Methodology steps
    icons = ['📥', '🔍', '📈', '🤝', '⚡', '✅', '🎯']
    
    for i, step in enumerate(methodology_steps):
        x_pos = 2 + (i % 4) * 3.5
        y_pos = 7 - (i // 4) * 2.8
        
        # Create step box
        step_box = FancyBboxPatch((x_pos, y_pos), 3, 2.2,
                                boxstyle="round,pad=0.1",
                                facecolor=colors['secondary'],
                                edgecolor='white', linewidth=2)
        ax.add_patch(step_box)
        
        # Icon
        ax.text(x_pos + 1.5, y_pos + 1.7, icons[i % len(icons)], 
                ha='center', va='center', fontsize=30)
        
        # Step text
        ax.text(x_pos + 1.5, y_pos + 1.2, f"Step {i+1}", 
                ha='center', va='center', fontsize=14, 
                weight='bold', color='white')
        
        # Description
        ax.text(x_pos + 1.5, y_pos + 0.7, step, 
                ha='center', va='center', fontsize=10, 
                color='white', wrap=True)
    
    # Add connecting arrows
    for i in range(len(methodology_steps) - 1):
        if (i + 1) % 4 != 0:  # Don't draw arrows between rows
            x1 = 2 + (i % 4) * 3.5 + 3
            x2 = 2 + ((i + 1) % 4) * 3.5
            y = 7 - (i // 4) * 2.8 + 1.1
            ax.annotate('', xy=(x2, y), xytext=(x1, y),
                       arrowprops=dict(arrowstyle='->', 
                                     color=colors['primary'], 
                                     lw=2))
    
    plt.tight_layout()
    return fig

def create_canva_style_infographic(research_data):
    """Create Canva-style modern infographic"""
    fig, ax = plt.subplots(figsize=(18, 12))
    
    # Modern color palette
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Main title with gradient effect
    title_bg = patches.Rectangle((1, 10), 16, 1.2, 
                               facecolor='#2C3E50', 
                               edgecolor='none', 
                               alpha=0.9)
    ax.add_patch(title_bg)
    ax.text(9, 10.6, "RESEARCH METHODOLOGY INFOGRAPHIC", 
            ha='center', va='center', 
            fontsize=28, weight='bold', color='white',
            fontfamily='sans-serif')
    
    # Steps in modern layout
    steps = research_data['steps']
    for i, step in enumerate(steps):
        row = i // 3
        col = i % 3
        
        x = 2 + col * 5
        y = 8 - row * 3
        
        # Modern card design
        card = FancyBboxPatch((x, y), 4.5, 2.2,
                            boxstyle="round,pad=0.1",
                            facecolor=colors[i % len(colors)],
                            edgecolor='white',
                            linewidth=3,
                            alpha=0.9)
        ax.add_patch(card)
        
        # Step number
        ax.text(x + 0.5, y + 1.7, f"{i+1:02d}", 
                ha='left', va='center', 
                fontsize=16, weight='bold', 
                color='white', alpha=0.8)
        
        # Step description
        ax.text(x + 2.25, y + 1.1, step, 
                ha='center', va='center', 
                fontsize=12, weight='bold', 
                color='white', wrap=True,
                fontfamily='sans-serif')
    
    # Footer
    footer_bg = patches.Rectangle((1, 0.5), 16, 0.8,
                                facecolor='#34495E',
                                edgecolor='none',
                                alpha=0.8)
    ax.add_patch(footer_bg)
    ax.text(9, 0.9, research_data['conclusion'],
            ha='center', va='center',
            fontsize=14, color='white',
            fontfamily='sans-serif')
    
    plt.tight_layout()
    return fig

def get_image_download_link(fig, filename, text):
    """Generate a download link for the image"""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Streamlit App Interface
def main():
    st.markdown('<div class="main-header">🎓 Academic Infographic Generator</div>', 
                unsafe_allow_html=True)
    
    # Sidebar for input
    with st.sidebar:
        st.header("Research Details")
        research_title = st.text_input("Research Title", 
                                     "Financial Time Series Analysis")
        
        st.subheader("Methodology Steps")
        steps = []
        for i in range(7):
            step = st.text_input(f"Step {i+1}", 
                               value=[
                                   "Data Collection & Preparation",
                                   "Unit Root Testing (ADF, PP)",
                                   "Stationarity Analysis",
                                   "Cointegration Testing",
                                   "VECM Model Estimation",
                                   "Diagnostic Checking",
                                   "Results Interpretation"
                               ][i] if i < 7 else "")
            if step:
                steps.append(step)
        
        color_primary = st.color_picker("Primary Color", "#2C3E50")
        color_secondary = st.color_picker("Secondary Color", "#3498DB")
        
        conclusion = st.text_area("Conclusion Text", 
                                "Advanced Econometric Analysis Revealing Significant Relationships")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Your Research Methodology")
        research_data = {
            'title': research_title,
            'steps': steps,
            'colors': {
                'primary': color_primary,
                'secondary': color_secondary
            },
            'conclusion': conclusion
        }
        
        # Display methodology as list
        for i, step in enumerate(steps, 1):
            st.markdown(f"""
            <div class="step-box">
                <b>Step {i}:</b> {step}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎨 Generated Infographic")
        
        # Generate infographic
        if steps:
            # Professional style
            fig1 = create_professional_infographic(
                steps, 
                research_title,
                research_data['colors']
            )
            
            # Canva style
            fig2 = create_canva_style_infographic({
                'steps': steps,
                'conclusion': conclusion
            })
            
            # Display images
            st.pyplot(fig1)
            st.markdown("---")
            st.pyplot(fig2)
            
            # Download buttons
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown(get_image_download_link(
                    fig1, "professional_infographic.png", 
                    "📥 Download Professional Style"
                ), unsafe_allow_html=True)
            
            with col_d2:
                st.markdown(get_image_download_link(
                    fig2, "canva_style_infographic.png", 
                    "📥 Download Canva Style"
                ), unsafe_allow_html=True)
    
    # Additional features
    st.markdown("---")
    st.subheader("🚀 Quick Templates")
    
    template_col1, template_col2, template_col3 = st.columns(3)
    
    with template_col1:
        if st.button("Time Series Analysis Template"):
            st.session_state.research_title = "Advanced Time Series Econometrics"
            st.session_state.steps = [
                "Data Collection & Cleaning",
                "Unit Root Testing (ADF/PP)",
                "Stationarity Assessment", 
                "Cointegration Analysis",
                "VECM Specification",
                "Model Diagnostics",
                "Policy Implications"
            ]
            st.rerun()
    
    with template_col2:
        if st.button("Financial Modeling Template"):
            st.session_state.research_title = "Financial Risk Modeling"
            st.session_state.steps = [
                "Market Data Acquisition",
                "Returns Calculation",
                "Volatility Modeling",
                "Risk Factor Analysis",
                "Portfolio Optimization",
                "Backtesting",
                "Risk Management Strategies"
            ]
            st.rerun()
    
    with template_col3:
        if st.button("Macroeconomic Research Template"):
            st.session_state.research_title = "Macroeconomic Policy Analysis"
            st.session_state.steps = [
                "Macro Data Collection",
                "Seasonal Adjustment",
                "Trend-Cycle Decomposition",
                "Multivariate Cointegration",
                "Structural VAR Modeling",
                "Shock Identification",
                "Policy Recommendations"
            ]
            st.rerun()

if __name__ == "__main__":
    main()
