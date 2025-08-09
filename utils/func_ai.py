import streamlit as st
import google.generativeai as genai

# --- NUEVA FUNCIÓN PARA INICIALIZAR EL CLIENTE ---
def inicializar_cliente_ia():
    """Inicializa el cliente de Google Gemini si la clave existe."""
    try:
        api_key = st.secrets.google_ai.api_key
        genai.configure(api_key=api_key)
        # Seleccionamos el modelo que vamos a usar
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except (AttributeError, KeyError):
        # Si st.secrets.google_ai.api_key no existe
        return None
    except Exception as e:
        st.write(f"Error al configurar la API de Google Gemini: {e}")
        return None
    
# --- FUNCIONES DE IA ACTUALIZADAS ---
def sugerir_categoria_ia(descripcion, categorias_posibles, model):
    """Usa Gemini para sugerir una categoría."""
    if not model:
        return None

    prompt = f"""Dada la descripción de un gasto: "{descripcion}", ¿cuál de estas categorías es la más apropiada? Categorías disponibles: {', '.join(categorias_posibles)}. Responde únicamente con el nombre exacto de la categoría. Si ninguna encaja, responde 'Otro'."""
    try:
        response = model.generate_content(prompt)
        sugerencia = response.text.strip()
        return sugerencia if sugerencia in categorias_posibles else "Otro"
    except Exception as e:
        st.write(f"Error al llamar a la API de Gemini para sugerir categoría: {e}")
        return None


def generar_resumen_ia(df_filtrado, model):
    """Usa Gemini para generar un resumen financiero."""
    if not model:
        return "La funcionalidad de IA no está disponible."
    if df_filtrado.empty:
        return "No hay datos suficientes para generar un resumen."

    # 1. Calcular métricas clave con Pandas
    gasto_total = df_filtrado['Monto'].sum()
    gastos_por_categoria = df_filtrado.groupby('Categoria')['Monto'].sum().sort_values(ascending=False)
    categoria_mayor_gasto = gastos_por_categoria.index[0]
    monto_mayor_gasto = gastos_por_categoria.iloc[0]

    # 2. Construir el prompt para la IA
    prompt = f"""
    Actúa como un asesor financiero personal amigable y constructivo para una pareja. Analiza los siguientes datos de gastos del período seleccionado:

    - Gasto Total: ${gasto_total:,.2f}
    - La categoría con el mayor gasto fue '{categoria_mayor_gasto}' con un total de ${monto_mayor_gasto:,.2f}.
    - Desglose de gastos por categoría:
    {gastos_por_categoria.to_string()}

    Basado en esta información, escribe un breve resumen financiero (máximo 3 párrafos). Tu resumen debe incluir:
    1. Un punto positivo o un logro evidente en sus finanzas.
    2. Un área principal donde podrían enfocarse para mejorar o reducir gastos.
    3. Un consejo práctico y accionable para el próximo período.

    Usa un tono positivo, motivador y evita el lenguaje técnico. Dirígete a ellos como "ustedes".
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.write(f"Error al llamar a la API de Gemini para generar resumen: {e}")
        return "Ocurrió un error al intentar generar el resumen."
    