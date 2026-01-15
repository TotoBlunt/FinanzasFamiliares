# Asistente Financiero Inteligente para Parejas 🤖📊

 <img width="1062" height="1673" alt="Captura de pantalla 2025-08-09 222651" src="https://github.com/user-attachments/assets/5a8c33f7-6a40-48be-9b40-503213521998" />


Una aplicación web avanzada, construida con Streamlit y Python, diseñada para transformar la gestión de finanzas en pareja. No solo registra y visualiza gastos, sino que utiliza **Inteligencia Artificial (Google Gemini)** para actuar como un verdadero asistente financiero, ofreciendo insights, resúmenes y una interfaz de chat para dialogar con tus datos.

**[➡️ Ver la aplicación en vivo]** [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://finanzasfamiliares.streamlit.app/)

---

## ✨ Características Principales

*   **Gestión de Gastos Completa (CRUD):** Permite **C**rear, **L**eer, **A**ctualizar y **E**liminar gastos de forma segura e intuitiva.
*   **Base de Datos en la Nube:** Utiliza Google Sheets como backend, garantizando accesibilidad y coste cero.
*   **Dashboard Interactivo:** Un centro de control visual con filtros potentes para analizar los datos por persona, fecha y categoría.

### 🚀 Funcionalidades Potenciadas por IA

*   **Categorización Asistida:** Al ingresar un gasto, la IA sugiere la categoría más probable basándose en la descripción, agilizando el proceso.
*   **💡 Insights Proactivos:** La aplicación analiza tus patrones de gasto y presenta "tarjetas de información" con tendencias y observaciones interesantes que podrías haber pasado por alto.
*   **🧠 Resúmenes Inteligentes:** Genera resúmenes en lenguaje natural sobre tu salud financiera en un período, destacando aciertos, áreas de mejora y consejos prácticos.
*   **💬 Chat con tus Finanzas:** ¡Habla con tus datos! Una interfaz de chat te permite hacer preguntas en español como `"¿Cuánto gastamos en restaurantes el mes pasado?"` y recibir respuestas instantáneas.

---

## 🛠️ Arquitectura del Proyecto

El proyecto está diseñado de forma modular para garantizar su mantenimiento y escalabilidad.

*   **`app.py`:** Orquesta la interfaz de usuario (UI) y el flujo de la aplicación.
*   **`utils/`:** Una carpeta que contiene la lógica de negocio separada:
    *   `conn_Gsheet.py`: Gestiona la conexión segura a Google Sheets.
    *   `add_informacion.py`: Contiene las funciones CRUD (ingresar, editar, eliminar).
    *   `func_dash.py`: Alberga las funciones que generan los gráficos y métricas del dashboard.
    *   `func_ai.py`: Contiene toda la lógica para interactuar con la API de Google Gemini, incluyendo la generación de código y la interpretación de resultados.

---

## 🚀 Guía de Configuración y Despliegue

Sigue estos pasos para poner en marcha tu propia versión de la aplicación.

### **Paso 1: Configuración de Google Sheets (Base de Datos)**

1.  **Crear Hoja:** Ve a [Google Sheets](https://sheets.google.com) y crea una hoja llamada `Finanzas Familiares`.
2.  **Definir Columnas:** En la primera fila, crea las siguientes columnas en este orden: `ID_Gasto`, `Fecha`, `Monto`, `Descripcion`, `Persona`, `Categoria`, `Subcategoria`, `Tipo de Gasto`, `Notas`.

### **Paso 2: Configuración de Google Cloud (Permisos para Google Sheets)**

1.  **Habilitar APIs:** En la [Consola de Google Cloud](https://console.cloud.google.com/), crea un proyecto y habilita la **"Google Drive API"** y la **"Google Sheets API"**.
2.  **Crear Cuenta de Servicio:** En `Credenciales`, crea una `Cuenta de servicio` con el rol de `Editor`. Descarga la clave en formato `JSON`.
3.  **Compartir Hoja:** Abre tu hoja de Google Sheets, haz clic en `Compartir` y añade el email de la cuenta de servicio (`client_email` del archivo JSON) como "Editor".

### **Paso 3: Configuración de Google AI Studio (API de Gemini)**

1.  **Obtener Clave de API:** Ve a [Google AI Studio](https://aistudio.google.com/), inicia sesión y haz clic en `Get API key` > `Create API key in new project`.
2.  **Copia tu nueva clave de API.** La necesitarás para los secretos.

### **Paso 4: Preparar y Desplegar en Streamlit Cloud**

1.  **Clona el repositorio** y asegúrate de tener los archivos `app.py`, `requirements.txt` y la carpeta `utils`.
2.  **Configura tus Secretos:** En tu dashboard de Streamlit Cloud, ve a `Settings` > `Secrets` de tu app y pega el siguiente contenido, reemplazando los valores con tus credenciales.

    ```toml
    # secrets.toml

    # --- Sección de Google Cloud para Google Sheets ---
    [gcp_service_account]
    type = "service_account"
    project_id = "tu-project-id"
    # ... (pega aquí el resto de tu JSON de la cuenta de servicio) ...

    # --- Sección de Google AI para Gemini ---
    [google_ai]
    api_key = "PEGA-AQUI-TU-CLAVE-DE-GEMINI"
    ```
3.  **Despliega la aplicación.** Streamlit se encargará de instalar las dependencias y ejecutar la app.

---

## 💰 Costes y Límites de la API de IA (Google Gemini)

Esta aplicación utiliza la API de Google Gemini, que tiene una estructura de precios muy asequible y un generoso nivel gratuito.

### Límites del Nivel Gratuito (Sin Facturación Habilitada)

*   **Límite Diario:** **50 solicitudes por día** para el modelo `gemini-1.5-flash`.
*   **Importante:** Cada pregunta en la función de "Chat con tus Gastos" consume **2 solicitudes** (una para generar el código y otra para interpretar la respuesta). Por lo tanto, el límite diario es de aproximadamente **25 preguntas de chat**.
*   Si alcanzas este límite, recibirás un error `Error 429: Quota exceeded` y deberás esperar 24 horas para que se reinicie.

### Uso con Facturación Habilitada (Recomendado)

Para un uso sin interrupciones, se recomienda habilitar la facturación en tu proyecto de Google Cloud.

*   **¿Significa que pagaré?** No necesariamente. Habilitar la facturación te da acceso a un **nivel gratuito mucho más grande** antes de empezar a pagar.
*   **Costes Reales:** El modelo `gemini-1.5-flash` es extremadamente barato. El coste se mide por cada 1,000,000 de tokens (un token es ~¾ de una palabra).
    *   **Entrada (tus prompts):** ~$0.35 por millón de tokens.
    *   **Salida (respuestas de la IA):** ~$1.05 por millón de tokens.
*   **Estimación Práctica:** Con un uso intensivo (cientos de interacciones de chat y resúmenes al mes), el coste mensual probablemente será de **unos pocos céntimos o, como mucho, un par de dólares**. Un presupuesto de $5 al mes es más que suficiente para un uso sin preocupaciones.

---

## 🔮 Roadmap de Futuras Mejoras

*   [ ] **Autenticación de Usuarios:** Implementar un sistema de login para una experiencia personalizada.
*   [ ] **Gestión de Presupuestos:** Definir presupuestos por categoría y visualizar el progreso.
*   [ ] **Notificaciones:** Enviar resúmenes o alertas a través de Telegram o email.
*   [ ] **Soporte Multilenguaje:** Adaptar la aplicación para otros idiomas.

---

## 📜 Licencia

Este proyecto está distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
