from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Cargar datos
data = pd.read_csv("datos.csv")

# Página principal (web)
@app.route("/")
def home():
    return render_template("index.html")

# Buscar por cédula desde la web
@app.route("/buscar", methods=["POST"])
def buscar():
    cedula = request.form["cedula"]

    resultado = data[data['Cedula'].astype(str) == cedula]

    if resultado.empty:
        return "<h2>No se encontró la cédula</h2>"

    fila = resultado.iloc[0]

    return f"""
    <h2>Resultado:</h2>
    Nombre: {fila['Nombre']} <br>
    Correo: {fila['Correo']} <br>
    Vacante: {fila['Vacante']} <br>
    Lugar: {fila['Lugar']} <br>
    Hora: {fila['Hora']}
    """

# Endpoint del bot de WhatsApp (NO LO BORRES)
@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form.get("Body")
    print("CÉDULA RECIBIDA:", incoming_msg)

    resultado = data[data['Cedula'].astype(str) == incoming_msg]

    if resultado.empty:
        return "No encontramos tu cédula."

    fila = resultado.iloc[0]

    return f"""Hola {fila['Nombre']} 👋
Tu citación es:
📍 Lugar: {fila['Lugar']}
⏰ Hora: {fila['Hora']}
💼 Vacante: {fila['Vacante']}"""

if __name__ == "__main__":
    app.run(debug=True)