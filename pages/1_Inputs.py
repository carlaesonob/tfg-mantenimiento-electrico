"""Pagina de inputs: inventario de los 20 activos (datos fisicos + criterios AHP). Lee de datos.py; solo consulta."""

import streamlit as st
from datos import (
    nombres,
    descripciones,
    tipos,
    caracteristicas,
    edades,
    prob_fallo_bruta,
    C2,
    a,
    b,
)

st.set_page_config(
    page_title="Inputs del modelo",
    page_icon="📋",
    layout="wide",
)

# Paleta y tipografias (consistente con la pagina principal)
COLORES = {
    "azul_ufv": "#003F72",
    "azul_ufv_oscuro": "#001F3D",
    "fondo_principal": "#FAF8F5",
    "fondo_sidebar": "#F0EDE6",
    "texto_oscuro": "#1A1A1A",
    "texto_medio": "#6B6B6B",
    "separador": "#E5E1D8",
    "fila_alterna": "#F5F2EB",
    "hover": "#EAE6DC",
}

# Formateo de numeros en castellano
def es_miles(n):
    return f"{int(round(n)):,}".replace(",", ".")

def es_decimal(n, decimales=2):
    formateado = f"{n:,.{decimales}f}"
    return formateado.replace(",", "§").replace(".", ",").replace("§", ".")

# Estilos CSS
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {{
        background-color: {COLORES['fondo_principal']};
    }}
[data-testid="stSidebar"] {{
        background-color: {COLORES['fondo_sidebar']} !important;
    }}
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    [data-testid="stHeader"] button[kind="header"],
    [data-testid="stHeader"] button[kind="headerNoPadding"],
    [data-testid="stHeader"] button[kind="header"] *,
    [data-testid="stHeader"] button[kind="headerNoPadding"] * {{
        font-family: 'Fraunces', serif !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em !important;
        color: {COLORES['texto_oscuro']} !important;
        text-transform: uppercase !important;
    }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    .inputs-cabecera {{
        margin-top: 0.5rem;
        margin-bottom: 2rem;
    }}
    .inputs-titulo {{
        font-family: 'Fraunces', serif;
        font-size: 2.2rem;
        font-weight: 600;
        color: {COLORES['texto_oscuro']};
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.5px;
    }}
    .inputs-subtitulo {{
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: {COLORES['texto_medio']};
        margin: 0;
    }}
    .inputs-separador {{
        height: 1px;
        background-color: {COLORES['separador']};
        margin: 1.2rem 0 2rem 0;
    }}
    .tabla-inputs {{
        font-family: 'Inter', sans-serif;
        font-size: 0.88rem;
        color: {COLORES['texto_oscuro']};
        border-collapse: collapse;
        width: 100%;
        margin: 0 0 1.5rem 0;
    }}
    .tabla-inputs thead th {{
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: {COLORES['azul_ufv']};
        text-align: left;
        padding: 0.85rem 0.9rem;
        border-bottom: 2px solid {COLORES['azul_ufv']};
        background-color: transparent;
        white-space: nowrap;
    }}
    .tabla-inputs thead th.num {{
        text-align: right;
    }}
    .tabla-inputs tbody td {{
        padding: 0.7rem 0.9rem;
        border-bottom: 1px solid {COLORES['separador']};
        vertical-align: middle;
    }}
    .tabla-inputs tbody tr:nth-child(even) {{
        background-color: {COLORES['fila_alterna']};
    }}
    .tabla-inputs tbody tr:hover {{
        background-color: {COLORES['hover']};
    }}
    .tabla-inputs td.codigo {{
        font-weight: 600;
        color: {COLORES['azul_ufv']};
        font-variant-numeric: tabular-nums;
    }}
    .tabla-inputs td.descripcion {{
        font-weight: 500;
    }}
    .tabla-inputs td.tipo,
    .tabla-inputs td.caracteristicas {{
        color: {COLORES['texto_medio']};
    }}
    .tabla-inputs td.num {{
        text-align: right;
        font-variant-numeric: tabular-nums;
    }}
    .inputs-pie {{
        margin-top: 2rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: {COLORES['texto_medio']};
        font-style: italic;
    }}
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Cabecera
st.markdown(
    """
    <div class="inputs-cabecera">
        <h1 class="inputs-titulo">Inputs del modelo</h1>
        <p class="inputs-subtitulo">
            Red de distribución MT/BT — Caso TFG. Inventario de los 20 activos
            con los datos físicos y los cuatro criterios que alimentan el modelo
            de optimización.
        </p>
        <div class="inputs-separador"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Construccion de la tabla a partir de datos.py
filas_html = []
for j in range(len(nombres)):
    fila = (
        f'<tr>'
        f'<td class="codigo">{nombres[j]}</td>'
        f'<td class="descripcion">{descripciones[j]}</td>'
        f'<td class="tipo">{tipos[j]}</td>'
        f'<td class="caracteristicas">{caracteristicas[j]}</td>'
        f'<td class="num">{int(edades[j])}</td>'
        f'<td class="num">{es_decimal(prob_fallo_bruta[j], 4)}</td>'
        f'<td class="num">{int(C2[j])}</td>'
        f'<td class="num">{es_miles(a[j])} €</td>'
        f'<td class="num">{es_decimal(b[j], 1)}</td>'
        f'</tr>'
    )
    filas_html.append(fila)
    
tabla_html = (
    '<table class="tabla-inputs">'
    '<thead>'
    '<tr>'
    '<th>Código</th>'
    '<th>Descripción</th>'
    '<th>Tipo</th>'
    '<th>Características</th>'
    '<th class="num">Edad (años)</th>'
    '<th class="num">Probabilidad de fallo</th>'
    '<th class="num">Impacto del fallo</th>'
    '<th class="num">Coste de intervención</th>'
    '<th class="num">Tiempo de intervención (h)</th>'
    '</tr>'
    '</thead>'
    '<tbody>'
    f'{"".join(filas_html)}'
    '</tbody>'
    '</table>'
)

st.markdown(tabla_html, unsafe_allow_html=True)

# Pie de pagina (mensaje de actualizacion + bloque Informacion tecnica / Proyecto)
st.markdown(
    """
    <div class="inputs-pie">
        Última actualización del inventario: 19 de mayo de 2026.
    </div>
    """,
    unsafe_allow_html=True,
)

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
