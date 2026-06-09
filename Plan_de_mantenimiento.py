
import streamlit as st
import plotly.graph_objects as go
import io
import pandas as pd

from datos import (
    nombres, descripciones, tipos,
    R, w, c, a, b,
    B_nominal, H_nominal, J_critico,
)
from modelo_optimizacion import construir_modelo, resolver_modelo
from cotas_analiticas import heuristica_greedy_dual
from datetime import datetime, date, timedelta

# Configuracion basica de la pagina
st.set_page_config(
    page_title="Plan de mantenimiento",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta de colores
COLORES = {
    "azul_ufv":       "#003F72",
    "azul_electrico": "#0099CC",
    "fondo":          "#FAF8F5",
    "fondo_sidebar":  "#F0EDE6",
    "texto_oscuro":   "#1A1A1A",
    "texto_medio":    "#6B6B6B",
    "separador":      "#E5E1D8",
}

# Formateo de numeros en castellano
def es_miles(n):
    """Entero con punto como separador de miles. 10200 -> '10.200'."""
    return f"{int(round(n)):,}".replace(",", ".")


def es_decimal(n, decimales=2):
    """Numero con coma decimal y punto de miles. 10200.45 -> '10.200,45'."""
    formateado = f"{n:,.{decimales}f}"
    # En el resultado anglosajon: la coma separa miles, el punto separa decimal.
    return formateado.replace(",", "§").replace(".", ",").replace("§", ".")

# Callbacks de sincronizacion entre slider e input
def actualizar_B_desde_slider():
    st.session_state.B_valor = st.session_state.B_slider_key
    st.session_state.B_input_key = st.session_state.B_slider_key

def actualizar_B_desde_input():
    st.session_state.B_valor = st.session_state.B_input_key
    st.session_state.B_slider_key = st.session_state.B_input_key

def actualizar_H_desde_slider():
    st.session_state.H_valor = st.session_state.H_slider_key
    st.session_state.H_input_key = st.session_state.H_slider_key

def actualizar_H_desde_input():
    st.session_state.H_valor = st.session_state.H_input_key
    st.session_state.H_slider_key = st.session_state.H_input_key


# CSS personalizado
CSS_BASE = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@300;400;500;600;700&family=Material+Symbols+Rounded&display=swap" rel="stylesheet">

<style>
    /* Fondo general */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {COLORES["fondo"]} !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div {{
        background-color: {COLORES["fondo_sidebar"]} !important;
        border-right: 1px solid {COLORES["separador"]} !important;
    }}

    /* Tipografia general */
    [data-testid="stAppViewContainer"] *,
    [data-testid="stSidebar"] *,
    .stMarkdown, .stMarkdown *,
    p, span, div, li, label, button {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: {COLORES["texto_oscuro"]};
    }}

/* Iconos de Material Symbols — aplicado a los botones del header
       interno del sidebar (cuando esta abierto) y a los iconos auxiliares.
       Se excluye deliberadamente el control colapsado del sidebar, que
       se trata mas abajo con un fallback unicode controlado. */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] *,
    button[kind="headerNoPadding"] *,
    [class*="iconContainer"] *,
    [class*="IconContainer"] *,
    span[class*="material"],
    .material-symbols-rounded,
    .material-icons,
    .material-symbols-outlined {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-feature-settings: 'liga' !important;
        font-weight: normal !important;
        font-style: normal !important;
        text-transform: none !important;
        letter-spacing: normal !important;
        word-wrap: normal !important;
        white-space: nowrap !important;
        direction: ltr !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
        font-size: 1.5rem !important;
    }}

    
    
