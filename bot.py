from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Leer archivo CSV
data = pd.read_csv("datos.csv")

# Limpiar nombres de columnas
data.columns = data.columns.str.strip()

print("COLUMNAS DISPONIBLES:")
print(data.columns)

# Detectar columna de cédula automáticamente
col_cedula = None
for col in data.columns:
    if "cedula" in col.lower():
        col_cedula = col
        break

print("COLUMNA DE CÉDULA USADA:", col_cedula)


# FUNCIÓN para limpiar texto (solo números)
def limpiar_cedula(valor):
    return ''.join(filter(str.isdigit, str(valor)))


# Ruta principal
@app.route("/")
def home():
    return render_template("index.html")


# Ruta para consultar
@app.route("/consultar", methods=["POST"])
def consultar():
    cedula_input = request.form.get("cedula")

    if not col_cedula:
        return "❌ Error: no se encontró la columna de cédula"

    # 🔥 LIMPIAR ENTRADA DEL USUARIO
    cedula_limpia = limpiar_cedula(cedula_input)

    print("CÉDULA INGRESADA:", cedula_input)
    print("CÉDULA LIMPIA:", cedula_limpia)

    # 🔥 LIMPIAR TODA LA COLUMNA UNA VEZ
    data[col_cedula] = data[col_cedula].apply(limpiar_cedula)

    print("CÉDULAS EN DATA:")
    print(data[col_cedula].head(10))

    # Buscar coincidencia
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