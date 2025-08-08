# ==============================================================================
# 1. IMPORTACIONES
# ==============================================================================
import streamlit as st
import pandas as pd
from openai import OpenAI

from utils.conn_Gsheet import conexion_gsheet_produccion, abrir_hoja, cargar_datos
from utils.add_informacion import ingresar_gasto, eliminar_gasto, editar_gasto
from utils.func_dash import aplicar_filtros, mostrar_metricas_clave, graficar_distribucion_categoria, graficar_evolucion_temporal, graficar_comparativa_persona, graficar_detalle_subcategoria, mostrar_tabla_detallada
from utils.func_openai import sugerir_categoria_ia, generar_resumen_ia

# ==============================================================================
# DEPURADOR DEFINITIVO DE SECRETOS (Eliminar al finalizar)
# ==============================================================================
st.header("🕵️‍♂️ Depurador Definitivo de Secretos")
if st.button("Revelar Estructura de Secretos"):
    try:
        # Esto imprimirá todo el diccionario de secretos que Streamlit está viendo.
        st.write("Estructura completa de `st.secrets`:")
        st.write(st.secrets.to_dict())

        # Verificación explícita de la clave de OpenAI en el nivel superior
        if "OPENAI_API_KEY" in st.secrets:
            st.success("¡ÉXITO! 'OPENAI_API_KEY' encontrada en el nivel superior.")
        else:
            st.error("¡FALLO! 'OPENAI_API_KEY' NO encontrada en el nivel superior.")

        # Verificación de la clave de OpenAI anidada
        if "gcp_service_account" in st.secrets and "OPENAI_API_KEY" in st.secrets.gcp_service_account:
            st.warning("¡ALERTA! 'OPENAI_API_KEY' fue encontrada ANIDADA dentro de 'gcp_service_account'. ¡Esto es incorrecto!")
        
    except Exception as e:
        st.error(f"Ocurrió un error al intentar leer los secretos: {e}")

st.markdown("---")
# ==============================================================================

# ==============================================================================
# 2. CONFIGURACIÓN DE LA PÁGINA Y CONSTANTES
# ==============================================================================
st.set_page_config(page_title="Gestor de Finanzas", layout="wide", initial_sidebar_state="expanded")

# Definir constantes globales para ser usadas en toda la app
PERSONAS = ["Milagros Valladolid", "Jose Longa"]
CATEGORIAS = ["Comida", "Hogar", "Transporte", "Ocio", "Salud", "Ropa y Calzado", "Tecnología", "Regalos", "Educación", "Deuda", "Otro"]
TIPOS_GASTO = ["Fijo Mensual", "Variable Diario", "Ocasional", "Ahorro/Inversión", "Deuda"]

# ==============================================================================
# 3. INICIALIZACIÓN DE CLIENTES Y CONEXIONES
# ==============================================================================

client_openai = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY")) if st.secrets.get("OPENAI_API_KEY") else None

# --- Conexión a Google Sheets ---
client_gsheet = conexion_gsheet_produccion()
if client_gsheet is None:
    st.error("No se pudo conectar a Google Sheets. La aplicación no puede continuar.")
    st.stop()
#=================================================================
# 4. CUERPO PRINCIPAL DE LA APLICACIÓN
# ==============================================================================

# --- TÍTULO ---
st.title("Nuestro Gestor de Finanzas Familiares 📊")
st.markdown("Una herramienta para registrar y analizar nuestros gastos diarios.")

