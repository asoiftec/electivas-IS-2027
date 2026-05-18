import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import os

# Configuración de la página
st.set_page_config(
    page_title="Electivas IF (IS-2027) - Análisis de Resultados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Electivas IF (IS-2027) - Análisis de Resultados")
st.markdown("Visualiza estadísticas del sondeo de electivas para el primer semestre 2027.")

# Carga de datos 
@st.cache_data
def cargar_datos():
    ruta_base = Path(__file__).parent
    ruta_csv = ruta_base / "prematricula_preprocesada.csv"
    
    df = pd.read_csv(ruta_csv)
    return df

df = cargar_datos()

# Diccionario de códigos y nombres
codigos_nombres = {
    "IF6004": "Física de Plasmas para Ingeniería I",
    "IF6005": "Física de Plasmas para Ingeniería II",
    "IF6007": "Aplicaciones de Física en Medicina y Biología I",
    "IF6009": "Aplicaciones de Física en Medicina y Biología II",
    "IF6008": "Tópicos de Astronomía y Astrofísica",
    "IF6010": "Laboratorio de Metrología II",
    "IF6011": "Exploración y análisis estadístico de datos experimentales",
    "IF6012": "Dinámica de Espines y Resonancia Magnética Nuclear",
    "IF6013": "Modelado Predictivo Aplicado",
    "IF60AA": "Gestión de la calidad y Sistemas Normalizados para Ingeniería Física",
    "IF60BB": "Filosofía de la ciencia, filosofía de la física",
    "IF60CC": "Análisis de Fallas y Microscopía Aplicada a Materiales de Ingeniería"
}
nombres_ordenados = sorted(codigos_nombres.values())
nombre_a_codigo = {v: k for k, v in codigos_nombres.items()}

# Barra lateral
st.sidebar.markdown("## 📌 Opciones disponibles:")
opcion = st.sidebar.radio(
    "Quiero ver:",
    ["Estadísticas generales", 
     "Resumen por curso electivo",
     "Resultados globales de electivas"],
    index=0
)