/* Fallback solo para el control colapsado del sidebar.
       Cuando el sidebar esta cerrado, Streamlit lo pone en la esquina
       superior izquierda con el texto "keyboard_double_arrow_right". Si
       la fuente Material Symbols no se aplica (problema conocido en
       algunas versiones), el texto se ve tal cual. Aqui ocultamos
       cualquier texto de ese contenedor concreto y pintamos un chevron
       unicode propio. Selector acotado: solo afecta a este contenedor,
       NO al boton Deploy ni al resto del header. */
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button {{
        position: relative !important;
        color: transparent !important;
        text-indent: -9999px !important;
        overflow: hidden !important;
        width: 2.5rem !important;
        height: 2.5rem !important;
    }}
    [data-testid="stSidebarCollapsedControl"] button::before,
    [data-testid="collapsedControl"] button::before {{
        content: "›" !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        text-indent: 0 !important;
        font-family: 'Fraunces', Georgia, serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: {COLORES["texto_oscuro"]} !important;
    }}

    /* Expanders: ocultar icono roto y dibujar caret limpio */
    [data-testid="stExpander"] summary {{
        position: relative !important;
        padding-right: 2rem !important;
    }}
    [data-testid="stExpander"] summary span[class*="icon" i],
    [data-testid="stExpander"] summary [data-testid*="icon" i],
    [data-testid="stExpander"] summary svg {{
        display: none !important;
    }}
    [data-testid="stExpander"] summary::after {{
        content: "›" !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 400 !important;
        color: {COLORES["texto_medio"]} !important;
        position: absolute !important;
        right: 0.8rem !important;
        top: 50% !important;
        transform: translateY(-50%) rotate(90deg) !important;
        transition: transform 0.2s ease !important;
        pointer-events: none !important;
    }}
    [data-testid="stExpander"] details[open] summary::after {{
        transform: translateY(-50%) rotate(-90deg) !important;
    }}

    /* Forzar visibilidad del boton de cerrar sidebar */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] button[kind="headerNoPadding"] {{
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] button,
    [data-testid="stSidebar"] header button {{
        opacity: 1 !important;
        visibility: visible !important;
    }}

    /* Titulares en serif Fraunces */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stHeading"] *,
    [data-testid="stHeading"],
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h1 *,
    [data-testid="stMarkdownContainer"] h2 *,
    [data-testid="stMarkdownContainer"] h3 * {{
        font-family: 'Fraunces', Georgia, 'Times New Roman', serif !important;
        font-weight: 600 !important;
        color: {COLORES["texto_oscuro"]} !important;
        letter-spacing: -0.01em !important;
    }}

    /* H1 mas grande y peso */
    h1, [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h1 *,
    [data-testid="stHeading"] h1 {{
        font-weight: 700 !important;
        font-size: 2.8rem !important;
        line-height: 1.1 !important;
        margin-bottom: 0.4rem !important;
    }}

    /* H2 / H3 */
    h2, [data-testid="stMarkdownContainer"] h2 {{
        font-size: 1.8rem !important;
        margin-top: 1.5rem !important;
    }}
    h3, [data-testid="stMarkdownContainer"] h3 {{
        font-size: 1.3rem !important;
    }}

    /* Subtitulo */
    .subtitulo, .subtitulo * {{
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1rem !important;
        color: {COLORES["texto_medio"]} !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
        margin-bottom: 1.8rem !important;
    }}

    /* Linea horizontal */
    hr {{
        border: none !important;
        border-top: 1px solid {COLORES["separador"]} !important;
        margin: 1.5rem 0 2rem 0 !important;
    }}

    /* Ocultar elementos por defecto */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background-color: transparent !important; }}

    /* Estilo del botón Deploy del header — mismo aspecto que en Inputs.
       Override sobre el bloque de Material Symbols anterior, que aplicaba
       Fraunces grande por efecto colateral. */
    /* Estilo Fraunces sobre el boton Deploy del header, salvo los iconos
       Material (span data-testid="stIconMaterial"), que necesitan
       conservar su fuente para renderizar como simbolo y no como texto.
       Esto resuelve el bug del icono "keyboard_double_arrow_right" que
       aparecia como texto cuando el sidebar estaba cerrado. */
    [data-testid="stHeader"] button[kind="header"],
    [data-testid="stHeader"] button[kind="headerNoPadding"],
    [data-testid="stHeader"] button[kind="header"] *:not([data-testid="stIconMaterial"]),
    [data-testid="stHeader"] button[kind="headerNoPadding"] *:not([data-testid="stIconMaterial"]) {{
        font-family: 'Fraunces', serif !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em !important;
        color: {COLORES["texto_oscuro"]} !important;
        text-transform: uppercase !important;
        font-variation-settings: normal !important;
    }}

    /* Iconos Material dentro del header: usan su fuente propia. */
    [data-testid="stIconMaterial"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-feature-settings: 'liga' !important;
        font-weight: normal !important;
        font-style: normal !important;
        text-transform: none !important;
        letter-spacing: normal !important;
        font-size: 1.5rem !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
    }}

    /* Padding del contenedor */
    .main .block-container, [data-testid="stMainBlockContainer"] {{
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }}

    /* Etiquetas de seccion en sidebar */
    .sidebar-section {{
        font-family: 'Inter', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.12em !important;
        color: {COLORES["azul_ufv"]} !important;
        text-transform: uppercase !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
    }}

    /* Slider: color azul UFV en vez del rojo por defecto */
    [data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
        background-color: {COLORES["azul_ufv"]} !important;
        border-color: {COLORES["azul_ufv"]} !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="slider"] > div > div > div {{
        background: {COLORES["azul_ufv"]} !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="slider"] > div > div {{
        background: {COLORES["separador"]} !important;
    }}
    
/* === TARJETAS KPI: estilo dashboard premium con degradado y formas === */

    /* Todas las tarjetas con la misma altura */
    .kpi-tarjeta {{
        position: relative;
        overflow: hidden;
        min-height: 240px;
        padding: 1.7rem 1.6rem 1.6rem 1.6rem;
        border-radius: 12px;
        background: linear-gradient(
            135deg,
            #00528F 0%,
            #1670B0 60%,
            #2A85C4 100%
        );
        box-shadow:
            0 4px 14px rgba(0, 60, 110, 0.20),
            0 1px 0 rgba(255, 255, 255, 0.12) inset;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }}

    .kpi-tarjeta:hover {{
        transform: translateY(-3px);
        box-shadow:
            0 8px 22px rgba(0, 60, 110, 0.28),
            0 1px 0 rgba(255, 255, 255, 0.15) inset;
    }}

    /* Decoracion organica: dos circulos translucidos */
    .kpi-tarjeta::before {{
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        right: -70px;
        top: -70px;
        background: radial-gradient(
            circle,
            rgba(255, 255, 255, 0.13) 0%,
            rgba(255, 255, 255, 0) 70%
        );
        border-radius: 50%;
        pointer-events: none;
    }}
    .kpi-tarjeta::after {{
        content: "";
        position: absolute;
        width: 120px;
        height: 120px;
        right: 40px;
        bottom: -50px;
        background: radial-gradient(
            circle,
            rgba(255, 255, 255, 0.09) 0%,
            rgba(255, 255, 255, 0) 70%
        );
        border-radius: 50%;
        pointer-events: none;
    }}

    /* Variante verde menta para la tarjeta de ganancia (cuando es positiva) */
    .kpi-tarjeta-verde {{
        background: linear-gradient(
            135deg,
            #5BB47C 0%,
            #74C492 60%,
            #8BD4A8 100%
        ) !important;
        box-shadow:
            0 4px 14px rgba(91, 180, 124, 0.22),
            0 1px 0 rgba(255, 255, 255, 0.14) inset !important;
    }}
    .kpi-tarjeta-verde:hover {{
        box-shadow:
            0 8px 22px rgba(91, 180, 124, 0.30),
            0 1px 0 rgba(255, 255, 255, 0.17) inset !important;
    }}

    /* Variante gris grafito para la tarjeta de ganancia (cuando es 0 o negativa) */
    .kpi-tarjeta-neutra {{
        background: linear-gradient(
            135deg,
            #4A5568 0%,
            #5C6878 60%,
            #718096 100%
        ) !important;
        box-shadow:
            0 4px 14px rgba(74, 85, 104, 0.20),
            0 1px 0 rgba(255, 255, 255, 0.12) inset !important;
    }}
    .kpi-tarjeta-neutra:hover {{
        box-shadow:
            0 8px 22px rgba(74, 85, 104, 0.28),
            0 1px 0 rgba(255, 255, 255, 0.15) inset !important;
    }}

    /* Etiqueta del KPI: mas grande y legible */
    .kpi-etiqueta {{
        position: relative;
        z-index: 2;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.10em !important;
        text-transform: uppercase !important;
        color: rgba(255, 255, 255, 0.95) !important;
        margin-bottom: 0.6rem !important;
        line-height: 1.35 !important;
        min-height: 2.6rem !important;
    }}

    /* Numero principal */
    .kpi-numero {{
        position: relative;
        z-index: 2;
        font-family: 'Fraunces', Georgia, serif !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        line-height: 1 !important;
        margin: 0.4rem 0 0.5rem 0 !important;
        letter-spacing: -0.02em !important;
    }}

    /* Unidad (%, h, /20, etc) */
    .kpi-unidad {{
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
        color: rgba(255, 255, 255, 0.78) !important;
        margin-left: 0.3rem !important;
    }}

    /* Subtitulo: mas grande y legible */
    .kpi-contexto {{
        position: relative;
        z-index: 2;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        color: rgba(255, 255, 255, 0.88) !important;
        margin-top: auto !important;
        padding-top: 0.8rem !important;
        line-height: 1.5 !important;
    }}

    /* Barra de progreso: mas gruesa */
    .kpi-barra-fondo {{
        position: relative;
        z-index: 2;
        height: 7px;
        background-color: rgba(255, 255, 255, 0.22);
        border-radius: 4px;
        margin-top: 0.7rem;
        overflow: hidden;
    }}
    .kpi-barra-relleno {{
        height: 100%;
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 4px;
        transition: width 0.3s ease;
    }}
    
    /* Variante para KPIs sin contexto (cobertura del plan y activos en el plan):
       el numero crece, se centra verticalmente y la barra se ancla al fondo. */
    .kpi-tarjeta-simple .kpi-numero {{
            font-size: 4.5rem !important;
            margin-top: 0 !important;
            margin-bottom: 1rem !important;
        }}
        .kpi-tarjeta-simple .kpi-unidad {{
            font-size: 1.2rem !important;
        }}
        .kpi-tarjeta-simple {{
            justify-content: space-between !important;
        }}
        .kpi-tarjeta-simple .kpi-numero-centrado {{
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 !important;
        }}
</style>
"""

st.markdown(CSS_BASE, unsafe_allow_html=True)


# Estado de sesion inicial
if "B_valor" not in st.session_state:
    st.session_state.B_valor = int(B_nominal)
if "H_valor" not in st.session_state:
    st.session_state.H_valor = int(H_nominal)

# Pesos AHP — uno por criterio. Por defecto los valores nominales del
if "w1_valor" not in st.session_state:
    st.session_state.w1_valor = float(w[0])
if "w2_valor" not in st.session_state:
    st.session_state.w2_valor = float(w[1])
if "w3_valor" not in st.session_state:
    st.session_state.w3_valor = float(w[2])
if "w4_valor" not in st.session_state:
    st.session_state.w4_valor = float(w[3])

# Activos criticos forzados — un booleano por activo. Por defecto solo
for j in range(len(nombres)):
    key = f"critico_{j}_valor"
    if key not in st.session_state:
        st.session_state[key] = (j in J_critico)


# Sidebar — Estructura completa con las cuatro secciones del dashboard
with st.sidebar:


    # Seccion PARÁMETROS
    st.markdown(
        "<div class='sidebar-section'>PARÁMETROS</div>",
        unsafe_allow_html=True,
    )

# --- Presupuesto B ---
    st.markdown(
        "<div style='font-size: 0.88rem; color: #6B6B6B; "
        "margin-bottom: 0.3rem; font-weight: 500;'>"
        "Presupuesto (€)"
        "</div>",
        unsafe_allow_html=True,
    )
    st.slider(
        "B_slider",
        min_value=0,
        max_value=250_000,
        value=st.session_state.B_valor,
        step=1_000,
        key="B_slider_key",
        on_change=actualizar_B_desde_slider,
        label_visibility="collapsed",
    )
    st.number_input(
        "B_input",
        min_value=0,
        max_value=250_000,
        value=st.session_state.B_valor,
        step=1_000,
        key="B_input_key",
        on_change=actualizar_B_desde_input,
        label_visibility="collapsed",
    )

    # --- Horas-hombre H ---
    st.markdown(
        "<div style='font-size: 0.88rem; color: #6B6B6B; "
        "margin-top: 1rem; margin-bottom: 0.3rem; font-weight: 500;'>"
        "Horas-hombre (h)"
        "</div>",
        unsafe_allow_html=True,
    )
    st.slider(
        "H_slider",
        min_value=0,
        max_value=150,
        value=st.session_state.H_valor,
        step=1,
        key="H_slider_key",
        on_change=actualizar_H_desde_slider,
        label_visibility="collapsed",
    )
    st.number_input(
        "H_input",
        min_value=0,
        max_value=150,
        value=st.session_state.H_valor,
        step=1,
        key="H_input_key",
        on_change=actualizar_H_desde_input,
        label_visibility="collapsed",
    )
    
    # --- Boton de restablecer nominales ---
    if st.button("Restablecer nominales", use_container_width=True):
        # Borramos las keys de los widgets (las que pueden tener cache interna
        for k in ("B_slider_key", "B_input_key", "H_slider_key", "H_input_key"):
            if k in st.session_state:
                del st.session_state[k]
        # Redefinimos las keys con el valor nominal explicitamente. Como
        st.session_state.B_valor = int(B_nominal)
        st.session_state.H_valor = int(H_nominal)
        st.session_state.B_slider_key = int(B_nominal)
        st.session_state.B_input_key = int(B_nominal)
        st.session_state.H_slider_key = int(H_nominal)
        st.session_state.H_input_key = int(H_nominal)
        st.rerun()

    # Seccion MODELO
    st.markdown(
        "<div class='sidebar-section' style='margin-top: 2rem;'>MODELO</div>",
        unsafe_allow_html=True,
    )
    with st.expander("Ver detalles del modelo", expanded=False):
        # Lectura de los pesos actuales desde session_state. Se normalizan
        w1_actual = st.session_state.get("w1_valor", float(w[0]))
        w2_actual = st.session_state.get("w2_valor", float(w[1]))
        w3_actual = st.session_state.get("w3_valor", float(w[2]))
        w4_actual = st.session_state.get("w4_valor", float(w[3]))
        suma_pesos = w1_actual + w2_actual + w3_actual + w4_actual
        if suma_pesos > 0:
            w1_norm = w1_actual / suma_pesos
            w2_norm = w2_actual / suma_pesos
            w3_norm = w3_actual / suma_pesos
            w4_norm = w4_actual / suma_pesos
        else:
            w1_norm, w2_norm, w3_norm, w4_norm = w[0], w[1], w[2], w[3]

        # Formato castellano (coma decimal) con cuatro decimales
        def _fmt(x):
            return f"{x:.4f}".replace(".", ",")

        # El ratio de consistencia (CR) es una propiedad de la matriz de
        pesos_son_nominales = (
            abs(w1_actual - float(w[0])) < 1e-4 and
            abs(w2_actual - float(w[1])) < 1e-4 and
            abs(w3_actual - float(w[2])) < 1e-4 and
            abs(w4_actual - float(w[3])) < 1e-4
        )

        if pesos_son_nominales:
            linea_cr = (
                "<strong>Ratio de consistencia:</strong> 3,68 % &lt; 10 % ✓"
            )
        else:
            linea_cr = (
                "<em style='color: #6B6B6B; font-size: 0.78rem;'>"
                "Ratio de consistencia no aplicable con pesos modificados."
                "</em>"
            )

        st.markdown(
            f"<div style='font-size: 0.85rem; line-height: 1.6;'>"
            f"<strong>Activos:</strong> 20<br>"
            f"<strong>Criterios:</strong> 4<br>"
            f"&nbsp;&nbsp;Probabilidad de fallo<br>"
            f"&nbsp;&nbsp;Impacto del fallo<br>"
            f"&nbsp;&nbsp;Coste de intervención<br>"
            f"&nbsp;&nbsp;Tiempo de intervención<br>"
            f"<strong>Pesos AHP:</strong><br>"
            f"&nbsp;&nbsp;w₁ = {_fmt(w1_norm)} (probabilidad)<br>"
            f"&nbsp;&nbsp;w₂ = {_fmt(w2_norm)} (impacto)<br>"
            f"&nbsp;&nbsp;w₃ = {_fmt(w3_norm)} (coste)<br>"
            f"&nbsp;&nbsp;w₄ = {_fmt(w4_norm)} (tiempo)<br>"
            f"{linea_cr}"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Seccion ANÁLISIS AVANZADO
    st.markdown(
        "<div class='sidebar-section' style='margin-top: 2rem;'>ANÁLISIS AVANZADO</div>",
        unsafe_allow_html=True,
    )
    with st.expander("Modificar pesos AHP", expanded=False):
        st.markdown(
            "<div style='font-size: 0.8rem; color: #6B6B6B; font-style: italic; "
            "margin-bottom: 0.8rem;'>"
            "Para análisis de sensibilidad. Si los pesos no suman 1, se "
            "normalizan automáticamente al aplicar."
            "</div>",
            unsafe_allow_html=True,
        )

        # w1 — Probabilidad de fallo
        st.markdown(
            "<div style='font-size: 0.82rem; color: #6B6B6B; "
            "margin-bottom: 0.1rem; font-weight: 500;'>"
            "Probabilidad de fallo (w₁)"
            "</div>",
            unsafe_allow_html=True,
        )
        st.number_input(
            "w1",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.w1_valor,
            step=0.05,
            format="%.4f",
            key="w1_input_key",
            on_change=lambda: st.session_state.update(
                w1_valor=st.session_state.w1_input_key
            ),
            label_visibility="collapsed",
        )

        # w2 — Impacto del fallo
        st.markdown(
            "<div style='font-size: 0.82rem; color: #6B6B6B; "
            "margin-top: 0.6rem; margin-bottom: 0.1rem; font-weight: 500;'>"
            "Impacto del fallo (w₂)"
            "</div>",
            unsafe_allow_html=True,
        )
        st.number_input(
            "w2",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.w2_valor,
            step=0.05,
            format="%.4f",
            key="w2_input_key",
            on_change=lambda: st.session_state.update(
                w2_valor=st.session_state.w2_input_key
            ),
            label_visibility="collapsed",
        )

        # w3 — Coste de intervención
        st.markdown(
            "<div style='font-size: 0.82rem; color: #6B6B6B; "
            "margin-top: 0.6rem; margin-bottom: 0.1rem; font-weight: 500;'>"
            "Coste de intervención (w₃)"
            "</div>",
            unsafe_allow_html=True,
        )
        st.number_input(
            "w3",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.w3_valor,
            step=0.05,
            format="%.4f",
            key="w3_input_key",
            on_change=lambda: st.session_state.update(
                w3_valor=st.session_state.w3_input_key
            ),
            label_visibility="collapsed",
        )

        # w4 — Tiempo de intervención
        st.markdown(
            "<div style='font-size: 0.82rem; color: #6B6B6B; "
            "margin-top: 0.6rem; margin-bottom: 0.1rem; font-weight: 500;'>"
            "Tiempo de intervención (w₄)"
            "</div>",
            unsafe_allow_html=True,
        )
        st.number_input(
            "w4",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.w4_valor,
            step=0.05,
            format="%.4f",
            key="w4_input_key",
            on_change=lambda: st.session_state.update(
                w4_valor=st.session_state.w4_input_key
            ),
            label_visibility="collapsed",
        )

        # Suma actual de los pesos. Si no es 1, avisamos.
        suma_pesos = (
            st.session_state.w1_valor + st.session_state.w2_valor +
            st.session_state.w3_valor + st.session_state.w4_valor
        )
        if abs(suma_pesos - 1.0) < 0.001:
            color_suma = "#2E7D32"
            mensaje_suma = f"Suma: {suma_pesos:.4f} ✓"
        else:
            color_suma = "#C77B30"
            mensaje_suma = (
                f"Suma: {suma_pesos:.4f} (se normalizará al aplicar)"
            )
        st.markdown(
            f"<div style='font-size: 0.78rem; color: {color_suma}; "
            f"margin-top: 0.8rem; font-style: italic;'>"
            f"{mensaje_suma}"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Boton para volver a los pesos del libro de Saaty
        if st.button("Restablecer pesos AHP", use_container_width=True):
            for k in (
                "w1_input_key", "w2_input_key",
                "w3_input_key", "w4_input_key",
            ):
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state.w1_valor = float(w[0])
            st.session_state.w2_valor = float(w[1])
            st.session_state.w3_valor = float(w[2])
            st.session_state.w4_valor = float(w[3])
            st.session_state.w1_input_key = float(w[0])
            st.session_state.w2_input_key = float(w[1])
            st.session_state.w3_input_key = float(w[2])
            st.session_state.w4_input_key = float(w[3])
            st.rerun()
        
        # Expander de activos criticos forzados (restriccion R3 del modelo)
    with st.expander("Forzar activos críticos", expanded=False):
        st.markdown(
            "<div style='font-size: 0.8rem; color: #6B6B6B; font-style: italic; "
            "margin-bottom: 0.8rem;'>"
            "Activos marcados como obligatorios en el plan. Por defecto, solo "
            "los de impacto máximo (C₂ = 5). Marcar más activos restringe el "
            "modelo: si la suma de sus costes u horas excede los recursos "
            "disponibles, el plan será infactible."
            "</div>",
            unsafe_allow_html=True,
        )

        # Lista de checkboxes en orden de codigo de activo.
        for j in range(len(nombres)):
            etiqueta = f"{nombres[j]} — {descripciones[j]}"
            st.checkbox(
                etiqueta,
                key=f"critico_{j}_valor",
            )

        # Boton para volver al conjunto nominal de criticos (C2 = 5).
        if st.button("Restablecer críticos", use_container_width=True):
            for j in range(len(nombres)):
                key_valor = f"critico_{j}_valor"
                if key_valor in st.session_state:
                    del st.session_state[key_valor]
                st.session_state[key_valor] = (j in J_critico)
            st.rerun()


# Lectura de los parametros activos para usar en el resto del dashboard
B_actual = int(st.session_state.B_valor)
H_actual = int(st.session_state.H_valor)

# Pesos AHP actuales — se normalizan si no suman 1 para garantizar que
import numpy as np
w_actual_raw = np.array([
    st.session_state.w1_valor,
    st.session_state.w2_valor,
    st.session_state.w3_valor,
    st.session_state.w4_valor,
])
suma_w = w_actual_raw.sum()
if suma_w > 0:
    w_actual = w_actual_raw / suma_w
else:
    # Caso degenerado: usuario pone todos los pesos a 0. Volvemos al
    w_actual = w.copy()
    
# Lectura de los activos criticos forzados desde el sidebar. Resultado:
J_critico_actual = [
    j for j in range(len(nombres))
    if st.session_state.get(f"critico_{j}_valor", False)
]

# Reasignacion de las variables globales c y J_critico con los valores
c = R @ w_actual
J_critico = J_critico_actual

# Deteccion del estado del caso: base (parametros nominales del TFG) o
from datos import J_critico as _J_critico_nominal
from datos import w as _w_nominal

pesos_modificados = not np.allclose(w_actual, _w_nominal, atol=1e-4)
criticos_modificados = set(J_critico_actual) != set(_J_critico_nominal)
caso_modificado = pesos_modificados or criticos_modificados


# Cabecera del dashboard
modo_demo_activo = (
    st.query_params.get("demo", "0") == "1"
)

# Etiqueta del estado del caso (verde si base, naranja si modificado)
if caso_modificado:
    etiqueta_color_fondo = "#FCE8D4"
    etiqueta_color_texto = "#9C5210"
    etiqueta_texto = "Caso modificado"
else:
    etiqueta_color_fondo = "#DCEEDC"
    etiqueta_color_texto = "#2E7D32"
    etiqueta_texto = "Caso base"

# Etiqueta de modo demo (solo si esta activo). Se muestra siempre, sea
etiqueta_demo_html = ""
if modo_demo_activo:
    etiqueta_demo_html = (
        "<span style='"
        "display: inline-block;"
        "font-family: Inter, sans-serif;"
        "font-size: 0.78rem;"
        "font-weight: 600;"
        "text-transform: uppercase;"
        "letter-spacing: 0.5px;"
        "color: #0891B2;"
        "background-color: #CFF4FB;"
        "padding: 0.35rem 0.8rem;"
        "border-radius: 999px;"
        "white-space: nowrap;"
        "transform: translateY(-0.3rem);"
        "'>Modo demo</span>"
    )

st.markdown(
    f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 1.2rem;
        flex-wrap: nowrap;
        margin-bottom: 0.4rem;
    ">
        <h1 style="
            margin: 0;
            font-family: 'Fraunces', Georgia, 'Times New Roman', serif;
            font-weight: 700;
            font-size: 2.8rem;
            line-height: 1.1;
            color: #1A1A1A;
            letter-spacing: -0.01em;
        ">Priorización del mantenimiento preventivo</h1>
        <span style="
            display: inline-block;
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: {etiqueta_color_texto};
            background-color: {etiqueta_color_fondo};
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            white-space: nowrap;
            transform: translateY(-0.3rem);
        ">{etiqueta_texto}</span>
        {etiqueta_demo_html}
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='subtitulo'>"
    "Combinación del método AHP de Saaty con programación entera binaria "
    "sobre una red de distribución MT/BT de 20 activos."
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("<hr/>", unsafe_allow_html=True)

# Bloque de trazabilidad
FECHA_ACTUALIZACION_INVENTARIO = date(2026, 5, 19)
NOMBRE_CONFIGURACION = "Red de distribución MT/BT — Caso TFG"

# Modo demo

# Inicializacion del estado del selector (solo si el modo demo esta activo)
if modo_demo_activo and "fecha_demo_opcion" not in st.session_state:
    st.session_state.fecha_demo_opcion = "Fecha real (RECIENTE)"

# Selector de fecha simulada en el sidebar
if modo_demo_activo:
    with st.sidebar:
        st.markdown(
            "<div style='margin-top: 2rem; font-family: Inter, sans-serif; "
            "font-size: 0.78rem; font-weight: 600; letter-spacing: 0.5px; "
            "text-transform: uppercase; color: #0891B2;'>"
            "Modo demo"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-size: 0.78rem; color: #6B6B6B; font-style: italic; "
            "margin-top: 0.3rem; margin-bottom: 0.6rem;'>"
            "Simula distintas antigüedades del inventario para ilustrar el "
            "aviso de frescura. Activo porque la URL incluye <code>?demo=1</code>."
            "</div>",
            unsafe_allow_html=True,
        )
        st.selectbox(
            "Fecha simulada del inventario",
            options=[
                "Fecha real (RECIENTE)",
                "Hace 7 meses (A REVISAR)",
                "Hace 10 meses (PRÓXIMO A CADUCAR)",
                "Hace 13 meses (CADUCADO)",
            ],
            key="fecha_demo_opcion",
            label_visibility="collapsed",
        )

# Resolucion de la fecha efectiva del inventario
if modo_demo_activo:
    opcion = st.session_state.fecha_demo_opcion
    if opcion == "Hace 7 meses (A REVISAR)":
        fecha_inventario_efectiva = date.today() - timedelta(days=7 * 30)
    elif opcion == "Hace 10 meses (PRÓXIMO A CADUCAR)":
        fecha_inventario_efectiva = date.today() - timedelta(days=10 * 30)
    elif opcion == "Hace 13 meses (CADUCADO)":
        fecha_inventario_efectiva = date.today() - timedelta(days=13 * 30)
    else:
        fecha_inventario_efectiva = FECHA_ACTUALIZACION_INVENTARIO
else:
    fecha_inventario_efectiva = FECHA_ACTUALIZACION_INVENTARIO

# Estado de frescura del inventario
dias_inventario = (date.today() - fecha_inventario_efectiva).days

if dias_inventario < 6 * 30:
    estado_inv_etiqueta = "RECIENTE"
    estado_inv_explicacion = "El plan tiene menos de 6 meses, los datos son fiables."
    estado_inv_color_texto = "#2E7D32"
    estado_inv_color_fondo = "#DCEEDC"
elif dias_inventario < 9 * 30:
    estado_inv_etiqueta = "A REVISAR"
    estado_inv_explicacion = "El plan tiene entre 6 y 9 meses, conviene actualizar el inventario."
    estado_inv_color_texto = "#8A6D00"
    estado_inv_color_fondo = "#FAEFC4"
elif dias_inventario < 12 * 30:
    estado_inv_etiqueta = "PRÓXIMO A CADUCAR"
    estado_inv_explicacion = "El plan tiene más de 9 meses, debería renovarse pronto."
    estado_inv_color_texto = "#9C5210"
    estado_inv_color_fondo = "#FCE8D4"
else:
    estado_inv_etiqueta = "CADUCADO"
    estado_inv_explicacion = "El plan ha superado el año, hay que recalcularlo con datos actualizados."
    estado_inv_color_texto = "#B71C1C"
    estado_inv_color_fondo = "#F8D7D7"

# Texto en castellano para la fecha del inventario (objeto date convertido
_meses_es = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
fecha_inventario_texto = (
    f"{fecha_inventario_efectiva.day} de "
    f"{_meses_es[fecha_inventario_efectiva.month - 1]} de "
    f"{fecha_inventario_efectiva.year}"
)

ahora = datetime.now()
fecha_calculo_texto = ahora.strftime("%d/%m/%Y a las %H:%M")

st.markdown(
    f"""
    <div style="
        display: flex;
        gap: 2.5rem;
        flex-wrap: wrap;
        margin: 0 0 1.8rem 0;
        padding: 0.9rem 1.1rem;
        background-color: #F5F2EB;
        border-left: 3px solid #003F72;
        border-radius: 2px;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
    ">
        <div>
            <div style="
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.7rem;
                color: #6B6B6B;
                font-weight: 600;
                margin-bottom: 0.2rem;
            ">Red Analizada</div>
            <div style="color: #1A1A1A; font-weight: 500;">
                {NOMBRE_CONFIGURACION}
            </div>
        </div>
        <div>
            <div style="
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.7rem;
                color: #6B6B6B;
                font-weight: 600;
                margin-bottom: 0.2rem;
            ">Plan calculado el</div>
            <div style="color: #1A1A1A; font-weight: 500;">
                {fecha_calculo_texto}
            </div>
        </div>
        <div>
            <div style="
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.7rem;
                color: #6B6B6B;
                font-weight: 600;
                margin-bottom: 0.2rem;
            ">Inventario actualizado el</div>
            <div style="color: #1A1A1A; font-weight: 500;">
                {fecha_inventario_texto}
            </div>
        </div>
        <div>
            <div style="
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 0.7rem;
                color: #6B6B6B;
                font-weight: 600;
                margin-bottom: 0.2rem;
            ">Estado del inventario</div>
            <div style="
                color: {estado_inv_color_texto};
                background-color: {estado_inv_color_fondo};
                font-weight: 700;
                font-size: 0.85rem;
                letter-spacing: 0.3px;
                padding: 0.15rem 0.6rem;
                border-radius: 999px;
                display: inline-block;
                margin-bottom: 0.25rem;
            ">{estado_inv_etiqueta}</div>
            <div style="
                color: #6B6B6B;
                font-size: 0.75rem;
                font-style: italic;
                max-width: 280px;
                line-height: 1.4;
            ">{estado_inv_explicacion}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Resolucion del modelo con los parametros activos
@st.cache_data(show_spinner=False)
def resolver_con_parametros(B, H, pesos_tupla, criticos_tupla):
    """
    Construye y resuelve el modelo PuLP con los parametros actuales y
    ademas calcula la solucion greedy para poder mostrar la mejora.

    Parametros:
        B             : presupuesto disponible (euros)
        H             : horas-hombre disponibles
        pesos_tupla   : tupla de 4 floats con los pesos AHP (w1..w4)
        criticos_tupla: tupla con los indices de los activos forzados

    Devuelve un diccionario con todos los resultados.
    """
    # Reconstruccion del vector de coeficientes c con los pesos actuales.
    import numpy as np
    w_actual = np.array(pesos_tupla)
    c_actual = R @ w_actual

    # Lista de criticos forzados (lista, no tupla, para el solver).
    J_crit_actual = list(criticos_tupla)

    modelo, x = construir_modelo(
        c_actual, a, b, B, H, J_crit_actual, nombres
    )
    resultado = resolver_modelo(modelo, x, c_actual, a, b, nombres)

    # Adjuntamos el vector c usado para que el resto del dashboard
    resultado["c_actual"] = c_actual

    # Solucion greedy con los mismos parametros, para calcular la mejora
    _, _, _, z_greedy = heuristica_greedy_dual(
        c_actual, a, b, B, H, J_crit_actual, criterio="coste"
    )
    resultado["z_greedy"] = z_greedy

    return resultado


# Funcion auxiliar: grafica de prioridad por activo
def construir_grafica_prioridades(seleccionados):
    """
    Recibe la lista de indices de activos en el plan optimo y devuelve la
    figura Plotly con las 20 barras horizontales.
    """
    # Indices ordenados por prioridad ascendente (Plotly dibuja de abajo
    orden = sorted(range(len(c)), key=lambda j: c[j])

    nombres_ord = [nombres[j] for j in orden]
    prioridades_ord = [c[j] * 100 for j in orden]
    costes_ord = [a[j] for j in orden]
    horas_ord = [b[j] for j in orden]

    # Color de cada barra: azul UFV si esta seleccionado, gris claro si no
    colores_barras = [
        COLORES["azul_ufv"] if j in seleccionados else "#D8D4CB"
        for j in orden
    ]

    # Patron de relleno para cada barra: rayado diagonal solo en los criticos
    patrones = [
        "/" if j in J_critico else ""
        for j in orden
    ]

    # Texto que aparece al hacer hover sobre cada barra
    hovertext = [
        f"<b>{descripciones[j]}</b> <span style='color:#6B6B6B; font-weight:400;'>({nombres[j]})</span><br>"
        f"Prioridad: {es_decimal(c[j]*100, 2)} %<br>"
        f"Coste: {es_miles(a[j])} €<br>"
        f"Tiempo: {es_decimal(b[j], 1)} h<br>"
        f"{'<b style=\"color:#5BB47C\">Incluido en el plan</b>' if j in seleccionados else '<i>No incluido</i>'}"
        for j in orden
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=prioridades_ord,
                y=nombres_ord,
                orientation="h",
                marker=dict(
                    color=colores_barras,
                    line=dict(width=0),
                    pattern=dict(
                        shape=patrones,
                        fgcolor="#001F3D",
                        size=6,
                        solidity=0.35,
                    ),
                ),
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hovertext,
            )
        ]
    )

    fig.update_layout(
        height=560,
        margin=dict(l=10, r=20, t=20, b=40),
        plot_bgcolor=COLORES["fondo"],
        paper_bgcolor=COLORES["fondo"],
        font=dict(
            family="Inter, sans-serif",
            size=13,
            color=COLORES["texto_oscuro"],
        ),
        xaxis=dict(
            title=dict(
                text="Prioridad AHP del activo (%)",
                font=dict(size=12, color=COLORES["texto_medio"]),
            ),
            range=[0, 100],
            tickmode="array",
            tickvals=[0, 20, 40, 60, 80, 100],
            ticktext=["0 %", "20 %", "40 %", "60 %", "80 %", "100 %"],
            showgrid=True,
            gridcolor=COLORES["separador"],
            gridwidth=1,
            zeroline=False,
            tickfont=dict(size=11, color=COLORES["texto_medio"]),
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=12, color=COLORES["texto_oscuro"]),
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor=COLORES["separador"],
            font=dict(
                family="Inter, sans-serif",
                size=12,
                color=COLORES["texto_oscuro"],
            ),
            align="left",
        ),
        showlegend=False,
    )

    return fig

