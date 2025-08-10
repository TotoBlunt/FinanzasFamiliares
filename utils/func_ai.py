import streamlit as st
import google.generativeai as genai
import pandas as pd

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
    
def generar_insights_proactivos(df, ia_model):
    """
    Analiza el DataFrame para encontrar patrones y genera insights con IA.
    """
    if not ia_model: return [] # Devuelve una lista vacía si no hay IA
    if df.empty or len(df) < 10: # Necesitamos un mínimo de datos para encontrar patrones
        return ["No hay suficientes datos para generar insights. ¡Sigue registrando gastos!"]

    insights_preparados = []

    # --- Insight 1: Gasto por Día de la Semana ---
    df['Dia_Semana'] = df['Fecha'].dt.day_name()
    gastos_por_dia = df.groupby('Dia_Semana')['Monto'].sum().sort_values(ascending=False)
    # Reordenar por día de la semana para una mejor lógica
    dias_ordenados = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    gastos_por_dia = gastos_por_dia.reindex(dias_ordenados).dropna()
    
    if not gastos_por_dia.empty:
        dia_mayor_gasto = gastos_por_dia.idxmax()
        monto_dia_mayor = gastos_por_dia.max()
        insights_preparados.append(f"El día de la semana con mayor gasto es el {dia_mayor_gasto} con un total de ${monto_dia_mayor:,.2f}.")

    # --- Insight 2: Categoría con Mayor Gasto ---
    gastos_por_categoria = df.groupby('Categoria')['Monto'].sum().sort_values(ascending=False)
    if not gastos_por_categoria.empty:
        cat_mayor_gasto = gastos_por_categoria.index[0]
        monto_cat_mayor = gastos_por_categoria.iloc[0]
        porcentaje_total = (monto_cat_mayor / df['Monto'].sum()) * 100
        insights_preparados.append(f"La categoría '{cat_mayor_gasto}' representa el {porcentaje_total:.1f}% de sus gastos totales en este período.")

    # --- Insight 3: Detección de Gasto Grande Inusual ---
    gasto_mas_caro = df.loc[df['Monto'].idxmax()]
    promedio_gasto = df['Monto'].mean()
    # Si el gasto más caro es 5 veces más grande que el promedio, es un insight interesante.
    if gasto_mas_caro['Monto'] > promedio_gasto * 5:
        insights_preparados.append(f"Se detectó un gasto significativamente grande de ${gasto_mas_caro['Monto']:,.2f} en '{gasto_mas_caro['Descripcion']}' en la categoría '{gasto_mas_caro['Categoria']}'.")
        
    # --- Ahora, pasamos estos insights a la IA para que los reformule ---
    if not insights_preparados:
        return ["No se encontraron patrones destacables en este período."]

    insights_texto = "\n- ".join(insights_preparados)
    
    prompt = f"""
    Actúa como un asistente financiero observador e inteligente. A continuación, se presentan algunos datos y patrones extraídos de los gastos de una pareja:

    Datos extraídos:
    - {insights_texto}

    Tu tarea es seleccionar los TRES insights más interesantes o útiles de esta lista y reescribirlos como tres frases cortas, amigables y fáciles de entender. Cada frase debe empezar con un emoji apropiado.
    
    Ejemplo de formato:
    - 💡 ¿Sabías que los sábados son su día de mayor gasto? ¡Parece que disfrutan el fin de semana!
    - 🍽️ El mayor porcentaje de sus gastos se destina a la categoría 'Comida', representando casi la mitad de su presupuesto.

    No añadas introducciones ni conclusiones, solo las tres frases. Separa cada frase con un salto de línea.
    """
    
    try:
        response = ia_model.generate_content(prompt)
        # Dividimos la respuesta de la IA en una lista de insights
        insights_finales = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        return insights_finales
    except Exception as e:
        st.write(f"Error al generar insights proactivos con IA: {e}")
        return ["Ocurrió un error al analizar las tendencias."]

