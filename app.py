import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Simulador", layout="wide", page_icon="🚗")

# --- ESTILOS VISUALES V2 PRO ---
st.markdown("""
<style>
@keyframes flow { 0%{background-position:0% 50%} 100%{background-position:100% 50%} }
.coolant-flow {
  height:12px; border-radius:10px;
  background: linear-gradient(90deg, #00b4ff, #ff3c3c, #00b4ff);
  background-size:200% 100%;
  animation: flow 1.5s linear infinite;
}
@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
.fan-on { animation: spin 0.3s linear infinite; display:inline-block; }
.engine-block { background: #1a1a1a; border-radius:16px; padding:15px; color:white; border:2px solid #333; }
.rad-ok { border-left:6px solid #00ff88; }
.rad-bad { border-left:6px solid #ff3c3c; }
</style>
""", unsafe_allow_html=True)

st.title("🚗 Simulador: Circuito de Refrigeración")

# --- CONTROLES ---
with st.sidebar:
    st.header("⚙️ Panel V2 PRO")
    rpm = st.slider("RPM Motor", 800, 6000, 2500, 100)
    vel = st.slider("Velocidad (km/h) - Enfría el radiador", 0, 120, 40)
    t_amb = st.slider("T° Ambiente °C", 10, 45, 23)
    t_init = st.slider("T° Inicial Motor °C", 20, 110, 65)
    st.divider()
    st.subheader("🔧 Fallas Reales")
    falla_term = st.toggle("Termostato trabado cerrado")
    falla_vent = st.toggle("Electroventilador no funciona")
    rad_tapado = st.slider("Radiador tapado %", 0, 100, 0)
    bajo_ref = st.toggle("Nivel bajo refrigerante")

# --- SIMULACIÓN FÍSICA ---
dt=1; t_max=90; steps=int(t_max/dt)
temps=[]; aperturas=[]; vent_log=[]; flujos=[]
t_motor=t_init

for i in range(steps):
    calor=(rpm/1000)*2.2 + 1.2
    caudal=(rpm/6000)*0.9 + 0.2
    if bajo_ref: caudal*=0.35
    if falla_term: apertura=0.0
    else:
        if t_motor<82: apertura=0.0
        elif t_motor>92: apertura=1.0
        else: apertura=(t_motor-82)/10.0
    
    flujo_base=(vel/120)*6.0 + 0.8
    electro_on = (t_motor>95 and not falla_vent)
    flujo=flujo_base + (6.5 if electro_on else 0.0)
    
    k_rad=22.0*(1-rad_tapado/100)
    disipado=k_rad*caudal*apertura*(flujo/6.0)*((t_motor-t_amb)/55 + 0.7)
    t_motor+=(calor-disipado)*0.22
    t_motor=np.clip(t_motor, 20, 135)
    temps.append(t_motor); aperturas.append(apertura*100)
    vent_log.append(100 if electro_on else 0); flujos.append(flujo)
    if t_motor>=129 and i>10: break

t_final=temps[-1]
ap_final=aperturas[-1]
electro_final = vent_log[-1]==100

# --- VISUAL SUPERIOR ---
col_vis1, col_vis2, col_vis3 = st.columns([1.2, 1, 1])

with col_vis1:
    st.markdown(f"""
    <div class="engine-block {'rad-bad' if t_final>105 else 'rad-ok'}">
        <h3 style="margin:0">🔥 Motor: {t_final:.1f}°C</h3>
        <div style="margin:10px 0">Refrigerante: {"🟦 Frío" if t_final<90 else "🟥 Caliente" if t_final>105 else "🟨 Tibio"}</div>
        <div class="coolant-flow" style="opacity:{0.3+ap_final/100}"></div>
        <small>Flujo: {ap_final:.0f}% abierto - Caudal: {caudal:.2f} L/s</small>
    </div>
    """, unsafe_allow_html=True)