def construir_grafica_saturacion(gasto, B, horas, H):
    """
    Pinta dos barras horizontales con la saturacion de las restricciones:
    presupuesto y tiempo. El color cambia segun lo cerca que este del techo.
    Sirve para que el usuario detecte de un vistazo si esta apretando mucho
    una restriccion y le sobra la otra.
    """
    pct_b = (100 * gasto / B) if B > 0 else 0.0
    pct_h = (100 * horas / H) if H > 0 else 0.0

    def color_por_saturacion(pct):
        if pct >= 95:
            return "#B5533B"
        elif pct >= 80:
            return "#E8A33D"
        else:
            return "#5BB47C"

    color_b = color_por_saturacion(pct_b)
    color_h = color_por_saturacion(pct_h)

    fig = go.Figure()

    # Barra de fondo (gris claro hasta 100) para las dos restricciones
    fig.add_trace(
        go.Bar(
            x=[100, 100],
            y=["Tiempo de intervención", "Presupuesto"],
            orientation="h",
            marker=dict(color="#E5E1D8", line=dict(width=0)),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Barra de relleno con la saturacion real (encima de la barra de fondo)
    fig.add_trace(
        go.Bar(
            x=[pct_h, pct_b],
            y=["Tiempo de intervención", "Presupuesto"],
            orientation="h",
            marker=dict(
                color=[color_h, color_b],
                line=dict(width=0),
            ),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Saturación: %{x:.1f} %<extra></extra>"
            ),
            showlegend=False,
        )
    )

    fig.update_layout(
        barmode="overlay",
        height=180,
        margin=dict(l=10, r=10, t=10, b=30),
        paper_bgcolor="#FAF8F5",
        plot_bgcolor="#FAF8F5",
        font=dict(family="Inter, sans-serif", size=12, color="#1A1A1A"),
        xaxis=dict(
            range=[0, 105],
            tickmode="array",
            tickvals=[0, 20, 40, 60, 80, 100],
            ticktext=["0 %", "20 %", "40 %", "60 %", "80 %", "100 %"],
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=11, color="#6B6B6B"),
        ),
        yaxis=dict(
            tickfont=dict(size=12, color="#1A1A1A"),
            automargin=True,
        ),
    )

    # Linea vertical en el 100 % para marcar el techo de la restriccion
    fig.add_shape(
        type="line",
        x0=100, x1=100,
        y0=-0.5, y1=1.5,
        line=dict(color="#1A1A1A", width=1.5, dash="dot"),
    )

    return fig