def responder_pregunta_financiera(pregunta_usuario, df, ia_model):
    """
    Procesa una pregunta en lenguaje natural, la convierte a código pandas,
    la ejecuta y devuelve una respuesta en lenguaje natural.
    """
    if not ia_model: return "La funcionalidad de IA no está disponible."
    if df.empty: return "No hay datos disponibles para responder preguntas."

    # Preparamos información sobre el DataFrame para darle contexto a la IA
    columnas = df.columns.tolist()
    tipos_de_datos = df.dtypes.to_string()
    
    # --- PASO 1: Generar el código Pandas ---
    prompt_generar_codigo = f"""
    Actúa como un experto en Python y la librería Pandas. Tu tarea es convertir una pregunta del usuario en código Pandas ejecutable.
    
    El DataFrame se llama `df` y tiene las siguientes columnas: {df.columns.tolist()}
    Los tipos de datos de las columnas son:
    {df.dtypes.to_string()}
    
    La pregunta del usuario es: "{pregunta_usuario}"
    
    Escribe el código de Python Pandas que calcule la respuesta.
    - El resultado final debe ser almacenado en una variable llamada `resultado`.
    - No incluyas la importación de pandas.
    - Responde únicamente con el bloque de código. No añadas explicaciones ni ```python.
    """
    
    try:
        response_codigo = ia_model.generate_content(prompt_generar_codigo)
        codigo_generado = response_codigo.text.strip()
    except Exception as e:
        st.write(f"Error al generar código: {e}")
        return "Tuve un problema al intentar entender tu pregunta. ¿Podrías reformularla?"
        
    # ==========================================================
    # <<<<<<<<<<<<<<<    NUEVO PASO DE LIMPIEZA    >>>>>>>>>>>>>>>>>
    # ==========================================================
    # Eliminamos cualquier línea que intente importar librerías o que sea un comentario de markdown.
    lineas_limpias = []
    for linea in codigo_generado.split('\n'):
        if not linea.strip().startswith('import ') and not linea.strip().startswith('```'):
            lineas_limpias.append(linea)
    codigo_limpio = "\n".join(lineas_limpias)
    # ==========================================================
        
    # --- PASO 2: Ejecutar el código de forma segura ---
    resultado_ejecucion = None
    try:
        # Usamos el CÓDIGO LIMPIO para la ejecución
        local_scope = {'df': df, 'pd': pd} # <-- AÑADIMOS 'pd' AL ENTORNO
        exec(codigo_limpio, {}, local_scope)
        resultado_ejecucion = local_scope.get('resultado', 'No se encontró la variable resultado.')
    except Exception as e:
        st.write(f"Error al ejecutar código: {e}\nCódigo problemático (limpio):\n{codigo_limpio}")
        return f"No pude procesar tu solicitud. Parece que la pregunta generó un cálculo inválido."

    # --- PASO 3: Interpretar el resultado y generar respuesta final ---
    prompt_interpretar_resultado = f"""
    Eres un asistente financiero amigable. Un usuario hizo la siguiente pregunta: "{pregunta_usuario}"
    
    Para responder, se ejecutó un cálculo que dio el siguiente resultado:
    {str(resultado_ejecucion)}
    
    Tu tarea es presentar este resultado al usuario de una manera clara, concisa y en lenguaje natural.
    - Si el resultado es un número, formatéalo como moneda si es apropiado.
    - Si es una tabla, preséntala de forma resumida.
    - Si es un error, explícalo de forma sencilla.
    - Sé breve y directo en tu respuesta.
    """
    
    try:
        response_final = ia_model.generate_content(prompt_interpretar_resultado)
        return response_final.text.strip()
    except Exception as e:
        st.write(f"Error al interpretar resultado: {e}")
        return f"El resultado del cálculo fue: {str(resultado_ejecucion)}, pero tuve problemas para explicarlo."