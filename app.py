import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador de Refrigeración", layout="wide")
st.title("🚗 Simulador Interactivo: Sistema de Refrigeración del Motor")

# Controles laterales
st.sidebar.header("🕹️ Panel de Control")
rpm = st.sidebar.slider("Revoluciones por Minuto (RPM)", 800, 6000, 2500, 100)
temp_inicial = st.sidebar.slider("Temperatura Inicial del Motor (°C)", 20, 110, 65)
falla_termostato = st.sidebar.checkbox("Termostato trabado (No abre)")

# Lógica matemática rápida
temperaturas = [temp_inicial]
tiempos = list(range(0, 61, 2))
temp_actual = temp_inicial

for _ in range(len(tiempos) - 1):
    calor_motor = rpm * 0.06
    apertura_termostato = 0.0 if falla_termostato or temp_actual < 80 else (1.0 if temp_actual > 90 else (temp_actual - 80) / 10.0)
    eficiencia = 0.8 * apertura_termostato
    if temp_actual >= 95 and not falla_termostato: eficiencia += 0.4
    
    cambio_temp = (calor_motor - (temp_actual * efficiency * (rpm / 1000.0))) / 150.0 if 'efficiency' in locals() else (calor_motor - (temp_actual * eficiencia * (rpm / 1000.0))) / 150.0
    temp_actual += cambio_temp
    temperaturas.append(round(temp_actual, 2))

# Indicadores en pantalla
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Temperatura Final del Motor", value=f"{temperaturas[-1]} °C")
with col2:
    st.metric(label="Estado del Termostato", value="❌ TRABADO" if falla_termostato else f"{int(apertura_termostato*100)}% Abierto")

# Gráfica
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(tiempos, temperaturas, color="red" if temperaturas[-1] >= 100 else "cyan", linewidth=2.5, marker="o")
ax.grid(True, linestyle=":")
st.pyplot(fig)