def construir_grafica_por_familia(seleccionados):
    """
    Barras horizontales apiladas con el reparto del plan optimo por familia
    de activo. Cada barra tiene dos segmentos: activos incluidos (azul UFV)
    y activos no incluidos (gris claro). Ayuda a ver si el plan ataca todas
    las familias o se concentra en algunas.
    """
    # Asignacion fija de cada activo a su familia. El orden de los indices
    familias = {
        "Transformadores": [0, 1, 2, 3],
        "Líneas MT":       [4, 5, 6, 7, 8],
        "Aparamenta MT":   [9, 10, 11, 12, 13],
        "Fusibles BT":     [14, 15, 16, 17],
        "Líneas BT":       [18, 19],
    }

    set_seleccionados = set(seleccionados)

    nombres_familia = []
    incluidos = []
    no_incluidos = []
    totales = []
    for familia, indices in familias.items():
        n_incl = sum(1 for j in indices if j in set_seleccionados)
        n_total = len(indices)
        n_no = n_total - n_incl
        nombres_familia.append(familia)
        incluidos.append(n_incl)
        no_incluidos.append(n_no)
        totales.append(n_total)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=nombres_familia,
            x=incluidos,
            orientation="h",
            name="En el plan",
            marker=dict(color="#003F72", line=dict(width=0)),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "En el plan: %{x}<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Bar(
            y=nombres_familia,
            x=no_incluidos,
            orientation="h",
            name="Fuera del plan",
            marker=dict(color="#D8D4CB", line=dict(width=0)),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Fuera del plan: %{x}<extra></extra>"
            ),
        )
    )

    # Etiquetas al final de cada barra con el conteo "incluidos / total"
    etiquetas = [
        f"{n_in} / {n_tot}"
        for n_in, n_tot in zip(incluidos, totales)
    ]
    fig.update_traces(
        selector=dict(name="Fuera del plan"),
        text=etiquetas,
        textposition="outside",
        textfont=dict(family="Inter, sans-serif", size=11, color="#1A1A1A"),
        cliponaxis=False,
    )

    fig.update_layout(
        barmode="stack",
        height=280,
        margin=dict(l=10, r=60, t=10, b=30),
        paper_bgcolor="#FAF8F5",
        plot_bgcolor="#FAF8F5",
        font=dict(family="Inter, sans-serif", size=12, color="#1A1A1A"),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, max(totales) + 1],
        ),
        yaxis=dict(
            tickfont=dict(size=12, color="#1A1A1A"),
            automargin=True,
            categoryorder="array",
            categoryarray=list(reversed(nombres_familia)),
        ),
        showlegend=False,
    )

    return fig