# --- FORMULARIO DE INGRESO DE GASTOS ---
with st.expander("➕ Añadir un nuevo gasto", expanded=True):
    # Usamos clear_on_submit=False para que la sugerencia de IA no se borre
    with st.form("entry_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            fecha_gasto = st.date_input("Fecha")
            descripcion_gasto = st.text_input("Descripción *", placeholder="Ej: Compra semanal en el supermercado")
        with col2:
            monto_gasto = st.number_input("Monto *", min_value=0.01, format="%.2f")
            persona_gasto = st.radio("Pagado por", PERSONAS)

        # Botón para sugerencia de IA
        if st.form_submit_button("🤖 Sugerir Categoría con IA"):
            if descripcion_gasto and client_openai:
                with st.spinner("Pensando... 🤔"):
                    sugerencia = sugerir_categoria_ia(descripcion_gasto, CATEGORIAS, client_openai)
                    if sugerencia:
                        st.session_state.sugerencia_categoria = sugerencia
            elif not client_openai:
                st.warning("Funcionalidad de IA no disponible. Revisa tu API Key.")
            else:
                st.warning("Escribe una descripción primero.")
        
        # Widget de Categoría que usa la sugerencia del session_state
        indice_sugerido = 0
        sugerencia_guardada = st.session_state.get('sugerencia_categoria')
        if sugerencia_guardada and sugerencia_guardada in CATEGORIAS:
            indice_sugerido = CATEGORIAS.index(sugerencia_guardada)

        categoria_gasto = st.selectbox("Categoría", CATEGORIAS, index=indice_sugerido)
        subcategoria_gasto = st.text_input("Subcategoría (Opcional)", placeholder="Ej: Supermercado, Netflix")
        tipo_gasto_seleccionado = st.selectbox("Tipo de Gasto", TIPOS_GASTO)
        notas_gasto = st.text_area("Notas (Opcional)", placeholder="Añade cualquier detalle extra")
        
        # Botón de envío principal
        submitted_add = st.form_submit_button("✅ Agregar Gasto", type="primary")

# Lógica de envío del formulario
if submitted_add:
    exito, mensaje = ingresar_gasto(worksheet, fecha_gasto, monto_gasto, descripcion_gasto, persona_gasto,
                                    categoria_gasto, subcategoria_gasto, tipo_gasto_seleccionado, notas_gasto)
    if exito:
        st.success(mensaje)
        if 'sugerencia_categoria' in st.session_state:
            del st.session_state.sugerencia_categoria
        st.rerun()
    else:
        st.error(mensaje)


# --- DASHBOARD ---
st.markdown("---")
st.header("Análisis y Visualización de Gastos 📈")

df_original = cargar_datos(worksheet)
if df_original.empty:
    st.info("Aún no hay datos para mostrar. ¡Agrega tu primer gasto para comenzar!")
    st.stop()

# --- Filtros en la barra lateral ---
st.sidebar.header("Filtros del Dashboard")
persona_sel = st.sidebar.selectbox("Filtrar por Persona:", ["Ambos"] + list(df_original['Persona'].unique()))
fecha_sel = st.sidebar.date_input("Filtrar por Rango de Fechas:",
    value=(df_original['Fecha'].min().date(), df_original['Fecha'].max().date()),
    min_value=df_original['Fecha'].min().date(), max_value=df_original['Fecha'].max().date())
categoria_sel = st.sidebar.multiselect("Filtrar por Categoría:",
    options=["Todas"] + list(df_original['Categoria'].unique()), default="Todas")

df_filtrado = aplicar_filtros(df_original, persona_sel, fecha_sel, categoria_sel)

# --- Layout del Dashboard ---
if df_filtrado.empty:
    st.warning("No se encontraron datos para los filtros seleccionados.")
else:
    mostrar_metricas_clave(df_filtrado)
    
    st.subheader("Visión General de Gastos")
    col_dash1, col_dash2 = st.columns(2)
    with col_dash1:
        graficar_distribucion_categoria(df_filtrado)
    with col_dash2:
        graficar_evolucion_temporal(df_filtrado)

    st.markdown("---")
    st.subheader("Análisis Detallado y Gestión")
    
    # --- Pestañas del Dashboard ---
    tabs = st.tabs(["👥 Comparativa", "🌳 Subcategorías", "📄 Tabla", "⚙️ Gestionar Gastos", "🧠 Resumen IA"])
    
    with tabs[0]:
        graficar_comparativa_persona(df_filtrado)
    with tabs[1]:
        graficar_detalle_subcategoria(df_filtrado)
    with tabs[2]:
        mostrar_tabla_detallada(df_filtrado)
    with tabs[3]:
        st.header("Gestionar Gastos Registrados")
        gastos_a_gestionar = df_filtrado.sort_values(by="Fecha", ascending=False).head(20)
        if gastos_a_gestionar.empty:
            st.info("No hay gastos para gestionar en la selección actual.")
        else:
            for _, row in gastos_a_gestionar.iterrows():
                id_gasto = str(row['ID_Gasto'])
                with st.expander(f"📝 {row['Descripcion']} | S/ {row['Monto']:.2f} | 📅 {row['Fecha'].strftime('%d/%m/%Y')}"):
                    with st.form(key=f"edit_form_{id_gasto}"):
                        st.write(f"**Editando Gasto ID:** `{id_gasto}`")
                        
                        form_col1, form_col2 = st.columns(2)
                        with form_col1:
                            nueva_fecha = st.date_input("Fecha", value=row['Fecha'].date(), key=f"date_{id_gasto}")
                            nuevo_monto = st.number_input("Monto", value=float(row['Monto']), format="%.2f", key=f"monto_{id_gasto}")
                            nueva_categoria = st.selectbox("Categoría", CATEGORIAS, index=CATEGORIAS.index(row['Categoria']) if row['Categoria'] in CATEGORIAS else 0, key=f"cat_{id_gasto}")
                        with form_col2:
                            nueva_descripcion = st.text_input("Descripción", value=row['Descripcion'], key=f"desc_{id_gasto}")
                            nueva_subcategoria = st.text_input("Subcategoría", value=row['Subcategoria'], key=f"subcat_{id_gasto}")
                            nueva_persona = st.selectbox("Persona", PERSONAS, index=PERSONAS.index(row['Persona']) if row['Persona'] in PERSONAS else 0, key=f"pers_{id_gasto}")

                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            submitted_edit = st.form_submit_button("💾 Guardar Cambios")
                        with btn_col2:
                            submitted_delete = st.form_submit_button("🗑️ Eliminar Gasto")

                    if submitted_edit:
                        datos_actualizados = {'Fecha': nueva_fecha.strftime('%Y-%m-%d'), 'Monto': nuevo_monto, 'Descripcion': nueva_descripcion,
                                              'Categoria': nueva_categoria, 'Subcategoria': nueva_subcategoria, 'Persona': nueva_persona}
                        exito, mensaje = editar_gasto(worksheet, id_gasto, datos_actualizados)
                        if exito: st.success(mensaje); st.rerun()
                        else: st.error(mensaje)
                    
                    if submitted_delete:
                        exito, mensaje = eliminar_gasto(worksheet, id_gasto)
                        if exito: st.success(mensaje); st.rerun()
                        else: st.error(mensaje)
    
    with tabs[4]:
        st.header("Asistente Financiero con IA")
        st.info("Obtén un análisis y consejos sobre tus gastos para el período seleccionado.")
        
        if not client_openai:
            st.warning("La funcionalidad de IA no está disponible. Revisa tu API Key de OpenAI.")
        else:
            if st.button("💡 Generar Resumen y Consejos", type="primary"):
                with st.spinner("Analizando tus finanzas... ⏳"):
                    resumen = generar_resumen_ia(df_filtrado, client_openai)
                    with st.container(border=True):
                        st.markdown(resumen)