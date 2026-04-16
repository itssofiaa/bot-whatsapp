from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Leer archivo
data = pd.read_csv("datos.csv")

# Limpiar nombres de columnas
data.columns = data.columns.str.strip()

# Ruta principal (ESTO ES LO QUE TE FALTA)
@app.route("/")
def home():
    return render_template("index.html")


# Ruta para consultar
@app.route("/consultar", methods=["POST"])
def consultar():
    cedula = request.form.get("cedula")

    resultado = data[data["Cedula"].astype(str) == str(cedula)]

    if resultado.empty:
        return "❌ No se encontró la cédula"

    fila = resultado.iloc[0]

    return f"""
    ✅ Nombre: {fila['Nombre']}<br>
    📍 Lugar: {fila['Lugar']}<br>
    🕒 Hora: {fila['Hora']}<br>
    💼 Vacante: {fila['Vacante']}
    """


if __name__ == "__main__":
    app.run()