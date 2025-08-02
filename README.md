# Gestor Financiero Avanzado para Parejas 📊

<!-- Reemplaza el enlace con una captura de pantalla de tu dashboard finalizado -->
 

Herramienta completa para la gestión de finanzas personales en pareja, construida con Python y Streamlit. Permite un registro detallado de gastos y ofrece un dashboard interactivo para un análisis profundo, con toda la información centralizada en Google Sheets.

**[➡️ Ver la aplicación en vivo]** <!-- <img width="1040" height="1707" alt="image" src="https://github.com/user-attachments/assets/479c4943-ea74-424a-9d69-90a3cc965450" />
-->

---

## ✨ Características

*   **Gestión CRUD Completa:** Permite **C**rear, **L**eer, **A**ctualizar y **E**liminar (CRUD) gastos de forma intuitiva.
*   **Formulario de Ingreso Detallado:** Añade nuevos gastos con campos para fecha, descripción, monto, categoría, subcategoría, persona y notas.
*   **Dashboard Interactivo:**
    *   **KPIs Principales:** Visión general inmediata del gasto total, número de transacciones y promedio.
    *   **Gráficos Dinámicos:** Gráfico de torta para la distribución por categoría y gráfico de líneas para la evolución temporal.
    *   **Análisis en Pestañas:** Desglose por persona, análisis por subcategoría (Treemap) y tabla de datos completa.
*   **Edición y Eliminación Segura:** Interfaz dedicada para modificar o eliminar registros con pasos de confirmación para evitar errores.
*   **Filtros Globales:** Filtra todo el dashboard por rango de fechas, persona o categoría para análisis específicos.
*   **Base de Datos en la Nube:** Utiliza Google Sheets como una base de datos gratuita y accesible.
*   **Despliegue Seguro:** Configurado para un despliegue seguro en Streamlit Community Cloud, protegiendo las credenciales con `st.secrets`.

---

## 🛠️ Arquitectura y Desglose de Funciones

El proyecto está modularizado para ser escalable y fácil de mantener. Cada función tiene una única responsabilidad.

### Funciones de Backend (Manejo de Datos)

*   `conexion_gsheet_produccion()`: Establece la conexión segura con la API de Google Sheets utilizando las credenciales almacenadas en los secretos de Streamlit. Está diseñada para el entorno de producción.
*   `ingresar_gasto(...)`: Toma los datos de un nuevo gasto desde el formulario y los añade como una nueva fila en la hoja de cálculo.
*   `editar_gasto(...)`: Busca una fila existente por su `ID_Gasto`, recibe un diccionario con los nuevos datos y actualiza las celdas correspondientes de forma eficiente (en lote).
*   `eliminar_gasto(...)`: Busca una fila por su `ID_Gasto` y la elimina por completo de la hoja de cálculo.

### Funciones de Frontend y Lógica del Dashboard

*   `cargar_datos(...)`: Lee todos los registros de Google Sheets, los convierte en un DataFrame de Pandas, limpia los datos (convierte tipos, maneja valores nulos) y fuerza que `ID_Gasto` sea un string. Utiliza `@st.cache_data` para mejorar el rendimiento.
*   `aplicar_filtros(...)`: Recibe el DataFrame principal y las selecciones del usuario en la barra lateral, y devuelve un nuevo DataFrame filtrado que se usará en todas las visualizaciones.
*   `mostrar_metricas_clave(...)`: Calcula y muestra los KPIs (Gasto Total, etc.) en la parte superior del dashboard.
*   `graficar_* (...)`: Cada una de las funciones `graficar_distribucion_categoria`, `graficar_evolucion_temporal`, etc., se especializa en crear y mostrar un gráfico específico usando Plotly, a partir del DataFrame filtrado.

---

## 🚀 Guía de Configuración y Despliegue (Desde Cero)

Sigue estos pasos para poner en marcha tu propia versión de la aplicación.

### **Paso 1: Configuración de Google Sheets (La Base de Datos)**

