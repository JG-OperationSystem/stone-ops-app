import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import date

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Gestión de Trabajos | JG-OperationSystem",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "stone_ops.db"

# ---------------------------------------------------------
# FUNCIONES DE BASE DE DATOS (SQLITE)
# ---------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            company TEXT,
            client TEXT,
            project TEXT,
            job_number TEXT,
            material TEXT,
            material_name TEXT,
            sqft REAL,
            slabs INTEGER,
            slab_type TEXT,
            edge_type TEXT,
            priority TEXT,
            assigned_employee TEXT,
            credits REAL,
            date_received TEXT
        )
    """)
    
    # Cargar datos de muestra iniciales si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM jobs")
    if cursor.fetchone()[0] == 0:
        initial_data = [
            ("JG-2026-0001", "Infinity Stone", "Space Construction", "3109 Emory Dr", "26-0720", "Quartz", "3cm Organic White", 62.54, 1, "Full Slab", "Flat", "NORMAL", "Juan", 95.0, "2026-07-23"),
            ("JG-2026-0008", "Infinity Stone", "David Davis", "4217 Edgewiev Dr", "N/A", "Porcelain", "12mm Calacata Apuano", 93.60, 2, "Full Slab", "Miter Edge", "NORMAL", "Jorge", 520.0, "2026-07-21"),
            ("JG-2026-0013", "UGM", "Roman Galindo", "2352 Palazzo Ln", "N/A", "Quartz", "3cm Alabaster", 7.91, 1, "Remnant", "Flat", "RUSH", "Jose", 7.91, "2026-07-23")
        ]
        cursor.executemany("""
            INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_data)
        conn.commit()
    conn.close()

def load_jobs_data():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    conn.close()
    
    # Renombrar columnas para la interfaz visual
    df = df.rename(columns={
        "job_id": "Job ID",
        "company": "Company",
        "client": "Client",
        "project": "Project",
        "job_number": "Job Number",
        "material": "Material",
        "material_name": "Material Name",
        "sqft": "SqFt",
        "slabs": "Slabs",
        "slab_type": "Slab Type",
        "edge_type": "Edge Type",
        "priority": "Priority",
        "assigned_employee": "Assigned Employee",
        "credits": "Credits",
        "date_received": "Date Received"
    })
    return df

