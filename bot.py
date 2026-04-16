from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Leer archivo CSV
data = pd.read_csv("datos.csv")

# Limpiar nombres de columnas
data.columns = data.columns.str.strip()

print("COLUMNAS DISPONIBLES:")
print(data.columns)

# Detectar automáticamente la columna de cédula
col_cedula = None
for col in data.columns:
    if "cedula" in col.lower():
        col_cedula = col
        break

print("COLUMNA DE CÉDULA USADA:", col_cedula)


# Ruta principal (página web)
@app.route("/")
def home():
    return render_template("index.html")


# Ruta para consultar
@app.route("/consultar", methods=["POST"])
def consultar():
    cedula = request.form.get("cedula")

    if not col_cedula:
        return "❌ Error: no se encontró la columna de cédula en el archivo"

    # Limpiar entrada del usuario
    cedula = str(cedula).strip()

    # Limpiar columna de cédula en el DataFrame
    data[col_cedula] = (
        data[col_cedula]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
    )

    print("CÉDULA INGRESADA:", cedula)
    print("CÉDULAS EN DATA:")
    print(data[col_cedula].head(10))

    # Filtrar resultados
    resultado = data[data[col_cedula] == cedula]

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


# Ejecutar app
if __name__ == "__main__":
    app.run()g