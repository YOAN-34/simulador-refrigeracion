import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Simulador V3 Dual", layout="wide", page_icon="🚗")
st.title("🚗 Simulador V3 PRO: Circuito de Refrigeración - Doble Gráfico")

with st.sidebar:
    st.header("⚙️ Panel de Control")
    rpm = st.slider("RPM Motor", 800, 6000, 2500, 100)
    vel = st.slider("Velocidad Vehículo (km/h)", 0, 120, 40)
    temp_amb = st.slider("T° Ambiente (°C)", 10, 45, 23)
    temp_init = st.slider("T° Inicial Motor (°C)", 20, 110, 65)
    st.divider()
    st.subheader("🔧 Modo Fallas")
    falla_term = st.toggle("Termostato trabado cerrado")
    falla_vent = st.toggle("Electroventilador no funciona")
    rad_tapado = st.slider("Radiador tapado %", 0, 100, 0)
    bajo_ref = st.toggle("Nivel bajo refrigerante")

dt=1; t_max=60; steps=int(t_max/dt)
temps=[]; aperturas=[]; vent_estado=[]; flujos=[]
t_motor=temp_init

for i in range(steps):
    calor=(rpm/1000)*1.8 + 1.5
    caudal=(rpm/6000)*0.9 + 0.2
    if bajo_ref: caudal*=0.35
    
    if falla_term: apertura=0.0
    else:
        if t_motor<82: apertura=0.0
        elif t_motor>92: apertura=1.0
        else: apertura=(t_motor-82)/10
    
    flujo_base=(vel/120)*5.0 + 1.0
    electro_on = 1 if (t_motor>95 and not falla_vent) else 0
    flujo_aire=flujo_base + (6.0 if electro_on else 0.0)
    
    k_rad=18.0*(1-rad_tapado/100)
    disipado=k_rad*caudal*apertura*(flujo_aire/5.0)*((t_motor-temp_amb)/50 + 0.6)
    t_motor+=(calor-disipado)*0.18
    t_motor=max(20,min(130,t_motor))
    
    temps.append(t_motor)
    aperturas.append(apertura*100)
    vent_estado.append(electro_on*100)
    flujos.append(flujo_aire)

k1,k2,k3,k4=st.columns(4)
k1.metric("T° Final", f"{temps[-1]:.1f} °C")
k2.metric("Termostato", f"{aperturas[-1]:.0f}% abierto")
k3.metric("Electroventilador", "ENCENDIDO 🔵" if vent_estado[-1]==100 else "APAGADO ⚪")
k4.metric("Flujo Aire", f"{flujos[-1]:.1f} m/s")

# GRAFICO 1 - TEMPERATURA
st.subheader("📈 Gráfico 1: Temperatura del Motor")
fig1,ax1=plt.subplots(figsize=(12,3.5))
t=np.linspace(0,len(temps),len(temps))
ax1.plot(t,temps,linewidth=3,color="#1f77b4",label="Temp Motor")
ax1.axhline(82,color="blue",ls="--",alpha=0.6,label="Abre termostato 82°C")
ax1.axhline(95,color="orange",ls="--",alpha=0.6,label="Prende ventilador 95°C")
ax1.axhline(105,color="red",ls="--",alpha=0.6,label="Peligro 105°C")
ax1.set_ylabel("°C"); ax1.set_xlabel("Tiempo (s)"); ax1.legend(); ax1.grid(True,alpha=0.3)
st.pyplot(fig1,use_container_width=True)

# GRAFICO 2 - CIRCUITO ELECTROVENTILADOR
st.subheader("⚡ Gráfico 2: Funcionamiento Circuito Electroventilador")
fig2,ax2=plt.subplots(figsize=(12,3.5))
ax2.plot(t,aperturas,linewidth=2.5,label="Apertura Termostato %",color="green")
ax2.plot(t,vent_estado,linewidth=2.5,label="Electroventilador ON/OFF %",color="orange",linestyle="--")
ax2.plot(t,flujos,linewidth=2.5,label="Flujo Aire m/s (x10)",color="purple")
ax2.set_ylabel("% / m/s"); ax2.set_xlabel("Tiempo (s)")
ax2.set_ylim(-5,110)
ax2.legend(); ax2.grid(True,alpha=0.3)
st.pyplot(fig2,use_container_width=True)

if temps[-1]>105:
    if falla_term: st.error("🔴 DIAGNÓSTICO: Termostato trabado cerrado.")
    elif falla_vent and vel<30: st.error("🔴 DIAGNÓSTICO: Electroventilador no funciona - en tráfico se sobrecalienta.")
    elif rad_tapado>60: st.error(f"🔴 DIAGNÓSTICO: Radiador {rad_tapado}% tapado.")
    else: st.error("🔴 DIAGNÓSTICO: Sobrecarga por alta RPM.")
elif temps[-1]>98: st.warning("🟡 Sistema en límite - ventilador encendido constante.")
else: st.success("🟢 Sistema OK: Termostato regula y ventilador entra solo a 95°C.")
