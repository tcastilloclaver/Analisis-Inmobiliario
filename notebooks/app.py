import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración general de Streamlit
st.set_page_config(page_title="Análisis de Inmuebles en pisos.com", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

# Configuración de la barra lateral de navegación
menu = st.sidebar.selectbox("Navegación", ["Inicio", "Datos", "Comparador de Inmuebles"])

# Función para cargar y limpiar datos desde archivos CSV
@st.cache_data
def cargar_datos(tipo):
    data_path = "alquiler_inmuebles_limpio.csv" if tipo == "Alquiler" else "venta_inmuebles_limpio.csv"
    data = pd.read_csv(data_path)
    data.columns = data.columns.str.lower()
    data["precio"] = pd.to_numeric(data.get("precio", np.nan), errors='coerce')
    data["superficie construida"] = pd.to_numeric(data.get("superficie construida", np.nan), errors='coerce')
    data["habitaciones"] = pd.to_numeric(data.get("habitaciones", np.nan), errors='coerce')
    data["baños"] = pd.to_numeric(data.get("baños", np.nan), errors='coerce')
    data["consumo energético"] = pd.to_numeric(data.get("consumo energético", np.nan), errors='coerce')
    data["emisiones co2"] = pd.to_numeric(data.get("emisiones co2", np.nan), errors='coerce')
    data.columns = [col.capitalize() for col in data.columns]
    return data

# Página de inicio
if menu == "Inicio":
    st.title("Bienvenido a la Plataforma de Análisis Inmobiliario")
    st.write("Aquí encontrarás información sobre el mercado de alquiler y venta de inmuebles.")

# Página de Datos
elif menu == "Datos":
    # Selección de datos y filtros
    tipo_datos = st.sidebar.radio("Selecciona el tipo de datos a visualizar", ["Alquiler", "Venta"])
    data = cargar_datos(tipo_datos)
    
    st.sidebar.header("Filtros de búsqueda")
    precio_min, precio_max = st.sidebar.slider("Rango de Precio (€)", 
                                               500 if tipo_datos == "Alquiler" else 50000, 
                                               20000 if tipo_datos == "Alquiler" else 1000000, 
                                               (1000, 3000) if tipo_datos == "Alquiler" else (200000, 500000))
    data = data[(data["Precio"] >= precio_min) & (data["Precio"] <= precio_max)]

    superficie_min, superficie_max = st.sidebar.slider("Rango de Superficie (m²)", 10, 1000, (50, 200))
    data = data[(data["Superficie construida"] >= superficie_min) & (data["Superficie construida"] <= superficie_max)]

    # Resultados filtrados
    st.subheader(f"Resultados Filtrados - {tipo_datos}")
    st.write(data)

    # Gráficos de Distribución de Precio
    st.write("Distribución del Precio")
    fig, ax = plt.subplots()
    data["Precio"].dropna().hist(ax=ax, bins=30, color='skyblue')
    ax.set_title("Distribución del Precio")
    ax.set_xlabel("Precio (€)")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)
    plt.close(fig)

    # Gráfico de Precio vs Superficie Construida si existen datos
    if not data["Precio"].isna().all() and not data["Superficie construida"].isna().all():
        st.write("Relación entre Precio y Superficie Construida")
        fig, ax = plt.subplots()
        ax.scatter(data["Superficie construida"].dropna(), data["Precio"].dropna(), color='purple')
        ax.set_title("Relación entre Precio y Superficie Construida")
        ax.set_xlabel("Superficie Construida (m²)")
        ax.set_ylabel("Precio (€)")
        st.pyplot(fig)
        plt.close(fig)

    # Gráfico de Caja de Precio por Habitaciones
    if "Habitaciones" in data.columns and not data["Habitaciones"].isna().all() and not data["Precio"].isna().all():
        st.write("Precio según Número de Habitaciones")
        fig, ax = plt.subplots()
        data.boxplot(column='Precio', by='Habitaciones', grid=False, ax=ax)
        ax.set_title("Precio según Número de Habitaciones")
        st.pyplot(fig)
        plt.close(fig)

    # Gráfico de Consumo Energético vs Emisiones CO2 (solo para "Venta")
    if tipo_datos == "Venta" and "Consumo energético" in data.columns and "Emisiones co2" in data.columns:
        if not data["Consumo energético"].isna().all() and not data["Emisiones co2"].isna().all():
            st.write("Relación entre Consumo Energético y Emisiones CO2")
            fig, ax = plt.subplots()
            ax.scatter(data["Consumo energético"].dropna(), data["Emisiones co2"].dropna(), color='green')
            ax.set_title("Consumo Energético vs Emisiones CO2")
            ax.set_xlabel("Consumo Energético (kWh/m²)")
            ax.set_ylabel("Emisiones CO2 (Kg CO₂/m²)")
            st.pyplot(fig)
            plt.close(fig)

    # Mapa interactivo si hay coordenadas
    if "Latitude" in data.columns and "Longitude" in data.columns and not data["Latitude"].isna().all() and not data["Longitude"].isna().all():
        st.subheader("Mapa de Ubicaciones")
        st.map(data[["Latitude", "Longitude"]])

