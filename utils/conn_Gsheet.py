import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

def conexion_gsheet_produccion():
    """
    Establece conexión con Google Sheets usando los Secretos de Streamlit.
    Esta función está diseñada para ser usada exclusivamente en un entorno
    desplegado en Streamlit Community Cloud.
    """
    # 1. Definir el alcance de los permisos
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    try:
        # 2. Cargar las credenciales directamente desde los secretos de Streamlit
        # st.secrets es un diccionario especial que contiene lo que configuraste en la nube.
        creds_dict = st.secrets["gcp_service_account"]
        
        # 3. Autorizar usando el diccionario de credenciales
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        return client
        
    except KeyError:
        # Este error ocurre si la sección [gcp_service_account] no está en los secretos.
        st.error("Error de configuración: La sección [gcp_service_account] no se encontró en los secretos de Streamlit.")
        st.info("Asegúrate de haber configurado correctamente los secretos en tu dashboard de Streamlit Community Cloud.")
        return None
    except Exception as e:
        # Captura cualquier otro error durante la autorización
        st.error(f"No se pudo conectar a Google Sheets. Error inesperado: {e}")
        return None

def abrir_hoja(client):
    """
    Abre una hoja de cálculo específica y devuelve el objeto de la hoja.
    Asegúrate de que el nombre de la hoja sea correcto.
    """
    spreadsheet = client.open("FinanzasFamiliares")  # Cambia por el nombre de tu hoja
    worksheet = spreadsheet.worksheet("Hoja 1")  # Cambia por el nombre de la pestaña que usarás
    return worksheet

def cargar_datos(worksheet):
    """
    Carga los datos de la hoja de cálculo en un DataFrame de Pandas.
    """
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    # Convertir tipos de datos
    if not df.empty:
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df.dropna(subset=['Fecha'], inplace=True)
    return df