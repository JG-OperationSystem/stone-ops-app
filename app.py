import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Stone Ops | Panel Ejecutivo",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ESTILOS CSS PERSONALIZADOS
st.markdown("""
    <style>
    /* Estilo general del fondo */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Tarjetas de Métricas */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e9ecef;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #6c757d;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    div[data-testid="stMetricValue"] {
        color: #1e293b;
        font-weight: 700;
    }

    /* Formulario */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }

    /* Botones */
    .stButton>button, .stFormSubmitButton>button {
        background-color: #0f766e !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100%;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover {
        background-color: #0d9488 !important;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl="0d")

# NAVEGACIÓN LATERAL
st.sidebar.image("https://img.icons8.com/emShapes/100/10b981/diamond.png", width=50)
st.sidebar.title("Stone Ops")
st.sidebar.caption("Sistema de Gestión de Fabricación")
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Navegación",
    ["📊 Dashboard Interactivo", "➕ Nuevo Trabajo", "📋 Lista de Trabajos"]
)

# CARGAR DATOS
try:
    df = get_data()
except Exception as e:
    df = pd.DataFrame()

# 1. DASHBOARD
if opcion == "📊 Dashboard Interactivo":
    st.title("Panel de Control Ejecutivo")
    st.caption("Visualización en tiempo real del estado de producción y créditos guardados en Google Sheets.")
    st.markdown("<br>", unsafe_allow_html=True)

    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Trabajos Totales", len(df))
        
        sqft_val = df['SqFt'].sum() if "SqFt" in df.columns else 0
        col2.metric("SqFt Totales", f"{sqft_val:,.2f}")
        
        cred_val = df['Credits'].sum() if "Credits" in df.columns else 0
        col3.metric("Créditos Totales ($)", f"${cred_val:,.2f}")
        
        rush_count = len(df[df['Priority'].isin(['RUSH', 'HIGH'])]) if "Priority" in df.columns else 0
        col4.metric("Prioridad RUSH / HIGH", rush_count)

        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if "Material" in df.columns and "Credits" in df.columns:
                st.subheader("Créditos Acumulados por Material")
                fig_mat = px.bar(
                    df, x="Material", y="Credits", color="Material",
                    color_discrete_sequence=px.colors.qualitative.Emerald,
                    text_auto=True
                )
                fig_mat.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    xaxis_title="",
                    yaxis_title="Créditos ($)"
                )
                st.plotly_chart(fig_mat, use_container_width=True)
                
        with c2:
            if "Company" in df.columns:
                st.subheader("Distribución por Empresa")
                fig_comp = px.pie(
                    df, names="Company", hole=0.5,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_comp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("No hay datos cargados aún en tu hoja de Google Sheets.")

# 2. NUEVO TRABAJO
elif opcion == "➕ Nuevo Trabajo":
    st.title("➕ Registro de Trabajo")
    st.caption("Ingresa los detalles de la nueva orden para guardarla directamente en Google Sheets.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("job_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            job_id = st.text_input("ID de Trabajo", placeholder="Ej. ST-2026-001")
            company = st.text_input("Empresa / Cliente", placeholder="Ej. Infinity Stone")
            material = st.selectbox("Material", ["Quartz", "Porcelain", "Granite", "Marble", "Quartzite", "Otro"])
        with col2:
            sqft = st.number_input("SqFt (Pies Cuadrados)", min_value=0.0, step=0.1)
            credits = st.number_input("Créditos ($)", min_value=0.0, step=1.0)
            priority = st.selectbox("Prioridad", ["LOW", "MEDIUM", "HIGH", "RUSH"])

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 Guardar Trabajo")
        
        if submitted:
            new_row = pd.DataFrame([{
                "Job_ID": job_id,
                "Company": company,
                "Material": material,
                "SqFt": sqft,
                "Credits": credits,
                "Priority": priority
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("¡Trabajo guardado exitosamente en Google Sheets!")
            st.cache_data.clear()

# 3. LISTA DE TRABAJOS
elif opcion == "📋 Lista de Trabajos":
    st.title("📋 Lista General de Trabajos")
    st.caption("Tabla completa sincronizada con la base de datos de Google Sheets.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("La lista está vacía actualmente.")
