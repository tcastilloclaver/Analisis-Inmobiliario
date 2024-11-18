import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
import joblib

# Configuración general de Streamlit
st.set_page_config(page_title="Análisis de Inmuebles", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

# Configuración de la barra lateral de navegación
menu = st.sidebar.selectbox("Navegación", ["Inicio", "Datos", "Análisis Exploratorio", "Modelo de Clasificación"])

# Función para cargar y limpiar datos
@st.cache_data
def cargar_datos():
    """Carga los datos desde el archivo CSV y convierte columnas problemáticas a numéricas."""
    data_path = r"C:\Users\guill\OneDrive\Documentos\hack a boss\proyecto-FB-main\proyecto-FB\inmuebles_venta_limpio.csv"
    try:
        data = pd.read_csv(data_path)
        data.columns = data.columns.str.lower().str.strip()  # Convertir nombres de columnas a minúsculas y eliminar espacios

        # Mostrar columnas disponibles para depuración
        st.write("Columnas disponibles:", data.columns.tolist())

        # Convertir columnas específicas a numéricas
        columnas_a_convertir = ["precio", "superficie construida", "habitaciones", "baños", "consumo energético", "emisiones co2"]
        for col in columnas_a_convertir:
            if col in data.columns:
                if isinstance(data[col], pd.Series) and not data[col].empty:
                    st.write(f"Convirtiendo columna '{col}' a numérico.")
                    data[col] = pd.to_numeric(data[col], errors="coerce")
                else:
                    st.warning(f"Columna '{col}' no es válida o está vacía.")
            else:
                st.warning(f"Columna '{col}' no encontrada en los datos.")

        # Rellenar valores faltantes
        data = data.fillna(0)

        return data

    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {data_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

# Página de inicio
if menu == "Inicio":
    st.title("Bienvenido a la Plataforma de Análisis Inmobiliario")
    st.write("Explora y analiza datos de inmuebles en venta. Selecciona una opción en el menú para comenzar.")

# Página de Datos
elif menu == "Datos":
    st.title("Visualización de Datos")
    data = cargar_datos()

    if not data.empty:
        # Mostrar los datos cargados
        st.write("Vista previa de los datos:")
        st.dataframe(data.head())

        # Filtros básicos
        st.sidebar.header("Filtros")
        precio_min, precio_max = st.sidebar.slider("Rango de Precio (€)", 500, 1000000, (50000, 500000))
        superficie_min, superficie_max = st.sidebar.slider("Rango de Superficie (m²)", 10, 1000, (50, 200))

        # Aplicar filtros
        data_filtrado = data[(data["precio"] >= precio_min) & 
                             (data["precio"] <= precio_max) & 
                             (data["superficie construida"] >= superficie_min) & 
                             (data["superficie construida"] <= superficie_max)]
        st.write(f"Datos filtrados: {data_filtrado.shape[0]} filas")
        st.dataframe(data_filtrado)
    else:
        st.error("No se pudieron cargar los datos. Verifica el archivo CSV.")

# Página de Análisis Exploratorio
elif menu == "Análisis Exploratorio":
    st.title("Análisis Exploratorio")
    data = cargar_datos()

    if not data.empty:
        # Matriz de Correlación
        st.subheader("Matriz de Correlación")
        numeric_data = data.select_dtypes(include=["number"]).dropna(how="all")
        if not numeric_data.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(numeric_data.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        else:
            st.error("No hay datos numéricos disponibles para generar la matriz de correlación.")

        # Distribución de Precios
        st.subheader("Distribución de Precios")
        if "precio" in data.columns:
            fig = px.histogram(data, x="precio", nbins=50, title="Distribución de Precios")
            st.plotly_chart(fig)
        else:
            st.error("La columna 'precio' no está disponible en los datos.")
    else:
        st.error("No se pudieron cargar los datos para el análisis exploratorio.")

# Página de Modelo de Clasificación
elif menu == "Modelo de Clasificación":
    st.title("Modelo de Clasificación")
    data = cargar_datos()

    if not data.empty:
        # Seleccionar columnas numéricas
        numeric_data = data.select_dtypes(include=["number"]).dropna()
        if numeric_data.empty:
            st.error("No hay suficientes datos numéricos para entrenar un modelo.")
        else:
            # Escalar datos
            st.subheader("Escalado de Datos")
            scaler_option = st.radio("Selecciona el método de escalado", ["StandardScaler", "MinMaxScaler"])
            scaler = StandardScaler() if scaler_option == "StandardScaler" else MinMaxScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            st.write("Datos escalados listos para el modelo.")

            # División en conjunto de entrenamiento y prueba
            test_size = st.slider("Tamaño del conjunto de prueba (%)", 10, 50, 20) / 100
            X_train, X_test = train_test_split(scaled_data, test_size=test_size, random_state=42)
            st.write(f"Conjunto de entrenamiento: {len(X_train)} muestras")
            st.write(f"Conjunto de prueba: {len(X_test)} muestras")

            # Entrenar modelo de clasificación
            if st.button("Entrenar Modelo"):
                y_train = np.random.choice(["Grupo 1", "Grupo 2", "Grupo 3"], size=len(X_train))
                model = RandomForestClassifier(random_state=42)
                model.fit(X_train, y_train)
                st.success("Modelo entrenado con éxito.")
                joblib.dump(model, "modelo_clasificacion.pkl")
                st.success("Modelo guardado como 'modelo_clasificacion.pkl'.")

            # Cargar modelo y predecir
            if st.button("Probar Modelo"):
                try:
                    model = joblib.load("modelo_clasificacion.pkl")
                    y_pred = model.predict(X_test)
                    st.write("Predicciones:")
                    st.write(y_pred)
                except FileNotFoundError:
                    st.error("El modelo no se encuentra. Entrena un modelo primero.")
    else:
        st.error("No se pudieron cargar los datos para el modelo de clasificación.")
