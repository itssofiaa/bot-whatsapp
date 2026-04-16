from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# 🔥 LEER CSV CON TABULADOR
data = pd.read_csv("datos.csv", sep="\t")

# Limpiar nombres de columnas
data.columns = data.columns.str.strip()

print("COLUMNAS DISPONIBLES:")
print(data.columns)

# Detectar columna de cédula
col_cedula = None
for col in data.columns:
    if "cedula" in col.lower():
        col_cedula = col
        break

print("COLUMNA DE CÉDULA USADA:", col_cedula)


def limpiar_cedula(valor):
    return ''.join(filter(str.isdigit, str(valor)))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/consultar", methods=["POST"])
def consultar():
    cedula_input = request.form.get("cedula")

    if not col_cedula:
        return "❌ Error: no se encontró la columna de cédula"

    cedula_limpia = limpiar_cedula(cedula_input)

    # limpiar columna
    data[col_cedula] = data[col_cedula].apply(limpiar_cedula)

    resultado = data[data[col_cedula] == cedula_limpia]

    if resultado.empty:
        return "❌ No se encontró la cédula"

    fila = resultado.iloc[0]

    return f"""
    <h2>Resultado</h2>
    <p>✅ Nombre: {fila['Nombre']}</p>
    <p>📍 Lugar: {fila['Lugar']}</p>
    <p>🕒 Hora: {fila['Hora']}</p>
    <p>💼 Vacante: {fila['Vacante']}</p>
    """


if __name__ == "__main__":
    app.run()