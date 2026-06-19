import streamlit as st
from pulp import *

st.set_page_config(page_title="Optimización Telecom", layout="wide")

st.title("📡 Optimización de Red de Telecomunicaciones")

st.write("Modificá los parámetros y resolvé el modelo de programación lineal.")

# -------------------------
# INPUTS
# -------------------------

st.header("📊 Parámetros de dispositivos")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("Antena A")
    covA = st.number_input("Cobertura A", value=5)
    capA = st.number_input("Capacidad A", value=40)
    eneA = st.number_input("Energía A", value=10)
    costA = st.number_input("Costo A", value=4)
    manA = st.number_input("Mant. A", value=2)
    confA = st.number_input("Conf. A", value=8)

with col2:
    st.subheader("Antena B")
    covB = st.number_input("Cobertura B", value=8)
    capB = st.number_input("Capacidad B", value=70)
    eneB = st.number_input("Energía B", value=20)
    costB = st.number_input("Costo B", value=6)
    manB = st.number_input("Mant. B", value=3)
    confB = st.number_input("Conf. B", value=9)

with col3:
    st.subheader("Drone")
    covD = st.number_input("Cobertura D", value=3)
    capD = st.number_input("Capacidad D", value=30)
    eneD = st.number_input("Energía D", value=15)
    costD = st.number_input("Costo D", value=5)
    manD = st.number_input("Mant. D", value=4)
    confD = st.number_input("Conf. D", value=7)

with col4:
    st.subheader("Microcelda")
    covM = st.number_input("Cobertura M", value=10)
    capM = st.number_input("Capacidad M", value=90)
    eneM = st.number_input("Energía M", value=25)
    costM = st.number_input("Costo M", value=8)
    manM = st.number_input("Mant. M", value=5)
    confM = st.number_input("Conf. M", value=10)

st.header("⚙️ Restricciones")

c1, c2, c3 = st.columns(3)

with c1:
    presupuesto = st.number_input("Presupuesto", value=150)
    energia = st.number_input("Energía máxima", value=420)
    mantenimiento = st.number_input("Mantenimiento máximo", value=35)

with c2:
    max_disp = st.number_input("Máx dispositivos", value=18)
    cap_min = st.number_input("Capacidad mínima", value=900)
    conf_min = st.number_input("Confiabilidad mínima", value=100)

with c3:
    min_micro = st.number_input("Microceldas mínimas", value=2)
    usar_relacion = st.checkbox("Drone ≤ Antenas", value=True)

# -------------------------
# SOLVER
# -------------------------

if st.button("🚀 Resolver modelo"):

    model = LpProblem("Telecom", LpMaximize)

    x = LpVariable("A", lowBound=0, cat="Integer")
    y = LpVariable("B", lowBound=0, cat="Integer")
    z = LpVariable("D", lowBound=0, cat="Integer")
    w = LpVariable("M", lowBound=0, cat="Integer")

    # OBJETIVO
    model += covA*x + covB*y + covD*z + covM*w

    # RESTRICCIONES
    model += costA*x + costB*y + costD*z + costM*w <= presupuesto
    model += eneA*x + eneB*y + eneD*z + eneM*w <= energia
    model += manA*x + manB*y + manD*z + manM*w <= mantenimiento
    model += x + y + z + w <= max_disp
    model += capA*x + capB*y + capD*z + capM*w >= cap_min
    model += confA*x + confB*y + confD*z + confM*w >= conf_min
    model += w >= min_micro

    if usar_relacion:
        model += z <= x + y

    model.solve()

    # -------------------------
    # RESULTADOS
    # -------------------------

    st.header("📌 Resultados")

    if LpStatus[model.status] == "Optimal":

        st.success("Solución óptima encontrada")

        st.metric("Cobertura máxima", value=f"{value(model.objective):.2f} km²")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Antenas A", int(value(x)))
        col2.metric("Antenas B", int(value(y)))
        col3.metric("Drones", int(value(z)))
        col4.metric("Microceldas", int(value(w)))

        st.subheader("📊 Uso de recursos")

        costo = costA*value(x)+costB*value(y)+costD*value(z)+costM*value(w)
        energia_u = eneA*value(x)+eneB*value(y)+eneD*value(z)+eneM*value(w)
        mant = manA*value(x)+manB*value(y)+manD*value(z)+manM*value(w)
        cap = capA*value(x)+capB*value(y)+capD*value(z)+capM*value(w)
        conf = confA*value(x)+confB*value(y)+confD*value(z)+confM*value(w)

        st.write(f"💰 Costo: {costo:.2f} / {presupuesto}")
        st.write(f"⚡ Energía: {energia_u:.2f} / {energia}")
        st.write(f"🛠️ Mantenimiento: {mant:.2f} / {mantenimiento}")
        st.write(f"📡 Capacidad: {cap:.2f}")
        st.write(f"🔒 Confiabilidad: {conf:.2f}")

    else:
        st.error("No hay solución factible con estos datos")