with col_vis2:
    fan_icon = "🌀" if electro_final else "💤"
    fan_class = "fan-on" if electro_final else ""
    st.markdown(f"""
    <div class="engine-block">
        <h3 style="margin:0"><span class="{fan_class}">{fan_icon}</span> Electroventilador</h3>
        <p style="font-size:28px; margin:10px 0">{'ENCENDIDO' if electro_final else 'APAGADO'}</p>
        <p>Flujo aire: {flujos[-1]:.1f} m/s</p>
        <small>Vel. vehículo: {vel} km/h {'+ ventilador' if electro_final else ''}</small>
    </div>
    """, unsafe_allow_html=True)

with col_vis3:
    st.markdown(f"""
    <div class="engine-block">
        <h3 style="margin:0">🌡️ Radiador {100-rad_tapado}% libre</h3>
        <p style="font-size:26px; margin:10px 0">{'🟩 ÓPTIMO' if rad_tapado<30 else '🟨 SUCIO' if rad_tapado<70 else '🟥 TAPADO'}</p>
        <p>T° Ambiente: {t_amb}°C</p>
        <small>Disipación: {k_rad:.1f} kW/C</small>
    </div>
    """, unsafe_allow_html=True)

k1,k2,k3,k4=st.columns(4)
k1.metric("T° Final", f"{t_final:.1f} °C")
k2.metric("Termostato", f"{ap_final:.0f}% abierto")
k3.metric("Ventilador", "ON" if electro_final else "OFF", f"{flujos[-1]:.1f} m/s")
estado="🔥 SOBRECAL." if t_final>105 else "✅ ÓPTIMO" if t_final<98 else "⚠️ ALTO"
k4.metric("Estado", estado)

# --- GRAFICO 1 ---
st.subheader("📈 Gráfico 1: Temperatura del Motor vs Tiempo")
fig1,ax1=plt.subplots(figsize=(12,3.5))
t=np.arange(len(temps))
ax1.plot(t,temps,lw=3,label="Temp Motor")
ax1.axhline(82,color="blue",ls="--",alpha=0.6,label="Abre termostato 82°C")
ax1.axhline(95,color="orange",ls="--",alpha=0.6,label="Prende ventilador 95°C")
ax1.axhline(105,color="red",ls="--",alpha=0.6,label="Peligro 105°C")
ax1.set_xlabel("Tiempo (s)"); ax1.set_ylabel("°C"); ax1.grid(True,alpha=0.3); ax1.legend()
st.pyplot(fig1,use_container_width=True)

# --- GRAFICO 2 ---
st.subheader("⚡ Gráfico 2: Circuito Electroventilador y Termostato")
fig2,ax2=plt.subplots(figsize=(12,3.5))
ax2.plot(t,aperturas,lw=2.5,label="Apertura Termostato %",color="green")
ax2.plot(t,vent_log,lw=2.5,label="Electroventilador ON/OFF",color="orange",ls="--")
ax2.plot(t,np.array(flujos)*8,lw=2.5,label="Flujo Aire x8",color="purple",alpha=0.7)
ax2.set_ylim(-5,115); ax2.set_xlabel("Tiempo (s)"); ax2.set_ylabel("%"); ax2.grid(True,alpha=0.3); ax2.legend()
st.pyplot(fig2,use_container_width=True)

# --- DIAGNOSTICO ---
if t_final>105:
    if falla_term: st.error("🔴 DIAGNÓSTICO V2: Termostato trabado cerrado - 0% flujo al radiador.")
    elif rad_tapado>60: st.error(f"🔴 DIAGNÓSTICO V2: Radiador {rad_tapado}% tapado - no disipa calor.")
    elif falla_vent and vel<30: st.error("🔴 DIAGNÓSTICO V2: Sin ventilador + tráfico (baja velocidad) = sobrecalentamiento.")
    elif bajo_ref: st.error("🔴 DIAGNÓSTICO V2: Nivel bajo refrigerante - caudal insuficiente.")
    else: st.error("🔴 DIAGNÓSTICO V2: Sobrecarga por RPM sostenida + T° ambiente alta.")
elif t_final>98:
    st.warning("🟡 Sistema en límite: Ventilador trabajando constante.")
else:
    st.success(f"🟢 Sistema V2 PRO OK: {t_final:.1f}°C estable. Termostato regulando a {ap_final:.0f}% y flujo aire {flujos[-1]:.1f} m/s.")