# Página de Comparador de Inmuebles
elif menu == "Comparador de Inmuebles":
    st.title("Comparador de Inmuebles")
    st.write("Busca y compara propiedades específicas.")
    
    # Campo de entrada para ID del inmueble
    comparador_placeholder = st.empty()
    with comparador_placeholder:
        inmueble = st.text_input("Introduce el ID del inmueble para buscar:")
        if inmueble:
            st.write(f"Mostrando detalles para el inmueble: {inmueble}")
            # Aquí podrías incluir la lógica para cargar y mostrar detalles específicos de inmuebles

    # Crear el DataFrame de comparación entre Alquiler y Venta
    alquiler_data, venta_data = cargar_datos("Alquiler"), cargar_datos("Venta")
    comparacion = pd.DataFrame({
        "Tipo": ["Alquiler", "Venta"],
        "Precio Promedio (€)": [alquiler_data["Precio"].mean(), venta_data["Precio"].mean()],
        "Superficie Promedio Construida (m²)": [alquiler_data["Superficie construida"].mean(), venta_data["Superficie construida"].mean()],
        "Número Promedio de Habitaciones": [alquiler_data["Habitaciones"].mean(), venta_data["Habitaciones"].mean()],
        "Número Promedio de Baños": [alquiler_data["Baños"].mean(), venta_data["Baños"].mean()]
    }).set_index("Tipo")

    # Comparación de Precio Promedio entre Alquiler y Venta
    st.write("Comparación de Precio Promedio entre Alquiler y Venta")
    st.bar_chart(comparacion[["Precio Promedio (€)"]])

    # Comparación de Superficie Construida Promedio entre Alquiler y Venta
    st.write("Comparación de Superficie Construida Promedio entre Alquiler y Venta")
    st.bar_chart(comparacion[["Superficie Promedio Construida (m²)"]])

    # Comparación de Número Promedio de Habitaciones entre Alquiler y Venta
    st.write("Comparación de Número Promedio de Habitaciones entre Alquiler y Venta")
    if not comparacion["Número Promedio de Habitaciones"].isnull().all():
        st.bar_chart(comparacion[["Número Promedio de Habitaciones"]])
    else:
        st.write("No hay datos disponibles para el Número Promedio de Habitaciones.")

    # Comparación de Número Promedio de Baños entre Alquiler y Venta
    st.write("Comparación de Número Promedio de Baños entre Alquiler y Venta")
    if not comparacion["Número Promedio de Baños"].isnull().all():
        st.bar_chart(comparacion[["Número Promedio de Baños"]])
    else:
        st.write("No hay datos disponibles para el Número Promedio de Baños.")



