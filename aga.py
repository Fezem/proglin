import streamlit as st
from pulp import *

st.set_page_config(page_title="Optimización Telecom", layout="wide")

st.title("📡 Optimización de Red de Telecomunicaciones")

st.write("Modelo de programación lineal con costos realistas de infraestructura.")

# -----------------------------
# PARÁMETROS
# -----------------------------

st.header("📊 Parámetros de dispositivos")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("Antena A")
    covA = st.number_input("Cobertura A", value=5)
    capA = st.number_input("Capacidad A", value=40)
    eneA = st.number_input("Energía A", value=10)
    costA = st.number_input("Costo A (USD)", value=3000)
    manA = st.number_input("Mantenimiento A", value=2)
    confA = st.number_input("Confiabilidad A", value=8)

with col2:
    st.subheader("Antena B")
    covB = st.number_input("Cobertura B", value=8)
    capB = st.number_input("Capacidad B", value=70)
    eneB = st.number_input("Energía B", value=20)
    costB = st.number_input("Costo B (USD)", value=5000)
    manB = st.number_input("Mantenimiento B", value=3)
    confB = st.number_input("Confiabilidad B", value=9)

with col3:
    st.subheader("Drone")
    covD = st.number_input("Cobertura D", value=3)
    capD = st.number_input("Capacidad D", value=30)
    eneD = st.number_input("Energía D", value=15)
    costD = st.number_input("Costo D (USD)", value=7000)
    manD = st.number_input("Mantenimiento D", value=4)
    confD = st.number_input("Confiabilidad D", value=7)

with col4:
    st.subheader("Microcelda")
    covM = st.number_input("Cobertura M", value=10)
    capM = st.number_input("Capacidad M", value=90)
    eneM = st.number_input("Energía M", value=25)
    costM = st.number_input("Costo M (USD)", value=12000)
    manM = st.number_input("Mantenimiento M", value=5)
    confM = st.number_input("Confiabilidad M", value=10)

# -----------------------------
# RESTRICCIONES
# -----------------------------

st.header("⚙️ Restricciones")

col1, col2, col3 = st.columns(3)

with col1:
    presupuesto = st.number_input("Presupuesto (USD)", value=80000)
    energia_max = st.number_input("Energía máxima", value=250)
    mantenimiento_max = st.number_input("Mantenimiento máximo", value=30)

with col2:
    max_disp = st.number_input("Máx dispositivos", value=15)
    cap_min = st.number_input("Capacidad mínima", value=300)
    conf_min = st.number_input("Confiabilidad mínima", value=60)

with col3:
    usar_relacion = st.checkbox("Drone ≤ Antenas", value=True)
    micro_min = st.number_input("Microceldas mínimas", value=1)

# -----------------------------
# MODELO
# -----------------------------

if st.button("🚀 Resolver modelo"):

    model = LpProblem("Telecom", LpMaximize)

    # VARIABLES
    x = LpVariable("Antena_A", lowBound=0, cat="Integer")
    y = LpVariable("Antena_B", lowBound=0, cat="Integer")
    z = LpVariable("Drone", lowBound=0, cat="Integer")
    w = LpVariable("Microcelda", lowBound=0, cat="Integer")

    # OBJETIVO
    model += covA*x + covB*y + covD*z + covM*w

    # RESTRICCIONES

    # Presupuesto (AHORA REALISTA)
    model += costA*x + costB*y + costD*z + costM*w <= presupuesto

    model += eneA*x + eneB*y + eneD*z + eneM*w <= energia_max
    model += manA*x + manB*y + manD*z + manM*w <= mantenimiento_max
    model += x + y + z + w <= max_disp
    model += capA*x + capB*y + capD*z + capM*w >= cap_min
    model += confA*x + confB*y + confD*z + confM*w >= conf_min
    model += w >= micro_min

    if usar_relacion:
        model += z <= x + y

    model.solve()

    # -----------------------------
    # RESULTADOS
    # -----------------------------

    st.header("📌 Resultados")

    if LpStatus[model.status] == "Optimal":

        st.success("Solución óptima encontrada ✔")

        st.metric("Cobertura máxima", f"{value(model.objective):.2f} km²")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Antenas A", int(value(x)))
        col2.metric("Antenas B", int(value(y)))
        col3.metric("Drones", int(value(z)))
        col4.metric("Microceldas", int(value(w)))

        st.subheader("📊 Uso de recursos")

        costo = costA*value(x) + costB*value(y) + costD*value(z) + costM*value(w)
        energia = eneA*value(x) + eneB*value(y) + eneD*value(z) + eneM*value(w)
        mant = manA*value(x) + manB*value(y) + manD*value(z) + manM*value(w)
        cap = capA*value(x) + capB*value(y) + capD*value(z) + capM*value(w)
        conf = confA*value(x) + confB*value(y) + confD*value(z) + confM*value(w)

        st.write(f"💰 Costo: {costo:.0f} / {presupuesto}")
        st.write(f"⚡ Energía: {energia:.0f} / {energia_max}")
        st.write(f"🛠️ Mantenimiento: {mant:.0f} / {mantenimiento_max}")
        st.write(f"📡 Capacidad: {cap:.0f} (mín {cap_min})")
        st.write(f"🔒 Confiabilidad: {conf:.0f} (mín {conf_min})")

    else:
        st.error("No existe solución factible con estos parámetros")
