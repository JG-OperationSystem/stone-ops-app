import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Gestión de Trabajos | JG-OperationSystem",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl="0d")

# NAVEGACIÓN
st.sidebar.title("💎 JG Operations")
st.sidebar.caption("Sistema de Gestión de Fabricación")
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Navegación",
    ["📊 Dashboard Interactivo", "➕ Nuevo Trabajo", "📋 Lista de Trabajos"]
)

# CARGAR DATOS DE GOOGLE SHEETS
try:
    df = get_data()
except Exception as e:
    st.error("Error al conectar con Google Sheets. Asegúrate de configurar los Secrets correctamente.")
    df = pd.DataFrame()

# 1. DASHBOARD
if opcion == "📊 Dashboard Interactivo":
    st.title("📊 Panel de Control Ejecutivo")
    st.caption("Visualización en tiempo real con Google Sheets")

    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Trabajos Totales", len(df))
        
        if "SqFt" in df.columns:
            col2.metric("SqFt Totales", f"{df['SqFt'].sum():,.2f}")
        if "Credits" in df.columns:
            col3.metric("Créditos Totales ($)", f"${df['Credits'].sum():,.2f}")
        if "Priority" in df.columns:
            rush_count = len(df[df['Priority'].isin(['RUSH', 'HIGH'])])
            col4.metric("Prioridad RUSH / HIGH", rush_count)

        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if "Material" in df.columns and "Credits" in df.columns:
                st.subheader("Créditos por Material")
                fig_mat = px.bar(df, x="Material", y="Credits", color="Material", text_auto=True)
                st.plotly_chart(fig_mat, use_container_width=True)
        with c2:
            if "Company" in df.columns:
                st.subheader("Distribución por Empresa")
                fig_comp = px.pie(df, names="Company", hole=0.4)
                st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("No hay datos disponibles en la hoja de cálculo.")

# 2. NUEVO TRABAJO
elif opcion == "➕ Nuevo Trabajo":
    st.title("➕ Registrar Nuevo Trabajo")
    
    with st.form("job_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            job_id = st.text_input("ID de Trabajo (ej. JG-2026-0001)")
            company = st.text_input("Empresa / Cliente")
            material = st.selectbox("Material", ["Quartz", "Porcelain", "Granite", "Marble", "Otro"])
        with col2:
            sqft = st.number_input("SqFt (Pies Cuadrados)", min_value=0.0, step=0.1)
            credits = st.number_input("Créditos ($)", min_value=0.0, step=1.0)
            priority = st.selectbox("Prioridad", ["LOW", "MEDIUM", "HIGH", "RUSH"])

        submitted = st.form_submit_button("Guardar en Google Sheets")
        
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
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("La hoja está vacía actualmente.")
