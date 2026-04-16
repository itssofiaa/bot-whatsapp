from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Leer CSV
data = pd.read_csv("datos.csv")

# Limpiar nombres de columnas
data.columns = data.columns.str.strip()

print("COLUMNAS DISPONIBLES:")
print(data.columns)

# Buscar columna de cédula automáticamente
col_cedula = None
for col in data.columns:
    if "cedula" in col.lower():
        col_cedula = col
        break

print("COLUMNA DE CÉDULA USADA:", col_cedula)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/consultar", methods=["POST"])
def consultar():
    cedula = request.form.get("cedula")

    if not col_cedula:
        return "❌ Error: no se encontró columna de cédula en el archivo"

    resultado = data[data[col_cedula].astype(str) == str(cedula)]

    if resultado.empty:
        return "❌ No se encontró la cédula"

    fila = resultado.iloc[0]

    return f"""
    <h2>Resultado</h2>
    ✅ Nombre: {fila['Nombre']}<br>
    📍 Lugar: {fila['Lugar']}<br>
    🕒 Hora: {fila['Hora']}<br>
    💼 Vacante: {fila['Vacante']}
    """
    

if __name__ == "__main__":
    app.run()