# Resolvemos para los valores actuales del slider
with st.spinner("Resolviendo el modelo..."):
    resultado = resolver_con_parametros(
        B_actual, H_actual,
        tuple(w_actual), tuple(J_critico_actual),
    )

# Visualizacion provisional del resultado (sera reemplazada en 6.D por
st.subheader("Resultado del modelo")

# Si el modelo no encontro solucion factible, lo avisamos de forma informativa
if resultado["estado"] != "Optimal":

    # Calculamos los minimos exactos para volver a factibilidad
    coste_minimo = sum(a[j] for j in J_critico)
    horas_minimas = sum(b[j] for j in J_critico)

    explicacion_b = ""
    explicacion_h = ""
    if B_actual < coste_minimo:
        explicacion_b = (
            f"El presupuesto actual ({es_miles(B_actual)} €) no llega a cubrir el "
            f"coste de los activos críticos forzados, que asciende a "
            f"<strong>{es_miles(coste_minimo)} €</strong>."
        )
    if H_actual < horas_minimas:
        explicacion_h = (
            f"Las horas-hombre actuales ({H_actual} h) no llegan a cubrir el "
            f"tiempo necesario para los activos críticos forzados, que "
            f"asciende a <strong>{es_decimal(horas_minimas, 1)} h</strong>."
        )

    cuerpo = ""
    if explicacion_b:
        cuerpo += f"<p style='margin: 0 0 0.6rem 0;'>{explicacion_b}</p>"
    if explicacion_h:
        cuerpo += f"<p style='margin: 0 0 0.6rem 0;'>{explicacion_h}</p>"
    if not cuerpo:
        cuerpo = (
            "<p style='margin: 0 0 0.6rem 0;'>"
            "Con los parámetros actuales no existe una combinación de activos "
            "que respete a la vez R1, R2 y R3."
            "</p>"
        )

    st.markdown(
            f"""
            <div style="
                background-color: #FBF1EE;
                border-left: 3px solid #B5533B;
                padding: 1.1rem 1.4rem;
                margin: 1.5rem 0 0.5rem 0;
                border-radius: 2px;
                font-family: 'Inter', sans-serif;
                color: {COLORES['texto_oscuro']};
                font-size: 0.92rem;
                line-height: 1.55;
            ">
                <div style="display: flex; align-items: flex-start; gap: 0.7rem;">
                    <span style="
                        display: inline-block;
                        width: 9px;
                        height: 9px;
                        background-color: #B5533B;
                        border-radius: 50%;
                        margin-top: 0.45rem;
                        flex-shrink: 0;
                    "></span>
                    <div style="flex: 1;">
                        <div style="
                            font-family: 'Fraunces', serif;
                            font-size: 1.05rem;
                            font-weight: 600;
                            color: #8A3A24;
                            margin-bottom: 0.6rem;
                        ">
                            Modelo sin solución factible
                        </div>
                        {cuerpo}
                        <p style="margin: 0.6rem 0 0 0; color: {COLORES['texto_medio']};">
                            Ajusta el presupuesto o las horas en el panel izquierdo
                            para volver a obtener un plan.
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    # Modelo resuelto correctamente: cinco tarjetas KPI premium + aviso verde
    plan_nombres = [nombres[j] for j in resultado["seleccionados"]]

    pct_b = (100 * resultado["gasto"] / B_actual) if B_actual > 0 else 0.0
    pct_h = (100 * resultado["horas"] / H_actual) if H_actual > 0 else 0.0

    prioridad_total = sum(c)
    cobertura_pct = (100 * resultado["z_optimo"] / prioridad_total) if prioridad_total > 0 else 0.0

    z_opt = resultado["z_optimo"]
    z_greedy = resultado["z_greedy"]
    if z_greedy > 0:
        mejora_pct = 100 * (z_opt - z_greedy) / z_greedy
    else:
        mejora_pct = 0.0

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-tarjeta kpi-tarjeta-simple">
                <div class="kpi-etiqueta">Cobertura del plan</div>
                <div class="kpi-numero-centrado">
                    <div class="kpi-numero">
                        {cobertura_pct:.1f}<span class="kpi-unidad">%</span>
                    </div>
                </div>
                <div class="kpi-barra-fondo">
                    <div class="kpi-barra-relleno" style="width: {min(cobertura_pct, 100):.1f}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-tarjeta kpi-tarjeta-simple">
                <div class="kpi-etiqueta">Activos en el plan</div>
                <div class="kpi-numero-centrado">
                    <div class="kpi-numero">
                        {len(plan_nombres)}<span class="kpi-unidad">/ {len(nombres)}</span>
                    </div>
                </div>
                <div class="kpi-barra-fondo">
                    <div class="kpi-barra-relleno" style="width: {100 * len(plan_nombres) / len(nombres):.1f}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    with col3:
        st.markdown(
            f"""
            <div class="kpi-tarjeta">
                <div class="kpi-etiqueta">Presupuesto utilizado</div>
                <div class="kpi-numero">
                    {pct_b:.1f}<span class="kpi-unidad">%</span>
                </div>
                <div class="kpi-barra-fondo">
                    <div class="kpi-barra-relleno" style="width: {min(pct_b, 100):.1f}%;"></div>
                </div>
                <div class="kpi-contexto">
                    {es_miles(resultado['gasto'])} € de {es_miles(B_actual)} €
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-tarjeta">
                <div class="kpi-etiqueta">Tiempo de intervención</div>
                <div class="kpi-numero">
                    {pct_h:.1f}<span class="kpi-unidad">%</span>
                </div>
                <div class="kpi-barra-fondo">
                    <div class="kpi-barra-relleno" style="width: {min(pct_h, 100):.1f}%;"></div>
                </div>
                <div class="kpi-contexto">
                    {es_decimal(resultado['horas'], 1)} h de {H_actual} h
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        # Cuando la ganancia es positiva: tarjeta verde menta.
        if mejora_pct > 0:
            clase_tarjeta = "kpi-tarjeta kpi-tarjeta-verde"
            signo = "+"
        else:
            clase_tarjeta = "kpi-tarjeta kpi-tarjeta-neutra"
            signo = ""

        st.markdown(
            f"""
            <div class="{clase_tarjeta}">
                <div class="kpi-etiqueta">Ganancia frente al método simple</div>
                <div class="kpi-numero">
                    {signo}{mejora_pct:.2f}<span class="kpi-unidad">%</span>
                </div>
                <div class="kpi-contexto">
                    Cobertura adicional respecto a intervenir los activos por
                    orden de importancia sin más cálculo.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Aviso verde con mensaje informativo
    st.markdown(
        f"""
        <div style="
            background-color: #F0F5EF;
            border-left: 3px solid #5C7A4A;
            padding: 1rem 1.4rem;
            margin: 1.5rem 0 0.5rem 0;
            border-radius: 2px;
            font-family: 'Inter', sans-serif;
            color: {COLORES['texto_oscuro']};
            font-size: 0.92rem;
            line-height: 1.55;
        ">
            <div style="
                display: flex;
                align-items: flex-start;
                gap: 0.7rem;
            ">
                <span style="
                    display: inline-block;
                    width: 9px;
                    height: 9px;
                    background-color: #5C7A4A;
                    border-radius: 50%;
                    margin-top: 0.45rem;
                    flex-shrink: 0;
                "></span>
                <div>
                    <span style="
                        font-family: 'Fraunces', serif;
                        font-size: 1.05rem;
                        font-weight: 600;
                        color: #3D5A2F;
                    ">
                        Esta es la mejor combinación posible
                    </span>
                    <span style="color: {COLORES['texto_medio']};">
                        de activos con los recursos que has fijado.
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Grafica principal: prioridad por activo, con seleccionados destacados
    st.markdown(
            """
            <div style="margin-top: 2.5rem; margin-bottom: 0.5rem;">
                <h2 style="
                    font-family: 'Fraunces', serif;
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: #1A1A1A;
                    margin-bottom: 0;
                ">
                    Ranking de activos por prioridad
                </h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

    fig_prioridades = construir_grafica_prioridades(resultado["seleccionados"])
    st.plotly_chart(fig_prioridades, use_container_width=True)
    
    # Leyenda explicativa de la grafica de prioridades
    st.markdown(
        """
        <div style="
            display: flex;
            gap: 2.2rem;
            align-items: center;
            margin-top: 0.4rem;
            margin-bottom: 1.5rem;
            padding-left: 0.2rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            color: #1A1A1A;
            flex-wrap: wrap;
        ">
            <div style="display: flex; align-items: center; gap: 0.55rem;">
                <span style="
                    display: inline-block;
                    width: 22px;
                    height: 12px;
                    background-color: #003F72;
                    border-radius: 2px;
                "></span>
                Incluido en el plan óptimo
            </div>
            <div style="display: flex; align-items: center; gap: 0.55rem;">
               <span style="
                    display: inline-block;
                    width: 22px;
                    height: 12px;
                    background-color: #003F72;
                    background-image: repeating-linear-gradient(
                        45deg,
                        #003F72 0px,
                        #003F72 3px,
                        #FFFFFF 3px,
                        #FFFFFF 4px
                    );
                    border-radius: 2px;
                "></span>
                Activo crítico forzado
            </div>
            <div style="display: flex; align-items: center; gap: 0.55rem;">
                <span style="
                    display: inline-block;
                    width: 22px;
                    height: 12px;
                    background-color: #D8D4CB;
                    border-radius: 2px;
                "></span>
                No incluido
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Saturacion de restricciones
    st.markdown(
        """
        <div style="margin-top: 2.5rem; margin-bottom: 0.3rem;">
            <h2 style="
                font-family: 'Fraunces', serif;
                font-size: 1.5rem;
                font-weight: 600;
                color: #1A1A1A;
                margin-bottom: 0.3rem;
            ">
                Consumo de los recursos disponibles
            </h2>
            <p style="
                font-family: 'Inter', sans-serif;
                font-size: 0.92rem;
                color: #6B6B6B;
                margin: 0 0 0.8rem 0;
            ">
                Cuánto del presupuesto y del tiempo disponibles consume el plan
                óptimo. La línea punteada marca el límite (100 %).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig_saturacion = construir_grafica_saturacion(
        gasto=resultado["gasto"],
        B=B_actual,
        horas=resultado["horas"],
        H=H_actual,
    )
    st.plotly_chart(fig_saturacion, use_container_width=True)

    pct_b_val = (100 * resultado["gasto"] / B_actual) if B_actual > 0 else 0.0
    pct_h_val = (100 * resultado["horas"] / H_actual) if H_actual > 0 else 0.0

    st.markdown(
        f"""
        <div style="
            display: flex;
            gap: 2.5rem;
            margin: 0.2rem 0 1.5rem 0;
            padding-left: 0.2rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            color: #6B6B6B;
        ">
            <div>
                <strong style="color: #1A1A1A;">Presupuesto:</strong>
                {es_miles(resultado['gasto'])} € de {es_miles(B_actual)} €
                ({es_decimal(pct_b_val, 1)} %)
            </div>
            <div>
                <strong style="color: #1A1A1A;">Tiempo:</strong>
                {es_decimal(resultado['horas'], 1)} h de {H_actual} h
                ({es_decimal(pct_h_val, 1)} %)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Plan por familia
    st.markdown(
        """
        <div style="margin-top: 2.5rem; margin-bottom: 0.3rem;">
            <h2 style="
                font-family: 'Fraunces', serif;
                font-size: 1.5rem;
                font-weight: 600;
                color: #1A1A1A;
                margin-bottom: 0.3rem;
            ">
                Plan por familia de activo
            </h2>
            <p style="
                font-family: 'Inter', sans-serif;
                font-size: 0.92rem;
                color: #6B6B6B;
                margin: 0 0 0.8rem 0;
            ">
                Cuántos activos de cada familia entran en el plan y cuántos
                quedan fuera. El número a la derecha indica activos incluidos
                sobre el total.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig_familia = construir_grafica_por_familia(resultado["seleccionados"])
    st.plotly_chart(fig_familia, use_container_width=True)

    # Leyenda corta debajo de la gráfica
    st.markdown(
        """
        <div style="
            display: flex;
            gap: 2.2rem;
            align-items: center;
            margin-top: 0.2rem;
            margin-bottom: 1.5rem;
            padding-left: 0.2rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            color: #1A1A1A;
            flex-wrap: wrap;
        ">
            <div style="display: flex; align-items: center; gap: 0.55rem;">
                <span style="
                    display: inline-block;
                    width: 22px;
                    height: 12px;
                    background-color: #003F72;
                    border-radius: 2px;
                "></span>
                En el plan
            </div>
            <div style="display: flex; align-items: center; gap: 0.55rem;">
                <span style="
                    display: inline-block;
                    width: 22px;
                    height: 12px;
                    background-color: #D8D4CB;
                    border-radius: 2px;
                "></span>
                Fuera del plan
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Plan detallado
    st.markdown(
        """
        <div style="margin-top: 2.5rem; margin-bottom: 0.3rem;">
            <h2 style="
                font-family: 'Fraunces', serif;
                font-size: 1.5rem;
                font-weight: 600;
                color: #1A1A1A;
                margin-bottom: 0.3rem;
            ">
                Plan óptimo
            </h2>
            <p style="
                font-family: 'Inter', sans-serif;
                font-size: 0.92rem;
                color: #6B6B6B;
                margin: 0 0 0.8rem 0;
            ">
                Activos seleccionados, ordenados de mayor a menor prioridad.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    plan_ordenado = sorted(
        resultado["seleccionados"],
        key=lambda j: c[j],
        reverse=True,
    )

    # Construccion de las filas HTML de la tabla del plan
    filas_plan_html = []
    for orden, j in enumerate(plan_ordenado, start=1):
        fila = (
            f'<tr>'
            f'<td class="num">{orden}</td>'
            f'<td class="codigo">{nombres[j]}</td>'
            f'<td class="descripcion">{descripciones[j]}</td>'
            f'<td class="tipo">{tipos[j]}</td>'
            f'<td class="num">{es_decimal(c[j]*100, 2)} %</td>'
            f'<td class="num">{es_miles(a[j])} €</td>'
            f'<td class="num">{es_decimal(b[j], 1)}</td>'
            f'</tr>'
        )
        filas_plan_html.append(fila)

    tabla_plan_html = (
        '<table class="tabla-plan">'
        '<thead>'
        '<tr>'
        '<th class="num">#</th>'
        '<th>Código</th>'
        '<th>Descripción</th>'
        '<th>Tipo</th>'
        '<th class="num">Prioridad</th>'
        '<th class="num">Coste</th>'
        '<th class="num">Tiempo (h)</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        f'{"".join(filas_plan_html)}'
        '</tbody>'
        '</table>'
    )

    # Estilos especificos de la tabla del plan
    st.markdown(
        """
        <style>
        .tabla-plan {
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            color: #1A1A1A;
            border-collapse: collapse;
            width: 100%;
            margin: 0 0 1.5rem 0;
        }
        .tabla-plan thead th {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #003F72;
            text-align: left;
            padding: 0.85rem 0.9rem;
            border-bottom: 2px solid #003F72;
            background-color: transparent;
            white-space: nowrap;
        }
        .tabla-plan thead th.num {
            text-align: right;
        }
        .tabla-plan tbody td {
            padding: 0.7rem 0.9rem;
            border-bottom: 1px solid #E5E1D8;
            vertical-align: middle;
        }
        .tabla-plan tbody tr:nth-child(even) {
            background-color: #F5F2EB;
        }
        .tabla-plan tbody tr:hover {
            background-color: #EAE6DC;
        }
        .tabla-plan td.codigo {
            font-weight: 600;
            color: #003F72;
            font-variant-numeric: tabular-nums;
        }
        .tabla-plan td.descripcion {
            font-weight: 500;
        }
        .tabla-plan td.tipo {
            color: #6B6B6B;
        }
        .tabla-plan td.num {
            text-align: right;
            font-variant-numeric: tabular-nums;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(tabla_plan_html, unsafe_allow_html=True)

    # Botones de descarga: CSV y Excel
    df_plan = pd.DataFrame(
        {
            "Orden": list(range(1, len(plan_ordenado) + 1)),
            "Codigo": [nombres[j] for j in plan_ordenado],
            "Descripcion": [descripciones[j] for j in plan_ordenado],
            "Tipo": [tipos[j] for j in plan_ordenado],
            "Prioridad (%)": [round(c[j] * 100, 2) for j in plan_ordenado],
            "Coste (EUR)": [int(a[j]) for j in plan_ordenado],
            "Tiempo (h)": [float(b[j]) for j in plan_ordenado],
        }
    )

    # CSV con coma como separador decimal y punto y coma como separador
    csv_bytes = df_plan.to_csv(
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    ).encode("utf-8-sig")

    # Excel: misma data, una sola hoja.
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_plan.to_excel(writer, sheet_name="Plan optimo", index=False)
    excel_bytes = excel_buffer.getvalue()

    col_descarga_1, col_descarga_2, _ = st.columns([1, 1, 4])
    with col_descarga_1:
        st.download_button(
            label="Descargar CSV",
            data=csv_bytes,
            file_name="plan_optimo.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_descarga_2:
        st.download_button(
            label="Descargar Excel",
            data=excel_bytes,
            file_name="plan_optimo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        
# Pie del dashboard
st.markdown(
    """
    <div style="
        margin-top: 4rem;
        padding-top: 1.5rem;
        border-top: 1px solid #E5E1D8;
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: #6B6B6B;
        line-height: 1.7;
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            gap: 2rem;
            flex-wrap: wrap;
        ">
            <div style="flex: 1; min-width: 280px;">
                <div style="
                    font-weight: 600;
                    color: #003F72;
                    font-size: 0.72rem;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                    margin-bottom: 0.5rem;
                ">
                    Información técnica
                </div>
                <div>
                    <strong style="color: #1A1A1A;">Motor de optimización:</strong>
                    PuLP + CBC
                </div>
                <div>
                    <strong style="color: #1A1A1A;">Método:</strong>
                    AHP + Programación entera 0-1
                </div>
                <div>
                    <strong style="color: #1A1A1A;">Versión del modelo:</strong>
                    1.0 — junio 2026
                </div>
            </div>
            <div style="flex: 1; min-width: 280px; text-align: right;">
                <div style="
                    font-weight: 600;
                    color: #003F72;
                    font-size: 0.72rem;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                    margin-bottom: 0.5rem;
                ">
                    Proyecto
                </div>
                <div style="color: #1A1A1A; font-weight: 500;">
                    Carla Esono Ballesteros
                </div>
                <div>
                    Trabajo Fin de Grado · UFV · Junio 2026
                </div>
                <div>
                    Tutor: Joaquín Hidalgo Trucios
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)