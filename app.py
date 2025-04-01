import streamlit as st
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from scipy.stats import beta
from plotly.subplots import make_subplots
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Análisis A/B Testing",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextArea {
        font-family: monospace;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

def parse_metrics_data(text):
    """Parse multiple metrics data from text input."""
    metrics_data = {}
    current_metric = None
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a metric name
        if not line.lower().startswith(('baseline', 'treatment')):
            current_metric = line
            metrics_data[current_metric] = {'baseline': None, 'treatment': None}
            continue
            
        # Parse baseline or treatment data
        parts = line.split()
        if len(parts) >= 3:
            group = parts[0].lower()
            if group in ['baseline', 'treatment']:
                metrics_data[current_metric][group] = {
                    'n': int(parts[1]),
                    'x': int(parts[2])
                }
    
    return metrics_data

def calculate_ab_test(control_n, control_x, treatment_n, treatment_x):
    """Calculate A/B test statistics."""
    control_p = control_x / control_n
    treatment_p = treatment_x / treatment_n
    
    # Calculate standard error
    se = np.sqrt(
        (control_p * (1 - control_p) / control_n) +
        (treatment_p * (1 - treatment_p) / treatment_n)
    )
    
    # Calculate z-score
    z_score = (treatment_p - control_p) / se
    
    # Calculate p-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    # Calculate relative lift
    relative_lift = ((treatment_p - control_p) / control_p) * 100
    
    # Calculate bayesian probability
    n_simulations = 10000
    baseline_posterior = np.random.beta(control_x + 1, control_n - control_x + 1, n_simulations)
    treatment_posterior = np.random.beta(treatment_x + 1, treatment_n - treatment_x + 1, n_simulations)
    p2bb = np.mean(treatment_posterior > baseline_posterior)
    
    return {
        'control_p': control_p,
        'treatment_p': treatment_p,
        'se': se,
        'z_score': z_score,
        'p_value': p_value,
        'relative_lift': relative_lift,
        'p2bb': p2bb
    }

def create_metric_card(metric_name, data, results):
    """Create a styled card for a metric."""
    st.markdown("""
        <style>
        .metric-card {
            width: 600px;
            height: 240px;
            background: #4A6489;
            box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
            border-radius: 12px;
            margin: 20px auto;
            color: white;
            position: relative;
            overflow: hidden;
        }
        .metric-header {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            padding: 16px;
            gap: 10px;
            width: 100%;
            height: 54px;
            background: #FFFFFF;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .metric-header-emoji {
            font-size: 24px;
            line-height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 8px;
        }
        .metric-header-text {
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 900;
            font-size: 20px;
            line-height: 24px;
            color: #1B365D;
            display: flex;
            align-items: center;
        }
        .metric-content {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            padding: 0 20px;
            gap: 20px;
            height: 140px;
        }
        .metric-section {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .metric-label {
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #FFFFFF;
            margin-bottom: 4px;
            text-align: left;
        }
        .conversion-container {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .conversion-row {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .conversion-label {
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #FFFFFF;
            width: 30px;
        }
        .metric-value {
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 6px 12px;
            min-width: 80px;
            height: 34px;
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #1B365D;
        }
        .metric-improvement {
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 6px 12px;
            min-width: 100px;
            height: 34px;
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #69BE28;
        }
        .p2bb-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 0;
            width: 100%;
            margin-top: 0;
        }
        .p2bb-chart {
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 0px;
            align-items: center;
        }
        .p2bb-bar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: auto;
        }
        .bar-container {
            width: 94px;
            height: 34px;
            background: #FFFFFF;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }
        .bar-fill {
            height: 100%;
            position: absolute;
            left: 0;
            top: 0;
            background: #3CCFE7;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .bar-value {
            font-family: 'Clan OT', sans-serif;
            font-weight: 700;
            font-size: 14px;
            position: absolute;
            width: 100%;
            text-align: center;
            z-index: 1;
        }
        </style>
    """, unsafe_allow_html=True)

    # Determinar los porcentajes y redondearlos
    v1_percentage = round(results['p2bb'] * 100)
    og_percentage = round((1 - results['p2bb']) * 100)
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-header">
                <span class="metric-header-emoji">🎯</span>
                <span class="metric-header-text">{metric_name}</span>
            </div>
            <div class="metric-content">
                <div class="metric-section">
                    <div class="metric-label">Conversion</div>
                    <div class="conversion-container">
                        <div class="conversion-row">
                            <span class="conversion-label">OG</span>
                            <div class="metric-value">{results['control_p']*100:.1f}%</div>
                        </div>
                        <div class="conversion-row">
                            <span class="conversion-label">V1</span>
                            <div class="metric-value">{results['treatment_p']*100:.1f}%</div>
                        </div>
                    </div>
                </div>
                <div class="metric-section p2bb-section">
                    <div class="metric-label">P2BB</div>
                    <div class="p2bb-chart">
                        <div class="p2bb-bar">
                            <div class="bar-container">
                                <div class="bar-fill" style="width: {og_percentage}%"></div>
                                <span class="bar-value" style="color: {('#FFFFFF' if og_percentage > 50 else '#3CCFE7')}">{og_percentage}%</span>
                            </div>
                        </div>
                        <div class="p2bb-bar">
                            <div class="bar-container">
                                <div class="bar-fill" style="width: {v1_percentage}%"></div>
                                <span class="bar-value" style="color: {('#FFFFFF' if v1_percentage > 50 else '#3CCFE7')}">{v1_percentage}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="metric-section">
                    <div class="metric-label">Improvement</div>
                    <div class="metric-improvement" style="color: {'#69BE28' if results['relative_lift'] > 0 else '#FF0000'}">
                        {'+' if results['relative_lift'] > 0 else ''}{results['relative_lift']:.2f}%
                    </div>
                </div>
                <div class="metric-section">
                    <div class="metric-label">P-value</div>
                    <div class="metric-value">{results['p_value']:.3f}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    # Título y descripción
    st.title("📊 Análisis A/B Testing")
    st.markdown("""
        Esta aplicación te permite analizar los resultados de pruebas A/B, calculando métricas clave 
        de rendimiento y significancia estadística.
    """)
    
    # Ejemplo de formato
    with st.expander("Ver ejemplo de formato"):
        st.code("""
Website conversion
Baseline 1000 100
treatment 1000 120
        """)
    
    # Área de texto para entrada de datos
    data = st.text_area(
        "Ingresa los datos en el siguiente formato:\n[Nombre de la Métrica]\nBaseline [sesiones] [conversiones]\ntreatment [sesiones] [conversiones]",
        height=200
    )
    
    if st.button("Analizar", type="primary"):
        if data:
            try:
                # Parsear y validar datos
                metrics_data = parse_metrics_data(data)
                
                if not metrics_data:
                    st.error("No valid metrics data found. Please check the format.")
                    return
                
                # Procesar cada métrica
                for metric_name, data in metrics_data.items():
                    if data['baseline'] and data['treatment']:
                        # Calcular resultados
                        results = calculate_ab_test(
                            data['baseline']['n'],
                            data['baseline']['x'],
                            data['treatment']['n'],
                            data['treatment']['x']
                        )
                        
                        # Crear y mostrar gráfico
                        create_metric_card(metric_name, data, results)
                    else:
                        st.error(f"Missing data for {metric_name}. Please check the format.")
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
        else:
            st.warning("Please enter some data to analyze.")

if __name__ == "__main__":
    main() 