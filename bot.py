from flask import Flask, request, render_template
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Leer archivo CSV
data = pd.read_csv("datos.csv", dtype=str)

# Limpiar nombres de columnas (por si hay espacios o caracteres raros)
data.columns = data.columns.str.strip()

print("COLUMNAS DETECTADAS:")
print(data.columns)

# =========================
# 🌐 RUTA WEB (Render)
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    resultado = None

    if request.method == "POST":
        cedula = request.form.get("cedula").strip()

        resultado_df = data[data['Cedula'].str.strip() == cedula]

        if not resultado_df.empty:
            resultado = resultado_df.iloc[0]

    return render_template("index.html", resultado=resultado)


# =========================
# 📲 RUTA WHATSAPP (Twilio)
# =========================
@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get('Body', '').strip()

    print("CÉDULA RECIBIDA:", incoming_msg)

    resultado = data[data['Cedula'].str.strip() == incoming_msg]

    resp = MessagingResponse()

    if not resultado.empty:
        fila = resultado.iloc[0]

        mensaje = f"""
Hola {fila['Nombre']} 👋

📌 Vacante: {fila['Vacante']}
📍 Lugar: {fila['Lugar']}
⏰ Hora: {fila['Hora']}

Por favor responde:
👉 SI para confirmar asistencia
👉 NO si no asistirás
"""
    else:
        mensaje = "❌ No encontramos tu cédula. Verifica e intenta nuevamente."

    resp.message(mensaje)
    return str(resp)


# =========================
# 🚀 INICIO APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)