# ============================================
# SECCIÓN 1: ESTADÍSTICAS GENERALES
# ============================================
if opcion == "Estadísticas generales":
    st.header("📈 Estadísticas Generales")

    # Total de participantes
    total_participantes = len(df)
    st.metric(label="👥 Total de participantes", value=total_participantes)

    # Extraer año de ingreso desde el carné 
    df["Año de ingreso"] = df["Carné"].astype(str).str[:4].astype(int)

    # Conteo de estudiantes por año (ordenado cronológicamente)
    conteo_por_anio = (
        df["Año de ingreso"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    conteo_por_anio.columns = ["Año de ingreso", "Cantidad"]

    # Gráfico de barras 
    fig = px.bar(
        conteo_por_anio,
        x="Año de ingreso",
        y="Cantidad",
        title="Participantes por año de ingreso",
        labels={"Cantidad": "Número de estudiantes", "Año de ingreso": "Año"},
        color="Año de ingreso",
        color_continuous_scale="Viridis",
        text_auto=True
    )
    fig.update_layout(
        showlegend=False,
        xaxis=dict(tickmode='linear', dtick=1)  # muestra todos los años
    )
    st.plotly_chart(fig, width='stretch')



# ============================================
# SECCIÓN 2: RESUMEN POR CURSO ELECTIVO
# ============================================
elif opcion == "Resumen por curso electivo":
    st.header("📋 Resumen por Curso Electivo")
    st.markdown("Selecciona un curso para ver sus resultados individuales.")

    nombre_seleccionado = st.selectbox(
        "🔍 Elegir curso:",
        options=nombres_ordenados,
        index=0
    )
    codigo_curso = nombre_a_codigo[nombre_seleccionado]

    col_interes = f"Interés {codigo_curso}"
    col_requisitos = f"Requisitos {codigo_curso}"
    col_nivel = f"Nivel {codigo_curso}"

    if col_interes not in df.columns:
        st.error(f"No se encontró la columna '{col_interes}' para el curso {nombre_seleccionado}.")
    else:
        # Interés (Sí/No)
        interes_counts = df[col_interes].value_counts().reset_index()
        interes_counts.columns = ["Interés", "Cantidad"]

        # Solo interesados (Sí)
        df_interesados = df[df[col_interes] == "Sí"]

        # Nivel de interés
        if col_nivel in df.columns:
            nivel_counts = df_interesados[col_nivel].value_counts().sort_index().reset_index()
            nivel_counts.columns = ["Nivel", "Cantidad"]
            df_interesados[col_nivel] = pd.to_numeric(df_interesados[col_nivel], errors="coerce")
            nivel_promedio = df_interesados[col_nivel].mean()
        else:
            nivel_counts = pd.DataFrame()
            nivel_promedio = None

        st.subheader(f"Resultados para **{nombre_seleccionado}**")

        # Métricas
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            si = interes_counts[interes_counts["Interés"] == "Sí"]["Cantidad"].values[0] if "Sí" in interes_counts["Interés"].values else 0
            st.metric("✅ Sí", si)
        with col_m2:
            no = interes_counts[interes_counts["Interés"] == "No"]["Cantidad"].values[0] if "No" in interes_counts["Interés"].values else 0
            st.metric("❌ No", no)
        with col_m3:
            st.metric("⭐ Nivel promedio (interesados)", 
                      f"{nivel_promedio:.2f}" if pd.notna(nivel_promedio) else "N/D")

        col_izq, col_der = st.columns(2)
        with col_izq:
            # Pie de interés
            fig_interes = px.pie(
                interes_counts,
                values="Cantidad",
                names="Interés",
                title=f"Interés en {nombre_seleccionado}",
                color="Interés",
                color_discrete_map={"Sí": "#2ca02c", "No": "#d62728"},
                hole=0.4
            )
            fig_interes.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_interes, width='stretch')

        with col_der:
            # Pie de requisitos (solo si existe la columna)
            if col_requisitos in df.columns:
                requisitos_counts = df_interesados[col_requisitos].value_counts().reset_index()
                requisitos_counts.columns = ["Requisitos", "Cantidad"]

                orden_requisitos = [
                    "Actualmente cumplo con todos los requisitos",
                    "Cumpliré con todos los requisitos al finalizar el I Semestre 2026",
                    "Cumpliré con todos los requisitos al finalizar el II Semestre 2026",
                    "No cumplo ninguno de los puntos anteriores"
                ]
                requisitos_counts["Requisitos"] = pd.Categorical(
                    requisitos_counts["Requisitos"],
                    categories=orden_requisitos,
                    ordered=True
                )
                requisitos_counts = requisitos_counts.sort_values("Requisitos")

                if not requisitos_counts.empty:
                    fig_requisitos = px.pie(
                        requisitos_counts,
                        values="Cantidad",
                        names="Requisitos",
                        title=f"Requisitos – {nombre_seleccionado} (solo quienes votaron Sí)",
                        hole=0.4
                    )
                    fig_requisitos.update_traces(textinfo="percent")
                    st.plotly_chart(fig_requisitos, width='stretch')
                else:
                    st.info("No hay datos de requisitos (ningún estudiante votó Sí).")
            else:
                st.info("ℹ️ Este curso no tiene columna de requisitos.")

        st.markdown("---")
        # Gráfico de nivel (si hay datos)
        if not nivel_counts.empty:
            fig_nivel = px.bar(
                nivel_counts,
                x="Nivel",
                y="Cantidad",
                title=f"Distribución del nivel de interés – {nombre_seleccionado}",
                labels={"Nivel": "Nivel de interés (1-5)", "Cantidad": "Estudiantes interesados"},
                text_auto=True,
                color="Nivel",
                color_continuous_scale="Blues"
            )
            fig_nivel.update_layout(showlegend=False, xaxis=dict(tickmode='linear', dtick=1))
            st.plotly_chart(fig_nivel, width='stretch')
        else:
            st.info("No hay datos de nivel de interés (ningún estudiante votó Sí).")

# ============================================
# SECCIÓN 3: RESULTADOS GLOBALES DE LAS ELECTIVAS
# ============================================
elif opcion == "Resultados globales de electivas":
    st.header("🌐 Resultados Globales de Electivas")
    st.markdown("Comparativa de interés entre todos los cursos electivos, con filtros dinámicos.")

    # Filtros de requisitos (checkboxes) 
    st.markdown("Solo se contarán estudiantes que hayan respondido **Sí** y cumplan al menos una de las condiciones seleccionadas.")

    opciones_requisitos = [
        "Actualmente cumplo con todos los requisitos",
        "Cumpliré con todos los requisitos al finalizar el I Semestre 2026",
        "Cumpliré con todos los requisitos al finalizar el II Semestre 2026",
        "No cumplo ninguno de los puntos anteriores"
    ]

    seleccionados = {}
    for req in opciones_requisitos:
        seleccionados[req] = st.checkbox(req, value=True)

    categorias_activas = [req for req, activo in seleccionados.items() if activo]

    if not categorias_activas:
        st.warning("Selecciona al menos una categoría de requisitos para visualizar los datos.")
        st.stop()

    # ---- Slider para Top N ----
    total_cursos = len(codigos_nombres)
    top_n = st.slider(
        "Cantidad de cursos a mostrar:",
        min_value=3,
        max_value=total_cursos,
        value=min(10, total_cursos),
        step=1
    )

    # ---- Construir datos para el gráfico ----
    data_global = []
    for codigo, nombre in codigos_nombres.items():
        col_interes = f"Interés {codigo}"
        col_requisitos = f"Requisitos {codigo}"

        if col_interes not in df.columns:
            continue  # por seguridad

        # Solo quienes dijeron "Sí"
        interesados = df[df[col_interes] == "Sí"]

        # Filtrar según requisitos (si la columna existe, aplicar los checkboxes; si no, contar todos)
        if col_requisitos in df.columns:
            interesados_filtrados = interesados[interesados[col_requisitos].isin(categorias_activas)]
        else:
            # Curso sin requisitos: se incluyen todos los interesados sin filtro
            interesados_filtrados = interesados

        cantidad = len(interesados_filtrados)
        data_global.append({"Curso": nombre, "Interesados": cantidad})

    df_global = pd.DataFrame(data_global)

    # Ordenar descendente y tomar Top N
    df_global = df_global.sort_values("Interesados", ascending=False).head(top_n)

    # ---- Gráfico de barras horizontal ----
    if df_global.empty:
        st.warning("No hay estudiantes que cumplan los criterios seleccionados.")
    else:
        fig_global = px.bar(
            df_global,
            x="Interesados",
            y="Curso",
            orientation='h',
            title=f"Top {top_n} cursos con mayor interés (según filtros de requisitos)",
            labels={"Interesados": "Cantidad de estudiantes interesados", "Curso": ""},
            text_auto=True,
            color="Interesados",
            color_continuous_scale="Viridis"
        )
        fig_global.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            height=400 + top_n * 30
        )
        st.plotly_chart(fig_global, width='stretch')

    st.caption("💡 Solo se consideran estudiantes que marcaron **Sí** en la pregunta de interés. "
               "Si el curso no tiene columna de requisitos, se cuentan todos los que dijeron Sí sin filtrar.")
