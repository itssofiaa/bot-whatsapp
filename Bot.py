from flask import Flask, request
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Leer Excel
data = pd.read_excel("datos.xlsx")

# Limpiar nombres de columnas (por si vienen raros)
data.columns = data.columns.str.strip()

# Diccionario para guardar estado de usuarios
usuarios = {}

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get('Body', '').strip()
    numero = request.values.get('From', '')

    resp = MessagingResponse()
    msg = resp.message()

    # 🔹 Si el usuario manda SI o NO
    if incoming_msg.lower() in ["si", "sí", "no"]:
        if numero in usuarios:
            cedula = usuarios[numero]

            if incoming_msg.lower() in ["si", "sí"]:
                respuesta = "SI"
                msg.body("✅ Gracias por confirmar tu asistencia. Te esperamos 🙌")
            else:
                respuesta = "NO"
                msg.body("❌ Gracias por informarnos. Tendremos en cuenta tu ausencia.")

            print(f"CÉDULA {cedula} respondió: {respuesta}")

            # Aquí luego guardamos en Excel o Sheets
            return str(resp)
        else:
            msg.body("⚠️ Primero envía tu cédula.")
            return str(resp)

    # 🔹 Si el usuario manda cédula
    cedula = incoming_msg

    # Buscar en Excel
    resultado = data[data['Cedula'].astype(str).str.strip() == cedula]

    if not resultado.empty:
        fila = resultado.iloc[0]

        # Guardar estado
        usuarios[numero] = cedula

        respuesta = f"""
Hola {fila['Nombre']} 👋

📌 Vacante: {fila['Vacante']}
📍 Lugar: {fila['Lugar']}
🕒 Hora: {fila['Hora']}

¿Confirmas asistencia?
Responde SI o NO
"""
        msg.body(respuesta)

    else:
        msg.body("❌ No encontramos tu cédula. Verifica e intenta de nuevo.")

    return str(resp)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)