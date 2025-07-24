import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def conexion_gsheet():
    """
    Esta función establece una conexión con Google Sheets usando gspread y las credenciales de un archivo JSON.
    Asegúrate de tener el archivo 'credential_gsheet.json' en la misma carpeta que este script.
    """
    # 1. Definir el 'alcance' (scope) de los permisos
    # Esto le dice a Google qué APIs puede usar nuestra conexión.
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    # 2. Cargar las credenciales desde el archivo JSON
    creds = ServiceAccountCredentials.from_json_keyfile_name("credential_gsheet.json", scope)

    # 3. Autorizar al cliente de gspread
    client = gspread.authorize(creds)

    return client

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