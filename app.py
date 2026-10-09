import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Simulador V2 Pro", layout="wide", page_icon="🚗")
st.title("🚗 Simulador V2 PRO: Circuito de Refrigeración")

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

dt=1; t_max=300; steps=int(t_max/dt)
temps=[]; aperturas=[]; t_motor=temp_init
for i in range(steps):
    calor=(rpm/1000)*4.5+2.0; caudal=(rpm/6000)
    if bajo_ref: caudal*=0.3
    if falla_term: apertura=0.0
    else:
        if t_motor<82: apertura=0.0
        elif t_motor>92: apertura=1.0
        else: apertura=(t_motor-82)/10
    flujo_aire=(vel/120)*6+1.5
    if t_motor>95 and not falla_vent: flujo_aire+=4.0
    eficiencia_rad=8.0*(1-rad_tapado/100)
    disipado=eficiencia_rad*caudal*apertura*(flujo_aire/10)*((t_motor-temp_amb)/60+0.5)
    t_motor+=(calor-disipado)*0.12
    t_motor=max(20,min(130,t_motor))
    temps.append(t_motor); aperturas.append(apertura*100)
    if t_motor>=129: break

k1,k2,k3,k4=st.columns(4)
k1.metric("T° Final Motor", f"{temps[-1]:.2f} °C")
k2.metric("Termostato", f"{aperturas[-1]:.0f}% abierto")
k3.metric("Flujo Aire", f"{flujo_aire:.1f} m/s")
estado="🔥 SOBRECALENTADO" if temps[-1]>105 else "✅ ÓPTIMO" if temps[-1]<98 else "⚠️ ALTO"
k4.metric("Estado", estado)

fig,ax=plt.subplots(figsize=(12,4))
t=np.linspace(0,len(temps),len(temps))
ax.plot(t,temps,linewidth=3,label="Temp Motor")
ax.axhline(82,color="blue",ls="--",alpha=0.7,label="Abre termostato 82°C")
ax.axhline(95,color="orange",ls="--",alpha=0.7,label="Prende ventilador 95°C")
ax.axhline(105,color="red",ls="--",alpha=0.7,label="Peligro 105°C")
ax.set_xlabel("Tiempo (s)"); ax.set_ylabel("°C")
ax.legend(); ax.grid(True,alpha=0.3)
st.pyplot(fig,use_container_width=True)

if temps[-1]>105:
    if falla_term: st.error("🔴 DIAGNÓSTICO: Termostato trabado cerrado.")
    elif rad_tapado>60: st.error(f"🔴 DIAGNÓSTICO: Radiador {rad_tapado}% obstruido.")
    elif falla_vent and vel<30: st.error("🔴 DIAGNÓSTICO: Sin ventilador + tráfico.")
    elif bajo_ref: st.error("🔴 DIAGNÓSTICO: Nivel bajo refrigerante.")
    else: st.error("🔴 DIAGNÓSTICO: Sobrecarga por alta RPM sostenida.")
elif temps[-1]>98: st.warning("🟡 Temperatura alta pero controlada.")
else: st.success("🟢 Sistema regulando correctamente.")