def save_job(job_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs VALUES (
            :job_id, :company, :client, :project, :job_number,
            :material, :material_name, :sqft, :slabs, :slab_type,
            :edge_type, :priority, :assigned_employee, :credits, :date_received
        )
    """, job_data)
    conn.commit()
    conn.close()

# Inicializar base de datos
init_db()
df = load_jobs_data()

# ---------------------------------------------------------
# NAVEGACIÓN DE BARRA LATERAL
# ---------------------------------------------------------
st.sidebar.title("💎 JG-OperationSystem")
st.sidebar.caption("Sistema de Gestión de Fabricación")
st.sidebar.markdown("---")
option = st.sidebar.radio(
    "Navegación",
    ["📊 Dashboard Interactivo", "➕ Nuevo Trabajo", "📋 Lista de Trabajos"]
)

# ---------------------------------------------------------
# 1. DASHBOARD INTERACTIVO
# ---------------------------------------------------------
if option == "📊 Dashboard Interactivo":
    st.title("📊 Panel de Control Ejecutivo")
    st.markdown("Visualización en tiempo real del estado de producción y créditos guardados en la Base de Datos.")
    st.markdown("---")

    if df.empty:
        st.warning("No hay trabajos registrados en la base de datos todavía.")
    else:
        # Métricas Principales (KPIs)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Trabajos Totales", len(df))
        with col2:
            st.metric("SqFt Totales", f"{df['SqFt'].sum():,.2f}")
        with col3:
            st.metric("Créditos Totales ($)", f"${df['Credits'].sum():,.2f}")
        with col4:
            rush_count = len(df[df['Priority'].isin(['RUSH', 'HIGH'])])
            st.metric("Prioridad RUSH / HIGH", rush_count)

        st.markdown("---")

        # Gráficos
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("Créditos Acumulados por Material")
            fig_mat = px.bar(
                df.groupby('Material', as_index=False)['Credits'].sum(),
                x='Credits', y='Material', orientation='h',
                color='Credits', color_continuous_scale='Greens',
                text_auto=True
            )
            fig_mat.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig_mat, use_container_width=True)

        with g2:
            st.subheader("Distribución por Empresa")
            fig_comp = px.pie(
                df, names='Company', hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_comp.update_layout(template="plotly_dark")
            st.plotly_chart(fig_comp, use_container_width=True)

        g3, g4 = st.columns(2)

        with g3:
            st.subheader("Rendimiento por Empleado (SqFt)")
            fig_emp = px.bar(
                df.groupby('Assigned Employee', as_index=False)['SqFt'].sum(),
                x='Assigned Employee', y='SqFt',
                color='Assigned Employee', color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_emp.update_layout(template="plotly_dark")
            st.plotly_chart(fig_emp, use_container_width=True)

        with g4:
            st.subheader("Top Clientes por Losas (Slabs)")
            top_clients = df.groupby('Client', as_index=False)['Slabs'].sum().sort_values(by='Slabs', ascending=False).head(5)
            fig_cli = px.bar(
                top_clients, x='Slabs', y='Client', orientation='h',
                color='Slabs', color_continuous_scale='Oranges', text_auto=True
            )
            fig_cli.update_layout(template="plotly_dark")
            st.plotly_chart(fig_cli, use_container_width=True)

# ---------------------------------------------------------
# 2. FORMULARIO DE NUEVO TRABAJO
# ---------------------------------------------------------
elif option == "➕ Nuevo Trabajo":
    st.title("➕ Carga de Nuevo Trabajo")
    st.markdown("Ingresa los datos del nuevo proyecto. La información se guardará permanentemente en SQLite.")
    st.markdown("---")

    with st.form("new_job_form", clear_on_submit=True):
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.subheader("1. General")
            company = st.selectbox("Empresa", ["Infinity Stone", "UGM", "Otro"])
            client = st.text_input("Cliente", placeholder="Ej. Roman Galindo")
            project = st.text_input("Dirección del Proyecto", placeholder="Ej. 105 N Benge St")
            job_number = st.text_input("Job Number", value="N/A")

        with col_b:
            st.subheader("2. Especificaciones")
            material = st.selectbox("Material Base", ["Quartz", "Granite", "Quartzite", "Marble", "Porcelain"])
            material_name = st.text_input("Nombre / Grosor del Material", placeholder="Ej. 3cm Honeydew")
            sqft = st.number_input("Pies Cuadrados (SqFt)", min_value=0.0, step=0.1, value=50.0)
            slabs = st.number_input("Cantidad de Losas (Slabs)", min_value=1, step=1, value=1)
            slab_type = st.selectbox("Tipo de Losa", ["Full Slab", "Remnant"])
            edge_type = st.selectbox("Tipo de Borde/Canto", ["Flat", "Miter Edge", "1/4 Bevel", "Demi", "Ogee", "Custom"])

        with col_c:
            st.subheader("3. Asignación y Fechas")
            priority = st.selectbox("Prioridad", ["NORMAL", "HIGH", "RUSH"])
            employee = st.selectbox("Empleado Asignado", ["Jorge", "Juan", "Jose"])
            date_received = st.date_input("Fecha de Recepción", value=date.today())
            credits = st.number_input("Créditos Calculados ($)", min_value=0.0, step=5.0, value=100.0)

        submitted = st.form_submit_button("⚡ Guardar en Base de Datos", use_container_width=True)

        if submitted:
            new_id = f"JG-2026-{len(df) + 1:04d}"
            job_dict = {
                "job_id": new_id,
                "company": company,
                "client": client if client else "N/A",
                "project": project if project else "N/A",
                "job_number": job_number if job_number else "N/A",
                "material": material,
                "material_name": material_name if material_name else "N/A",
                "sqft": sqft,
                "slabs": slabs,
                "slab_type": slab_type,
                "edge_type": edge_type,
                "priority": priority,
                "assigned_employee": employee,
                "credits": credits,
                "date_received": str(date_received)
            }
            save_job(job_dict)
            st.success(f"¡Trabajo guardado permanentemente! ID asignado: {new_id}")
            st.rerun()

# ---------------------------------------------------------
# 3. LISTA Y GESTIÓN DE TRABAJOS
# ---------------------------------------------------------
elif option == "📋 Lista de Trabajos":
    st.title("📋 Registro General de Trabajos")
    st.markdown("Busca, filtra y revisa los detalles guardados en SQLite.")
    st.markdown("---")

    # Buscador rápido
    search_term = st.text_input("🔍 Buscar por Cliente, Proyecto o ID de Trabajo:", "")

    filtered_df = df.copy()
    if search_term and not filtered_df.empty:
        filtered_df = filtered_df[
            filtered_df['Client'].str.contains(search_term, case=False, na=False) |
            filtered_df['Project'].str.contains(search_term, case=False, na=False) |
            filtered_df['Job ID'].str.contains(search_term, case=False, na=False)
        ]

    st.dataframe(filtered_df, use_container_width=True)
