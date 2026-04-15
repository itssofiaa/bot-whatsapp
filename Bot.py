from flask import Flask, request
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# 🔥 Detectar separador automáticamente
try:
    data = pd.read_csv("datos.csv", dtype=str, sep=None, engine='python')
except:
    data = pd.read_csv("datos.csv", dtype=str)

# Limpiar nombres de columnas
data.columns = data.columns.str.strip()

print("COLUMNAS DETECTADAS:")
print(data.columns)

# Detectar columna de cédula (la que contenga 'cedula')
columna_cedula = None
for col in data.columns:
    if "cedula" in col.lower():
        columna_cedula = col
        break

# Si no la encuentra, usa la primera
if columna_cedula is None:
    columna_cedula = data.columns[0]

print("COLUMNA USADA PARA CÉDULA:", columna_cedula)

# Limpiar cédulas del archivo
data[columna_cedula] = data[columna_cedula].astype(str)
data[columna_cedula] = data[columna_cedula].str.replace(".", "", regex=False)
data[columna_cedula] = data[columna_cedula].str.replace(",", "", regex=False)
data[columna_cedula] = data[columna_cedula].str.replace(" ", "", regex=False)
data[columna_cedula] = data[columna_cedula].str.strip()

print("CÉDULAS EN EL ARCHIVO:")
print(data[columna_cedula].head(10))

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip()
    
    respuesta = MessagingResponse()
    msg = respuesta.message()

    # Limpiar cédula del usuario
    cedula_usuario = incoming_msg.replace(".", "").replace(",", "").replace(" ", "").strip()

    print("CÉDULA RECIBIDA:", cedula_usuario)

    # Buscar
    resultado = data[data[columna_cedula] == cedula_usuario]

    if not resultado.empty:
        fila = resultado.iloc[0]
        reply = f"""Hola 👋
📍 Lugar: {fila.get('Lugar', 'No disponible')}
🕒 Citación: {fila.get('Hora', fila.get('Fecha y hora', 'No disponible'))}
💼 Vacante: {fila.get('Vacante', 'No disponible')}"""
    else:
        reply = "❌ No encontramos tu cédula. Verifica e intenta nuevamente."

    msg.body(reply)
    return str(respuesta)

if __name__ == "__main__":
    app.run(port=5000)