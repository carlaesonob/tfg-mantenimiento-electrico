# datos.py - Datos del caso de estudio y vector de coeficientes de la funcion objetivo.

import numpy as np

# 1. Identificadores de los activos
nombres = [
    "T-CT1", "T-CT2", "T-CT3", "T-CT4",
    "LMT-1", "LMT-2", "LMT-3", "LMT-4", "LMT-5",
    "IA-CT1", "IA-CT2", "IA-CT3", "IA-CT4", "SEC-Bucle",
    "F-BT-2", "F-BT-3", "F-BT-6", "F-BT-7",
    "LBT-1", "LBT-2",
]
descripciones = [
    "Transformador CT-1",
    "Transformador CT-2",
    "Transformador CT-3",
    "Transformador CT-4",
    "Línea MT 1",
    "Línea MT 2",
    "Línea MT 3",
    "Línea MT 4",
    "Línea MT 5",
    "Interruptor automático CT-1",
    "Interruptor automático CT-2",
    "Interruptor automático CT-3",
    "Interruptor automático CT-4",
    "Seccionador de bucle",
    "Fusible BT-2",
    "Fusible BT-3",
    "Fusible BT-6",
    "Fusible BT-7",
    "Línea BT 1",
    "Línea BT 2",
]
# 1.B. Datos fisicos del inventario (metadatos descriptivos, no entran al modelo)
tipos = [
    "Transformador MT/BT",
    "Transformador MT/BT",
    "Transformador MT/BT",
    "Transformador MT/BT",
    "Línea MT subterránea",
    "Línea MT subterránea",
    "Línea MT subterránea",
    "Línea MT subterránea",
    "Línea MT subterránea",
    "Interruptor automático MT",
    "Interruptor automático MT",
    "Interruptor automático MT",
    "Interruptor automático MT",
    "Seccionador MT",
    "Fusible BT",
    "Fusible BT",
    "Fusible BT",
    "Fusible BT",
    "Línea BT subterránea",
    "Línea BT subterránea",
]
caracteristicas = [
    "400 kVA · 20/0,4 kV",
    "250 kVA · 20/0,4 kV",
    "400 kVA · 20/0,4 kV",
    "400 kVA · 20/0,4 kV",
    "HEPRZ1 12/20 kV · 240 mm² Al · 350 m",
    "HEPRZ1 12/20 kV · 240 mm² Al · 250 m",
    "HEPRZ1 12/20 kV · 240 mm² Al · 300 m",
    "HEPRZ1 12/20 kV · 240 mm² Al · 280 m",
    "HEPRZ1 12/20 kV · 240 mm² Al · 400 m",
    "24 kV",
    "24 kV",
    "24 kV",
    "24 kV",
    "24 kV · normalmente abierto",
    "400 V",
    "400 V",
    "400 V",
    "400 V",
    "XZ1 0,6/1 kV · 240 mm² Al · 80 m",
    "XZ1 0,6/1 kV · 240 mm² Al · 120 m",
]
edades = np.array([
    18, 32,  8, 22,
    25, 35, 12, 25, 40,
    18, 28,  8, 22, 30,
    10, 15,  6, 12,
    20, 15,
])

# 2. Matriz de evaluacion normalizada R (filas: activos; columnas: C1..C4; valores en [0,1])
R = np.array([
    [0.352, 0.000, 0.713, 0.724],   # T-CT1
    [0.583, 0.333, 0.527, 1.000],   # T-CT2
    [0.352, 0.333, 0.713, 0.724],   # T-CT3
    [0.352, 0.667, 0.713, 0.862],   # T-CT4
    [0.537, 0.333, 0.875, 0.497],   # LMT-1
    [0.583, 0.333, 0.623, 0.483],   # LMT-2
    [0.444, 0.333, 0.749, 0.490],   # LMT-3
    [0.407, 0.333, 0.698, 0.490],   # LMT-4
    [1.000, 1.000, 1.000, 0.641],   # LMT-5
    [0.167, 0.000, 0.214, 0.310],   # IA-CT1
    [0.306, 0.333, 0.214, 0.379],   # IA-CT2
    [0.167, 0.333, 0.214, 0.310],   # IA-CT3
    [0.167, 0.667, 0.214, 0.310],   # IA-CT4
    [0.167, 0.667, 0.112, 0.241],   # SEC-Bucle
    [0.815, 0.000, 0.000, 0.000],   # F-BT-2
    [0.815, 0.333, 0.000, 0.000],   # F-BT-3
    [0.815, 0.333, 0.000, 0.000],   # F-BT-6
    [0.815, 0.667, 0.000, 0.000],   # F-BT-7
    [0.000, 0.333, 0.057, 0.331],   # LBT-1
    [0.056, 0.667, 0.089, 0.345],   # LBT-2
])

# 2.B. Probabilidad de fallo bruta (C1 antes de normalizar)
prob_fallo_bruta = np.array([
    0.0050, 0.0075, 0.0050, 0.0050,
    0.0070, 0.0075, 0.0060, 0.0056, 0.0120,
    0.0030, 0.0045, 0.0030, 0.0030, 0.0030,
    0.0100, 0.0100, 0.0100, 0.0100,
    0.0012, 0.0018,
])

# 3. Vector de pesos AHP (CR = 3,68 % < 10 %)
w = np.array([0.2746, 0.5753, 0.0589, 0.0911])

# 4. Costes a_j (euros) y tiempos b_j (horas) de intervencion
a = np.array([
    22931, 17000, 22931, 22931,
    28049, 20035, 24042, 22439, 32056,
     7000,  7000,  7000,  7000,  3750,
      160,   160,   160,   160,
     2000,  3000,
])

b = np.array([
    12.0, 16.0, 12.0, 14.0,
     8.7,  8.5,  8.6,  8.6, 10.8,
     6.0,  7.0,  6.0,  6.0,  5.0,
     1.5,  1.5,  1.5,  1.5,
     6.3,  6.5,
])

# 5. Criticidad C2 bruta (escala 1 a 5); activos con C2 = 5 se fuerzan
C2 = np.array([
    2, 3, 3, 4,
    3, 3, 3, 3, 5,
    2, 3, 3, 4, 4,
    2, 3, 3, 4,
    3, 4,
])

# 6. Parametros nominales del modelo
B_nominal = 100_000     # Presupuesto disponible (euros)
H_nominal = 60          # Horas-hombre disponibles

# Subconjunto critico forzado: construccion generativa a partir de C2 = 5
J_critico = [int(j) for j in np.where(C2 == 5)[0]]

# 7. Vector de coeficientes de la funcion objetivo: c = R @ w
c = R @ w