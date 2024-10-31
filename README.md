Descripción del Proyecto
Para este proyecto, desarrollaremos una aplicación web con Streamlit para analizar el mercado
inmobiliario español, utilizando pisos.com como fuente principal de datos. Crearemos una base
de datos para almacenar eficientemente la información extraída y diseñaremos un proceso ETL
para mantenerla actualizada.
La aplicación se dividirá en dos secciones principales:
● Vista para usuarios.
● Vista para cliente.
Vista para Usuarios
Esta sección estará orientada al público en general y ofrecerá las siguientes funcionalidades:
● Mapa interactivo: Visualización geográfica de los inmuebles, permitiendo filtrar por
zonas.
● Tabla de datos: Presentación detallada de los inmuebles en formato tabular.
● Dashboard: Visualizaciones interactivas (gráficos, tablas) que muestren variables
relevantes como precios, superficies, etc.
● Ficha detallada: Información específica de cada inmueble.
● Comparador: Herramienta para comparar múltiples propiedades y tomar decisiones
informadas.
Vista para Clientes
Esta sección estará dirigida a un público más especializado y ofrecerá:
● Dashboard en PowerBI: Visualizaciones personalizadas de KPIs clave para el negocio
inmobiliario.
● Esquema de la base de datos: Representación visual de la estructura de la base de
datos para facilitar la comprensión.
Funcionalidades de la página web
● Navegación: Implementar filtros, búsqueda y paginación para facilitar la exploración de
los datos.
● Actualización: Garantizar que los dashboards estén actualizados con los datos más
recientes.
Objetivos del Proyecto
● Desarrollar una herramienta que pueda ser utilizada por usuarios y clientes interesados
en el mercado inmobiliario

---

pisos.com - SPRINT I
Parte 1 - Extracción de Datos
● Navegar la web de pisos.com y entender su estructura.
● Desarrollar un script que recorra las publicaciones de compra y venta, y extraiga los
contenidos necesarios para la aplicación.
● Desarrollar otro script que recorra las publicaciones de alquiler, y extraiga los
contenidos necesarios para la aplicación.
● Ejecutar los scripts con una muestra relativamente pequeña de publicaciones y
verificar que todo funcione correctamente.
Parte 2 - Limpieza y EDA inicial
● Hacer limpieza general de datos (si aplica)
● Modelar los datos para trabajar cómodamente para poder cargarlos en una base de
datos. La base de datos que van a utilizar queda a vuestro criterio.
● En el modelo de datos, cada registro debe tener un timestamp de scrapeo y un
identificador para que se pueda manejar el sistema de actualización.
● Ejecutar los scripts de recopilación de datos, aplicándoles la limpieza y
transformaciones de modelado correspondientes.
● Estudiar cómo se relacionan las diferentes variables entre sí.
● Hacer una segmentación del mercado y buscar un grupo de inmuebles con el mejor
ratio entre precio de compra y precio de alquiler.
● Preparar un dashboard usando plotly exponiendo los resultados del análisis de
segmentación.
Parte 3 - Base de Datos
● Definir una estructura de bases de datos.
● Realizar un script para popular la base de datos.
● Realizar un script para extraer datos mediante queries.
Parte 4 - Streamlit
● Preparar la estructura del proyecto (carpetas, entorno virtual, dependencias, etc.)
● Preparar un archivo .env o un st.secrets para almacenar información sensible como
usuario y contraseña de la base de datos.
● Preparar la configuración general de Streamlit.
● Definir la paginación y las secciones principales
○ Las vista principal (landing page).
○ La vista de presentación de datos (filtros, mapa, dashboard, etc.)
○ La vista detallada donde se puede buscar un inmueble y compararlo.
● Montar placeholders para las visualizaciones, media y el texto que se vaya a incluir
en cada una de las vistas

---
