import streamlit as st  # <--- Corregido: "as st" en lugar de "as pd"
import pandas as pd
import requests
import matplotlib.pyplot as plt

# Configuración inicial del sitio
st.set_page_config(page_title="Portal Sísmico", page_icon="🌋", layout="wide")
st.title("🌋 Monitoreo de Actividad Sísmica Global")
st.caption("Visualización de eventos telúricos en tiempo real mediante la API pública de USGS.")

# Panel de control lateral
st.sidebar.header("Filtros de Búsqueda")
min_mag = st.sidebar.slider("Magnitud mínima", 1.0, 9.0, 4.5, 0.1)
max_rows = st.sidebar.number_input("Número de registros a cargar", min_value=10, max_value=100, value=30)

if st.sidebar.button("Buscar registros"):
    # Construcción dinámica de la URL
    api_url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude={min_mag}&limit={max_rows}"
    
    with st.spinner("Consultando base de datos internacional..."):
        response = requests.get(api_url)
        
        if response.status_code == 200:
            st.success("Conexión exitosa.")
            
            # Procesamiento del JSON de la API
            raw_data = response.json()
            events = raw_data.get("features", [])
            
            if not events:
                st.warning("No se encontraron sismos con los criterios seleccionados.")
            else:
                # Extracción y estructuración con Pandas
                properties_list = [evt["properties"] for evt in events]
                df_earthquakes = pd.DataFrame(properties_list)
                
                # Selección y renombrado de variables clave (usando .copy() para evitar warnings)
                df_final = df_earthquakes[['place', 'mag', 'time']].copy()
                df_final.columns = ['Ubicación', 'Magnitud', 'Fecha']
                
                # Conversión de timestamp (milisegundos) a formato legible
                df_final['Fecha'] = pd.to_datetime(df_final['Fecha'], unit='ms')
                
                # Sección de Datos
                st.subheader("📋 Registros Encontrados")
                st.dataframe(df_final, use_container_width=True)
                
                # Zona de descargas
                csv_file = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar datos en formato CSV",
                    data=csv_file,
                    file_name="reporte_sismos.csv",
                    mime="text/csv"
                )
                
                # Sección Gráfica
                st.subheader("📈 Tendencia de Magnitudes")
                df_sorted = df_final.sort_values('Fecha')
                
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(df_sorted['Fecha'], df_sorted['Magnitud'], marker='v', color='#E63946', linestyle='--')
                ax.set_xlabel("Tiempo")
                ax.set_ylabel("Escala Richter")
                ax.grid(True, linestyle=':', alpha=0.6)
                
                plt.xticks(rotation=35)
                plt.tight_layout()
                st.pyplot(fig)
        else:
            st.error(f"Error de comunicación. Código de respuesta: {response.status_code}")
else:
    st.info("💡 Define los parámetros en la barra de la izquierda y haz clic en 'Buscar registros' para empezar.")