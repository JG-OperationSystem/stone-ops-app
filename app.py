import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN DE PÁGINA E IDENTIDAD
st.set_page_config(
    page_title="JG-OperationSystem | Production Control 3.0",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ESTILOS CSS EJECUTIVOS
st.markdown("""
    <style>
    /* Fondo general neutro corporativo */
    .stApp {
        background-color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Principal */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.1);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #94a3b8;
        margin: 4px 0 0 0;
        font-size: 0.95rem;
    }

    /* Tarjetas de Métricas Ejecutivas */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    div[data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        color: #0f172a;
        font-weight: 800;
        font-size: 1.8rem;
    }

    /* Formulario */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }

    /* Botón Principal */
    .stButton>button, .stFormSubmitButton>button {
        background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100%;
        padding: 0.75rem 1.25rem !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 6px -1px rgba(13, 148, 136, 0.2);
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover {
        background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%) !important;
        box-shadow: 0 6px 12px -2px rgba(13, 148, 136, 0.35);
    }
    </style>
""", unsafe_allow_html=True)

# BARRA LATERAL CORPORATIVA
st.sidebar.markdown("""
    <div style="padding: 10px 0;">
        <h2 style="color:#0f172a; margin:0; font-size:1.4rem;">💎 JG-OperationSystem</h2>
        <p style="color:#64748b; margin:0; font-size:0.85rem;">Production Control 3.0</p>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Navegación del Sistema",
    ["📊 Dashboard Interactivo", "➕ Nuevo Trabajo", "📋 Lista de Trabajos"]
)

# CONEXIÓN INTELIGENTE A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(worksheet="Production Intake", ttl="0d")
        if not df.empty:
            for idx, row in df.iterrows():
                if "Job ID" in row.values:
                    df.columns = row
                    df = df.iloc[idx+1:].reset_index(drop=True)
                    break
            df = df.dropna(how="all")
            if 'SqFt' in df.columns:
                df['SqFt'] = pd.to_numeric(df['SqFt'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
            if 'Slabs' in df.columns:
                df['Slabs'] = pd.to_numeric(df['Slabs'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# HEADER SUPERIOR
st.markdown("""
    <div class="main-header">
        <h1>Production Control System</h1>
        <p>Panel Ejecutivo de Gestión de Producción y Monitoreo en Tiempo Real</p>
    </div>
""", unsafe_allow_html=True)

# 1. DASHBOARD
if opcion == "📊 Dashboard Interactivo":
    if not df.empty and 'Job ID' in df.columns:
        df_valid = df[df['Job ID'].notnull() & (df['Job ID'] != "")].copy()
        
        # Tarjetas de Indicadores Principales
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Órdenes Totales", len(df_valid))
        
        sqft_val = df_valid['SqFt'].sum() if 'SqFt' in df.columns else 0.0
        col2.metric("SqFt Totales", f"{sqft_val:,.2f}")
        
        slabs_val = df_valid['Slabs'].sum() if 'Slabs' in df.columns else 0
        col3.metric("Slabs Totales", int(slabs_val))
        
        col4.metric("Estatus Base de Datos", "🟢 Conectado")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos Profesionales
        c1, c2 = st.columns(2)
        with c1:
            if 'Material' in df.columns and 'SqFt' in df.columns:
                st.subheader("Volumen (SqFt) por Material")
                df_mat = df_valid.groupby('Material', as_index=False)['SqFt'].sum()
                fig_mat = px.bar(
                    df_mat, x="Material", y="SqFt", color="Material",
                    color_discrete_sequence=px.colors.qualitative.Bold, text_auto='.1f'
                )
                fig_mat.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    xaxis_title="",
                    yaxis_title="SqFt Totales"
                )
                st.plotly_chart(fig_mat, use_container_width=True)
                
        with c2:
            if 'Company' in df.columns:
                st.subheader("Distribución por Empresa")
                fig_comp = px.pie(
                    df_valid, names="Company", hole=0.55,
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_comp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Sincronizando datos con Google Sheets...")

# 2. NUEVO TRABAJO
elif opcion == "➕ Nuevo Trabajo":
    st.subheader("Ingreso de Orden de Fabricación")
    st.caption("Los datos ingresados se actualizarán automáticamente en la hoja de Google Sheets.")
    
    with st.form("job_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            company = st.selectbox("Company", ["Infinity Stone", "UGM", "Otro"])
            client = st.text_input("Client", placeholder="Nombre del Cliente")
            project = st.text_input("Project / Address", placeholder="Ubicación o Dirección")
            material = st.selectbox("Material", ["Quartz", "Marble", "Porcelain", "Granite", "Quartzite"])
        with col2:
            material_name = st.text_input("Material Name", placeholder="Ej. 3cm Organic White")
            sqft = st.number_input("SqFt", min_value=0.0, step=0.1)
            slabs = st.number_input("Slabs", min_value=1, step=1)
            slab_type = st.selectbox("Slab Type", ["Full Slab", "Remnant"])

        submitted = st.form_submit_button("💾 Guardar Trabajo en Sistema")
        
        if submitted:
            next_num = len(df) + 1
            new_job_id = f"JG-2026-{next_num:04d}"
            
            new_row = pd.DataFrame([{
                "Job ID": new_job_id,
                "Submit": "Y",
                "Company": company,
                "Client": client,
                "Project": project,
                "Material": material,
                "Material Name": material_name,
                "SqFt": sqft,
                "Slabs": slabs,
                "Slab Type": slab_type
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Production Intake", data=updated_df)
            st.success(f"¡Orden {new_job_id} registrada con éxito!")
            st.cache_data.clear()

# 3. LISTA DE TRABAJOS
elif opcion == "📋 Lista de Trabajos":
    st.subheader("Control General de Production Intake")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay órdenes registradas.")
