import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="JG-OperationSystem | Production Control",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ESTILOS CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
    }
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    .stButton>button, .stFormSubmitButton>button {
        background-color: #0f766e !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100%;
        padding: 0.6rem 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# CONEXIÓN APUNTANDO DIRECTO A LA PESTAÑA 'Production Intake'
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Lee la pestaña exacta 'Production Intake' saltando las primeras 3 filas de encabezado/instrucciones
    df = conn.read(worksheet="Production Intake", skiprows=3, ttl="0d")
    
    # Limpiar columnas vacías y convertir números
    df = df.dropna(how="all")
    if 'SqFt' in df.columns:
        df['SqFt'] = pd.to_numeric(df['SqFt'], errors='coerce').fillna(0)
    
    return df

# NAVEGACIÓN
st.sidebar.markdown("# 💎 Stone Ops")
st.sidebar.caption("Production Control 3.0")
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Navegación",
    ["📊 Dashboard Interactivo", "➕ Nuevo Trabajo", "📋 Lista de Trabajos"]
)

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al leer la hoja: {e}")
    df = pd.DataFrame()

# 1. DASHBOARD INTERACTIVO
if opcion == "📊 Dashboard Interactivo":
    st.title("Panel de Control Ejecutivo")
    st.caption("Sincronizado con Production Intake")
    st.markdown("<br>", unsafe_allow_html=True)

    if not df.empty and 'Job ID' in df.columns:
        # Filtrar solo registros válidos con Job ID
        df_valid = df[df['Job ID'].notnull() & (df['Job ID'] != "")]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Trabajos Totales", len(df_valid))
        
        sqft_val = df_valid['SqFt'].sum() if 'SqFt' in df.columns else 0.0
        col2.metric("SqFt Totales", f"{sqft_val:,.2f}")
        
        # Estimación / Créditos si aplica
        credits_est = sqft_val * 3.8  # Ratio promedio de créditos por SqFt
        col3.metric("Créditos Est. ($)", f"${credits_est:,.2f}")
        
        slabs_val = df_valid['Slabs'].sum() if 'Slabs' in df.columns else 0
        col4.metric("Slabs Totales", int(slabs_val))

        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if 'Material' in df.columns and 'SqFt' in df.columns:
                st.subheader("SqFt por Material")
                df_mat = df_valid.groupby('Material', as_index=False)['SqFt'].sum()
                fig_mat = px.bar(
                    df_mat, x="Material", y="SqFt", color="Material",
                    color_discrete_sequence=px.colors.qualitative.Emerald, text_auto='.1f'
                )
                fig_mat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig_mat, use_container_width=True)
                
        with c2:
            if 'Company' in df.columns:
                st.subheader("Distribución por Empresa")
                fig_comp = px.pie(
                    df_valid, names="Company", hole=0.5,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_comp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Cargando datos desde Production Intake...")

# 2. NUEVO TRABAJO
elif opcion == "➕ Nuevo Trabajo":
    st.title("➕ Registrar en Production Intake")
    
    with st.form("job_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            company = st.selectbox("Company", ["Infinity Stone", "UGM", "Otro"])
            client = st.text_input("Client")
            project = st.text_input("Project / Address")
            material = st.selectbox("Material", ["Quartz", "Marble", "Porcelain", "Granite", "Quartzite"])
        with col2:
            material_name = st.text_input("Material Name (ej. 3cm Organic White)")
            sqft = st.number_input("SqFt", min_value=0.0, step=0.1)
            slabs = st.number_input("Slabs", min_value=1, step=1)
            slab_type = st.selectbox("Slab Type", ["Full Slab", "Remnant"])

        submitted = st.form_submit_button("💾 Guardar en Google Sheets")
        
        if submitted:
            # Generar siguiente Job ID automáticamente (JG-2026-XXXX)
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
            st.success(f"¡Trabajo {new_job_id} registrado en Google Sheets!")
            st.cache_data.clear()

# 3. LISTA DE TRABAJOS
elif opcion == "📋 Lista de Trabajos":
    st.title("📋 Production Intake - Lista General")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay datos disponibles.")