1.  **Crear la Hoja de Cálculo:**
    *   Ve a [Google Sheets](https://sheets.google.com) y crea una nueva hoja de cálculo.
    *   Nómbrala exactamente `Finanzas Familiares`.

2.  **Definir las Columnas:**
    *   En la primera fila de la primera hoja (normalmente `Hoja 1`), crea las siguientes columnas en este orden exacto. El nombre debe ser idéntico.

| A | B | C | D | E | F | G | H | I |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ID_Gasto` | `Fecha` | `Monto`| `Descripción` | `Persona` | `Categoría` | `Subcategoría` | `Tipo de Gasto` | `Notas` |

### **Paso 2: Configuración de Google Cloud (Permisos y Credenciales)**

1.  **Crear un Proyecto y Habilitar APIs:**
    *   Ve a la [Consola de Google Cloud](https://console.cloud.google.com/).
    *   Crea un nuevo proyecto (ej. "App Finanzas Streamlit").
    *   En el buscador, busca y habilita las siguientes dos APIs: **"Google Drive API"** y **"Google Sheets API"**.

2.  **Crear una Cuenta de Servicio y Clave JSON:**
    *   En el menú de navegación, ve a `APIs y servicios > Credenciales`.
    *   Haz clic en `+ CREAR CREDENCIALES` y selecciona `Cuenta de servicio`.
    *   Dale un nombre (ej. `streamlit-finanzas-bot`) y haz clic en `CREAR Y CONTINUAR`.
    *   En "Rol", busca y selecciona `Editor`. Haz clic en `CONTINUAR` y luego en `LISTO`.
    *   Serás devuelto a la pantalla de credenciales. Haz clic en el email de la cuenta de servicio que acabas de crear.
    *   Ve a la pestaña `CLAVES`, haz clic en `AGREGAR CLAVE` > `Crear nueva clave`.
    *   Selecciona `JSON` y haz clic en `CREAR`. Un archivo `.json` se descargará automáticamente. **Guarda este archivo, es tu contraseña.**

### **Paso 3: Conceder Permisos a la Hoja de Cálculo**

1.  Abre el archivo `.json` que descargaste. Busca y copia el valor de `client_email`. Se verá algo así: `streamlit-finanzas-bot@tu-proyecto.iam.gserviceaccount.com`.
2.  Vuelve a tu hoja de Google Sheets, haz clic en el botón `Compartir` (arriba a la derecha).
3.  Pega el `client_email` en el campo para añadir personas, asegúrate de que tenga el rol de **Editor** y haz clic en `Enviar`.

### **Paso 4: Preparar el Repositorio para el Despliegue**

1.  **Clona este repositorio o crea el tuyo:**
    ```bash
    git clone https://github.com/[tu-usuario]/[tu-repositorio].git
    cd [tu-repositorio]
    ```

2.  **Crea el archivo `requirements.txt`:**
    Este archivo le dice a Streamlit qué librerías instalar. Debe contener:
    ```txt
    streamlit
    pandas
    gspread
    oauth2client
    plotly
    ```


3.  **Sube tu código a GitHub:**
    Añade todos tus archivos (`app.py`, `requirements.txt`, `.gitignore`, `README.md`) y súbelos a tu repositorio de GitHub.

### **Paso 5: Despliegue en Streamlit Community Cloud**

1.  Ve a [share.streamlit.io](https://share.streamlit.io/) e inicia sesión con tu cuenta de GitHub.
2.  Haz clic en `New app` y selecciona tu repositorio.
3.  Antes de desplegar, haz clic en `Advanced settings...`.
4.  Ve a la sección `Secrets`. Aquí copiarás el contenido de tu archivo `.json` de credenciales, pero con formato TOML:

    ```toml
    [gcp_service_account]
    type = "service_account"
    project_id = "tu-project-id"
    private_key_id = "tu-private-key-id"
    private_key = "-----BEGIN PRIVATE KEY-----\n...todo el contenido...\n-----END PRIVATE KEY-----\n"
    client_email = "tu-client-email@..."
    client_id = "tu-client-id"
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
    client_x509_cert_url = "https://www.googleapis.com/..."
    ```
5.  Haz clic en `Save` y luego en `Deploy!`. ¡Tu aplicación estará en línea y funcionando en minutos!

---

## 🔮 Roadmap de Futuras Mejoras

*   [ ] **Gestión de Presupuestos:** Definir límites de gasto por categoría y visualizar el progreso.
*   [ ] **Categorización con IA:** Sugerir categorías automáticamente a partir de la descripción del gasto.
*   [ ] **Autenticación de Usuarios:** Añadir un sistema de login para que solo tú y tu esposa puedan acceder.
*   [ ] **Soporte Multimoneda:** Para registrar gastos en diferentes divisas.

---

## 📜 Licencia

Este proyecto está distribuido bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
