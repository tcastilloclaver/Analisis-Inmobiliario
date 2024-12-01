import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from scipy import stats
import joblib
import os
import base64


# Configuración general de Streamlit
st.set_page_config(
    page_title="Análisis de Inmuebles - Proyecto Final",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.image("pisoslogo.png")

menu = st.sidebar.selectbox(
    "Navegación",
    ["Inicio", "Vista para Usuarios", "Vista para Clientes","Análisis Avanzado","Esquema de Base de Datos", "Contacto","About Us"]
)

# Función para cargar y limpiar datos
@st.cache_data
def cargar_datos(tipo):
    try:
        data_path = "inmuebles_alquilerconcp.csv" if tipo == "Alquiler" else "inmueblesventaconcp.csv"
        data = pd.read_csv(data_path)
        data.columns = data.columns.str.lower().str.strip()

        # Convertir columnas a tipo numérico
        columnas_numericas = ["precio", "superficie construida", "habitaciones", "baños", "consumo energético", "emisiones co2"]
        for columna in columnas_numericas:
            if columna in data.columns:
                data[columna] = pd.to_numeric(data[columna], errors="coerce")
        
        # Verificar y limpiar la columna 'cp' si existe
        if "cp" in data.columns:
            data["cp"] = data["cp"].astype(str).str.extract(r'(\d{5})')[0]  # Extraer solo códigos válidos (5 dígitos)
            data = data.dropna(subset=["cp"])  # Eliminar filas con 'cp' nulo
        else:
            st.warning("La columna 'cp' no está disponible en los datos. Algunas funcionalidades pueden estar limitadas.")
            data["cp"] = None  # Añadir una columna vacía si no existe 'cp'

        return data
    except FileNotFoundError:
        st.error(f"No se encontró el archivo: {data_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def cargar_geojson():
    try:
        geojson_path = "MADRID.geojson"
        madrid_geojson = gpd.read_file(geojson_path)
        return madrid_geojson
    except FileNotFoundError:
        st.error("No se encontró el archivo MADRID.geojson.")
        return None
    except Exception as e:
        st.error(f"Error al cargar el archivo GeoJSON: {str(e)}")
        return None

# Función para escalar los datos
def escalar_datos(df, columnas):
    scaler = MinMaxScaler()
    df_escalado = df.copy()
    df_escalado[columnas] = scaler.fit_transform(df[columnas].fillna(0))
    return df_escalado
# Página: Esquema de Base de Datos
if menu == "Esquema de Base de Datos":
    st.title("Esquema de la Base de Datos")
    st.write("""
    A continuación, se muestra el esquema de la base de datos utilizada en el proyecto.
    Este esquema detalla las tablas principales y sus relaciones.
    """)

    # Mostrar el diagrama exportado
    st.image("dbeaver.drawio.png", caption="Esquema de la Base de Datos", use_column_width=True)

    # Explicación adicional de las tablas
    st.write("""
    ### Descripción de las Tablas

#### **1. `alquiler_data`**
- **Utilidad**: 
  Esta tabla almacena información detallada sobre los inmuebles disponibles para **alquiler**. Se utiliza para realizar análisis específicos del mercado de alquiler.
- **Columnas**:
  - **`id`**: Identificador único del inmueble (clave primaria).
  - **`descripcion`**: Breve descripción de la propiedad (puede incluir detalles sobre distribución, estilo o estado).
  - **`localizacion`**: Dirección o ubicación de la propiedad.
  - **`precio`**: Precio del alquiler en euros.
  - **`ultima_actualizacion`**: Fecha de la última modificación o actualización de la información.
  - **`tipo_operacion`**: Especifica que la operación corresponde a "alquiler".
  - **`superficie_construida`**: Metros cuadrados totales construidos.
  - **`superficie_util`**: Metros cuadrados útiles disponibles para el inquilino.
  - **`habitaciones`**: Número de habitaciones.
  - **`baños`**: Número de baños.
  - **`antigüedad`**: Años desde la construcción de la propiedad.
  - **`conservacion`**: Estado de conservación del inmueble (e.g., nuevo, reformado, a renovar).
  - **`codigo_postal`**: Código postal del inmueble.
  - **`planta`**: Piso o planta en la que se encuentra la vivienda (si es un edificio).
  - **`tipo_casa`**: Clasificación del tipo de propiedad (e.g., apartamento, chalet, dúplex).
  - **`cp`**: Código postal (formato resumido o estándar).

#### **2. `venta_data`**
- **Utilidad**: 
  Esta tabla almacena información detallada sobre los inmuebles disponibles para **venta**. Permite realizar análisis de precios, evaluar propiedades en función de sus características y comparar tendencias con el mercado de alquiler.
- **Columnas**:
  - **`id`**: Identificador único del inmueble (clave primaria).
  - **`descripcion`**: Detalles descriptivos de la propiedad (e.g., "piso exterior con terraza").
  - **`localizacion`**: Dirección o ubicación del inmueble.
  - **`precio`**: Precio de venta en euros.
  - **`ultima_actualizacion`**: Fecha de la última modificación de la información.
  - **`tipo_operacion`**: Especifica que la operación corresponde a "venta".
  - **`superficie_construida`**: Metros cuadrados totales construidos.
  - **`superficie_util`**: Metros cuadrados útiles disponibles.
  - **`habitaciones`**: Número de habitaciones.
  - **`baños`**: Número de baños.
  - **`antigüedad`**: Años desde la construcción.
  - **`conservacion`**: Estado de la propiedad (e.g., nuevo, reformado).
  - **`codigo_postal`**: Código postal de la ubicación.
  - **`planta`**: Piso o planta en la que se encuentra la vivienda.
  - **`tipo_casa`**: Tipo de inmueble (e.g., chalet, estudio).
  - **`cp`**: Código postal en formato reducido.

#### **3. `inmuebles_combined`**
- **Utilidad**: 
  Esta tabla consolida la información de las tablas `alquiler_data` y `venta_data`, permitiendo realizar análisis unificados sobre el mercado inmobiliario (alquiler y venta). Se utiliza para estudios globales o comparaciones entre ambos tipos de operación.
- **Columnas**:
  - **`id`**: Identificador único del inmueble (clave primaria).
  - **`tipo_operacion_origen`**: Indica si el inmueble proviene de la tabla de `alquiler_data` o `venta_data`.
  - **`descripcion`**: Descripción de la propiedad.
  - **`localizacion`**: Dirección o ubicación.
  - **`precio`**: Precio de alquiler o venta, dependiendo del tipo de operación.
  - **`ultima_actualizacion`**: Fecha de la última modificación de la información.
  - **`tipo_operacion`**: Especifica el tipo de operación ("alquiler" o "venta").
  - **`superficie_construida`**: Metros cuadrados totales construidos.
  - **`superficie_util`**: Metros cuadrados útiles.
  - **`habitaciones`**: Número de habitaciones.
  - **`baños`**: Número de baños.
  - **`antigüedad`**: Años desde la construcción.
  - **`conservacion`**: Estado de la propiedad.
  - **`cp`**: Código postal del inmueble.
  - **`planta`**: Piso o planta.
  - **`tipo_casa`**: Tipo de inmueble.
    """)
# Página: Inicio
if menu == "Inicio":
    st.title("Proyecto Final de Bootcamp")
    st.write("""
    ### Descripción del Proyecto
    ¡Hola! Este proyecto es una aplicación web que hemos creado con Streamlit para explorar el mercado inmobiliario en España. Usamos datos de pisos.com y construimos una base de datos para organizar todo de forma eficiente. Además, diseñamos un proceso ETL para que la información siempre esté actualizada.

    ### Funcionalidades Principales

    #### **Vista para Usuarios**
    - **Mapa interactivo**: Visualización geográfica de los inmuebles con filtros por zonas.
    - **Tabla de datos**: Consulta detalles completos de los inmuebles disponibles en un formato claro y accesible.
    - **Dashboard interactivo**: Explora precios, superficies y otras variables importantes mediante gráficos y tablas dinámicas.
    - **Ficha detallada**: Visualiza información específica de cada inmueble seleccionado.
    - **Comparador de propiedades**: Herramienta que permite comparar múltiples inmuebles para tomar decisiones informadas.

    #### **Vista para Clientes**
    - **Dashboard en Power BI**: Análisis visuales personalizados con KPIs clave del mercado inmobiliario.
    - **Esquema de la base de datos**: Muestra la estructura de los datos almacenados, facilitando su interpretación.

    #### **Análisis Avanzado**
    - **Predicción de precios**: Utiliza un modelo de Machine Learning para estimar el precio de inmuebles según sus características principales (superficie, número de habitaciones, consumo energético, etc.).

    #### **Contacto**
    - **Formulario interactivo**: Permite enviar mensajes directamente al equipo de desarrollo para consultas o comentarios.

    #### **About Us**
    - **Información del equipo**: Conoce a los desarrolladores del proyecto y accede a sus perfiles de LinkedIn y GitHub.

    ### Características Adicionales
    - **Filtros avanzados**: Herramientas para buscar inmuebles según criterios específicos como precio, tamaño o ubicación.
    - **Datos actualizados**: Un proceso ETL mantiene la base de datos sincronizada con los datos más recientes.
    - **Navegación intuitiva**: El diseño modular permite moverse fácilmente entre las diferentes secciones de la aplicación.

    ### Implementación Modular
    Todas las secciones están organizadas como funciones individuales para garantizar un código limpio, escalable y fácil de mantener.
    """)
# Vista para Usuarios
elif menu == "Vista para Usuarios":
    st.title("Vista para Usuarios")
    st.write("""
    Esta sección está orientada al público en general y ofrece análisis interactivo de inmuebles.
    """)

    # Cargar datos y GeoJSON
    tipo_datos = st.sidebar.radio("Selecciona el tipo de datos", ["Alquiler", "Venta"])
    data = cargar_datos(tipo_datos)
    geojson_data = cargar_geojson()

    if not data.empty:
        # Filtro de precio
        if "precio" in data.columns:
            st.sidebar.subheader("Filtro de Precios")
            precio_min, precio_max = int(data["precio"].min()), int(data["precio"].max())
            rango_precio = st.sidebar.slider(
                "Selecciona el rango de precio (€)",
                min_value=precio_min,
                max_value=precio_max,
                value=(precio_min, precio_max),
                step=100
            )
            data = data[(data["precio"] >= rango_precio[0]) & (data["precio"] <= rango_precio[1])]
        else:
            st.warning("La columna 'precio' no está disponible en los datos.")

        # Filtro por número de habitaciones
        if "habitaciones" in data.columns:
            st.sidebar.subheader("Filtro por Número de Habitaciones")
            opciones_habitaciones = sorted(data["habitaciones"].dropna().unique())
            habitaciones_seleccionadas = st.sidebar.selectbox(
                "Selecciona el número de habitaciones",
                options=["Todas"] + opciones_habitaciones
            )
            if habitaciones_seleccionadas != "Todas":
                data = data[data["habitaciones"] == habitaciones_seleccionadas]
        else:
            st.warning("La columna 'habitaciones' no está disponible en los datos.")

        # Filtro por número de baños
        if "baños" in data.columns:
            st.sidebar.subheader("Filtro por Número de Baños")
            opciones_baños = sorted(data["baños"].dropna().unique())
            baños_seleccionados = st.sidebar.selectbox(
                "Selecciona el número de baños",
                options=["Todas"] + opciones_baños
            )
            if baños_seleccionados != "Todas":
                data = data[data["baños"] == baños_seleccionados]
        else:
            st.warning("La columna 'baños' no está disponible en los datos.")

        # Filtro por código postal
        if "cp" in data.columns and data["cp"].notnull().any():
            codigos_postales_unicos = sorted(data["cp"].unique())
            codigo_postal_seleccionado = st.sidebar.multiselect(
                "Filtrar por Código Postal",
                options=codigos_postales_unicos,
                default=codigos_postales_unicos[:5]
            )
            if codigo_postal_seleccionado:
                data = data[data["cp"].isin(codigo_postal_seleccionado)]
        else:
            st.warning("No hay datos de códigos postales disponibles para filtrar.")

        # Tabla interactiva
        st.subheader("Datos Filtrados")
        st.dataframe(data)

        # Mapa coroplético interactivo
        if geojson_data is not None:
            st.subheader("Mapa Coroplético - Cantidad de Inmuebles por Código Postal")
            inmuebles_count_cp = data.groupby("cp").size().reset_index(name="Cantidad de Inmuebles")
            fig = px.choropleth_mapbox(
                inmuebles_count_cp,
                geojson=geojson_data,
                locations="cp",
                featureidkey="properties.COD_POSTAL",
                color="Cantidad de Inmuebles",
                hover_name="cp",
                title="Cantidad de Inmuebles por Código Postal",
                mapbox_style="carto-positron",
                center={"lat": 40.4168, "lon": -3.7038},
                zoom=10,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Histograma de precios
        st.subheader("Histograma de Precios")
        fig = px.histogram(
            data,
            x='precio',
            nbins=50,
            title='Distribución de Precios',
            labels={'precio': 'Precio (€)'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Relación entre precio y superficie construida
        st.subheader("Relación entre Precio y Superficie Construida")
        superficie_df = data[data["superficie construida"] <= 2000].dropna(subset=["precio", "superficie construida", "cp"])
        fig = px.scatter(
            superficie_df,
            x="superficie construida",
            y="precio",
            color="cp",
            title="Relación entre Precio y Superficie Construida por Código Postal",
            labels={"superficie construida": "Superficie Construida (m²)", "precio": "Precio (€)", "cp": "Código Postal"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Relación entre precio y antigüedad (Boxplot)
        if "antigüedad" in data.columns:
            st.subheader("Relación entre Precio y Antigüedad (Boxplot)")
            data['antigüedad'] = pd.to_numeric(data['antigüedad'].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
            data['precio'] = pd.to_numeric(data['precio'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
            data = data.dropna(subset=['antigüedad', 'precio'])

            # Crear el boxplot
            fig = px.box(
                data,
                x='antigüedad',
                y='precio',
                title='Distribución de Precios por Antigüedad',
                labels={'antigüedad': 'Antigüedad (años)', 'precio': 'Precio (€)'},
                color='antigüedad',  # Opcional, para diferenciar por color
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("La columna 'antigüedad' no está disponible en los datos.")

        # Comparador de inmuebles
        st.subheader("Comparador de Inmuebles")
        columnas_para_escalar = ["habitaciones", "baños", "superficie construida", "precio"]
        df_escalado = escalar_datos(data.dropna(subset=columnas_para_escalar), columnas_para_escalar)

        if not df_escalado.empty:
            opciones = {f"Inmueble {i}": i for i in df_escalado.index}
            inmueble1_idx = st.selectbox("Selecciona el primer inmueble:", list(opciones.keys()), key="inmueble1")
            inmueble2_idx = st.selectbox("Selecciona el segundo inmueble:", list(opciones.keys()), key="inmueble2")

            if st.button("Comparar Inmuebles"):
                inmueble1 = df_escalado.loc[opciones[inmueble1_idx], columnas_para_escalar]
                inmueble2 = df_escalado.loc[opciones[inmueble2_idx], columnas_para_escalar]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=inmueble1.values,
                    theta=columnas_para_escalar,
                    fill='toself',
                    name=f'Inmueble {inmueble1_idx}'
                ))
                fig.add_trace(go.Scatterpolar(
                    r=inmueble2.values,
                    theta=columnas_para_escalar,
                    fill='toself',
                    name=f'Inmueble {inmueble2_idx}'
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    title="Comparación de Características entre dos Inmuebles",
                    showlegend=True
                )
                st.plotly_chart(fig)

        # Ficha detallada de inmuebles
        st.subheader("Ficha Detallada de Inmuebles")
        inmuebles_disponibles = data["id"].unique()
        inmueble_seleccionado = st.selectbox(
            "Selecciona un inmueble para ver los detalles",
            options=inmuebles_disponibles,
            format_func=lambda x: f"Inmueble {x}"
        )

        # Mostrar detalles del inmueble seleccionado
        inmueble = data[data["id"] == inmueble_seleccionado].iloc[0]
        st.write(f"### {inmueble.get('descripción', 'Sin descripción')}")
        st.write(f"**Precio**: {inmueble.get('precio', 'No disponible')} €")
        st.write(f"**Superficie Construida**: {inmueble.get('superficie construida', 'No disponible')} m²")
        st.write(f"**Habitaciones**: {inmueble.get('habitaciones', 'No disponible')}")
        st.write(f"**Baños**: {inmueble.get('baños', 'No disponible')}")
        st.write(f"**Ubicación**: {inmueble.get('localización', 'No disponible')}")
        st.write(f"**Antigüedad**: {inmueble.get('antigüedad', 'No disponible')} años")

        # Mostrar imágenes del inmueble si están disponibles
        imagen_url = inmueble.get("imagen", None)
        if pd.notna(imagen_url):
            st.image(imagen_url, caption="Vista del inmueble", use_column_width=True)
        else:
            st.warning("No hay imágenes disponibles para este inmueble.")

        # Mostrar mapa con la ubicación si está disponible
        latitud = inmueble.get("latitud", None)
        longitud = inmueble.get("longitud", None)
        if pd.notna(latitud) and pd.notna(longitud):
            st.map(pd.DataFrame({'lat': [latitud], 'lon': [longitud]}))
        else:
            st.warning("No hay información de ubicación para este inmueble.")

        # Mostrar características adicionales
        st.write("### Características Adicionales")
        st.write(inmueble.get("características", "No disponible"))



elif menu == "Vista para Clientes":
    st.title("Vista para Clientes")
    st.write("""
    Esta sección está dirigida a un público más especializado y ofrece:
    - **Análisis avanzado de datos**: Tendencias, precios y características destacadas de los inmuebles.
    - **KPIs clave**: Datos resumidos para una rápida toma de decisiones.
    - **Integración con Power BI y Reportes PDF y HTML**: Visualizaciones personalizadas y dinámicas del negocio inmobiliario.
    """)




    # **1. Descargar el PDF:**
    st.subheader("Descargar el Dashboard en PDF:")
    pdf_path = "dashboard.pdf"  # Ruta del archivo PDF
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            st.download_button(
                label="Descargar Dashboard PDF",
                data=pdf_data,
                file_name="dashboard.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error al procesar el archivo PDF: {e}")
    else:
        st.error(f"No se encontró el archivo PDF: '{pdf_path}'. Verifica su ubicación.")


    # **2. Power BI:**
    st.title("Informe Adicional de Power BI")
    powerbi_width = 600
    powerbi_height = 373.5
    st.markdown(
        body=f"""
        <iframe title="Informe Adicional Power BI" width="{powerbi_width}" height="{powerbi_height}" 
        src="https://app.powerbi.com/view?r=eyJrIjoiZjFhOGY0ZjItZWM1MC00OTEwLWFiMDMtMzliOWYzZjFmMTE1IiwidCI6IjVlNzNkZTM1LWU4MjUtNGVkNS1iZTIyLTg4NTYzNTI3MDkxZSIsImMiOjl9&pageName=5b02787c82b37e935098" 
        frameborder="0" allowFullScreen="true"></iframe>
        """, 
        unsafe_allow_html=True
    )






    # Descripción adicional del dashboard y sus características
    st.write("""
    ### Características del Dashboard
    - **KPIs Clave**: Precio promedio, inmuebles disponibles por región, y métricas adicionales.
    - **Gráficos Interactivos**: Distribuciones, tendencias y análisis por áreas.
    - **Actualización Dinámica**: Datos cargados y procesados en tiempo real desde tu base de datos.
    """)

    # Mensaje final para personalización del reporte
    st.write("Si deseas una funcionalidad adicional o personalizar el reporte, ¡contáctanos!")

# Página: Análisis Avanzado
elif menu == "Análisis Avanzado":
    st.title("Análisis Avanzado")
    st.write("""
    En esta sección puedes utilizar un modelo de Machine Learning para predecir el precio estimado de un inmueble basado en sus características principales.
    """)

    # Función para cargar el modelo
    @st.cache_resource
    def load_model():
        model = joblib.load("model.pkl")  # Asegúrate de ajustar el path si el modelo está en otro directorio
        return model

    # Cargar el modelo
    model = load_model()

    # Verificar si el modelo está cargado correctamente
    if model:
        st.subheader("Estimador de Precio de Inmueble")
        
        # Formulario para ingresar datos del inmueble
        st.write("Ingrese las características del inmueble para realizar la predicción:")
        
        # Recolectar datos de entrada del usuario
        superficie = st.number_input("Superficie Construida (m²)", min_value=10, max_value=1000, value=100)
        habitaciones = st.number_input("Número de Habitaciones", min_value=1, max_value=10, value=3)
        baños = st.number_input("Número de Baños", min_value=1, max_value=5, value=1)
        consumo_energetico = st.number_input("Consumo Energético (kWh/m² año)", min_value=0.0, value=100.0, step=1.0)
        emisiones_co2 = st.number_input("Emisiones CO2 (kgCO2/m² año)", min_value=0.0, value=50.0, step=1.0)

        # Botón para realizar la predicción
        if st.button("Predecir Precio"):
            # Preparar los datos de entrada para el modelo
            input_data = np.array([[superficie, habitaciones, baños, consumo_energetico, emisiones_co2]])

            try:
                # Realizar la predicción con el modelo cargado
                prediction = model.predict(input_data)
                # Mostrar el resultado de la predicción
                st.write(f"**Precio estimado del inmueble:** €{prediction[0]:,.2f}")
            except Exception as e:
                st.error(f"Error al realizar la predicción: {e}")
    else:
        st.error("El modelo no se pudo cargar correctamente. Por favor, verifica la configuración del archivo 'model.pkl'.")



# Página: Contacto
elif menu == "Contacto":
    st.title("Contacto")
    with st.form(key='contact_form'):
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        mensaje = st.text_area("Mensaje")
        submit_button = st.form_submit_button(label='Enviar')

    if submit_button:
        st.success("¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.")

# Página: About Us
elif menu == "About Us":
    st.title("About Us")
    st.write("""
    ### Equipo de Desarrollo
    Conoce a los integrantes del proyecto:
    """)

    integrantes = [
        {"nombre": "Tomás Castillo Claver", "linkedin": "http://linkedin.com/in/tom%C3%A1s-castillo-claver-2271002a8", "github": "https://github.com/tcastilloclaver"},
        {"nombre": "Miguel González Llanera", "linkedin": "http://www.linkedin.com/in/miguel-gonzalez-llanera-storemanager", "github": "https://github.com/miguelgonzalez23"},
        {"nombre": "Guillermo Pérez Toba", "linkedin": "https://www.linkedin.com/in/guillermo-p%C3%A9rez-toba/", "github": "https://github.com/GuillePT95"},
    ]

    for integrante in integrantes:
        st.subheader(integrante["nombre"])
        st.write(f"[LinkedIn]({integrante['linkedin']}) | [GitHub]({integrante['github']})")

elif menu == "Power BI":
    st.title("Informe Adicional de Power BI")
    powerbi_width = 600
    powerbi_height = 373.5
    st.markdown(
        body=f"""
        <iframe title="Informe Adicional Power BI" width="{powerbi_width}" height="{powerbi_height}" 
        src="https://app.powerbi.com/view?r=eyJrIjoiZjFhOGY0ZjItZWM1MC00OTEwLWFiMDMtMzliOWYzZjFmMTE1IiwidCI6IjVlNzNkZTM1LWU4MjUtNGVkNS1iZTIyLTg4NTYzNTI3MDkxZSIsImMiOjl9&pageName=5b02787c82b37e935098" 
        frameborder="0" allowFullScreen="true"></iframe>
        """, 
        unsafe_allow_html=True
    )