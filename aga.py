import streamlit as st
from pulp import *

st.set_page_config(page_title="Optimización de Red de Telecomunicaciones",
                   page_icon="📡",
                   layout="wide")

st.title("📡 Optimización de una Red de Telecomunicaciones")

st.write("""
Modifique los parámetros del problema y presione **Resolver** para obtener
la combinación óptima de dispositivos.
""")

st.header("Datos de cada dispositivo")

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.subheader("Antena A")
    covA = st.number_input("Cobertura A (km²)", value=5)
    capA = st.number_input("Capacidad A (Mbps)", value=40)
    eneA = st.number_input("Consumo A (W)", value=10)
    costA = st.number_input("Costo A", value=4)
    manA = st.number_input("Mantenimiento A", value=2)
    confA = st.number_input("Confiabilidad A", value=8)

with col2:
    st.subheader("Antena B")
    covB = st.number_input("Cobertura B (km²)", value=8)
    capB = st.number_input("Capacidad B (Mbps)", value=70)
    eneB = st.number_input("Consumo B (W)", value=20)
    costB = st.number_input("Costo B", value=6)
    manB = st.number_input("Mantenimiento B", value=3)
    confB = st.number_input("Confiabilidad B", value=9)

with col3:
    st.subheader("Drone")
    covD = st.number_input("Cobertura Drone (km²)", value=3)
    capD = st.number_input("Capacidad Drone (Mbps)", value=30)
    eneD = st.number_input("Consumo Drone (W)", value=15)
    costD = st.number_input("Costo Drone", value=5)
    manD = st.number_input("Mantenimiento Drone", value=4)
    confD = st.number_input("Confiabilidad Drone", value=7)

with col4:
    st.subheader("Microcelda")
    covM = st.number_input("Cobertura Micro (km²)", value=10)
    capM = st.number_input("Capacidad Micro (Mbps)", value=90)
    eneM = st.number_input("Consumo Micro (W)", value=25)
    costM = st.number_input("Costo Micro", value=8)
    manM = st.number_input("Mantenimiento Micro", value=5)
    confM = st.number_input("Confiabilidad Micro", value=10)

st.header("Restricciones")

c1,c2,c3 = st.columns(3)

with c1:
    presupuesto = st.number_input("Presupuesto máximo", value=150)
    energia = st.number_input("Consumo máximo (W)", value=420)
    mantenimiento = st.number_input("Horas de mantenimiento", value=35)

with c2:
    dispositivos = st.number_input("Máximo de dispositivos", value=18)
    capacidad = st.number_input("Capacidad mínima (Mbps)", value=900)
    confiabilidad = st.number_input("Confiabilidad mínima", value=100)

with c3:
    minimo_micro = st.number_input("Microceldas mínimas", value=2)
    relacion = st.checkbox("Aplicar restricción Drone ≤ Antenas", value=True)

if st.button("Resolver problema"):

    modelo = LpProblem("Telecomunicaciones", LpMaximize)

    x = LpVariable("Antenas_A", lowBound=0, cat='Integer')
    y = LpVariable("Antenas_B", lowBound=0, cat='Integer')
    z = LpVariable("Drones", lowBound=0, cat='Integer')
    w = LpVariable("Microceldas", lowBound=0, cat='Integer')

    modelo += covA*x + covB*y + covD*z + covM*w

    modelo += costA*x + costB*y + costD*z + costM*w <= presupuesto
    modelo += eneA*x + eneB*y + eneD*z + eneM*w <= energia
    modelo += manA*x + manB*y + manD*z + manM*w <= mantenimiento
    modelo += x+y+z+w <= dispositivos
    modelo += capA*x + capB*y + capD*z + capM*w >= capacidad
    modelo += confA*x + confB*y + confD*z + confM*w >= confiabilidad
    modelo += w >= minimo_micro

    if relacion:
        modelo += z <= x+y

    modelo.solve()

    st.header("Resultados")

    if LpStatus[modelo.status] == "Optimal":

        st.success("Se encontró una solución óptima.")

        st.metric("Cobertura máxima", value=f"{value(modelo.objective):.2f} km²")

        st.subheader("Cantidad de dispositivos")

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("Antenas A", int(value(x)))
        c2.metric("Antenas B", int(value(y)))
        c3.metric("Drones", int(value(z)))
        c4.metric("Microceldas", int(value(w)))

        st.subheader("Uso de recursos")

        costo = costA*value(x)+costB*value(y)+costD*value(z)+costM*value(w)
        consumo = eneA*value(x)+eneB*value(y)+eneD*value(z)+eneM*value(w)
        mant = manA*value(x)+manB*value(y)+manD*value(z)+manM*value(w)
        cap = capA*value(x)+capB*value(y)+capD*value(z)+capM*value(w)
        conf = confA*value(x)+confB*value(y)+confD*value(z)+confM*value(w)

        st.write(f"**Costo utilizado:** {costo:.2f} / {presupuesto}")
        st.write(f"**Consumo energético:** {consumo:.2f} / {energia} W")
        st.write(f"**Horas de mantenimiento:** {mant:.2f} / {mantenimiento}")
        st.write(f"**Capacidad total:** {cap:.2f} Mbps")
        st.write(f"**Confiabilidad total:** {conf:.2f}")

    else:
        st.error("No existe una solución factible para los datos ingresados.")
