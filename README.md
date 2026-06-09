# Priorización del mantenimiento preventivo en infraestructuras eléctricas

Dashboard interactivo que combina el método AHP (Analytic Hierarchy Process)
de Saaty con programación entera 0-1 para construir planes óptimos de
mantenimiento preventivo en redes de distribución MT/BT bajo restricciones
de presupuesto y horas-hombre.

**Trabajo Fin de Grado** — Grado en Ingeniería en Industria Conectada
Universidad Francisco de Vitoria · Madrid · Junio 2026
Autora: Carla Esono Ballesteros
Tutor: Joaquín Hidalgo Trucios

## Acceso al dashboard

URL pública: pendiente de publicación.

## Caso de estudio

Red de distribución urbana simulada con 20 activos: 4 transformadores MT/BT,
5 líneas MT subterráneas, 4 interruptores automáticos MT, 1 seccionador de
bucle, 4 fusibles BT y 2 líneas BT subterráneas. Inventario dimensionado
según el REBT (ITC-BT-10) y normativa de distribuidoras (E-Redes ET/5024,
Iberdrola MT 2.03.20).

## Estructura del código

- `Plan_de_mantenimiento.py` — página principal del dashboard (Streamlit).
- `pages/1_Inputs.py` — página de consulta del inventario completo.
- `datos.py` — inventario del caso de estudio + parámetros del modelo.
- `modelo_optimizacion.py` — construcción y resolución del modelo en PuLP.
- `cotas_analiticas.py` — cota inferior (greedy) y cota superior (LP)
  para validar el resultado del solver.
- `requirements.txt` — dependencias del proyecto.

## Ejecución local

\`\`\`bash
pip install -r requirements.txt
streamlit run Plan_de_mantenimiento.py
\`\`\`

## Modo demo

El dashboard incluye un modo demo activable desde la URL con el parámetro
\`?demo=1\`. Permite simular distintas antigüedades del inventario para
ilustrar el sistema de aviso de frescura de datos.

## Stack técnico

Python · Streamlit · Plotly · PuLP · CBC solver · pandas · openpyxl · numpy

