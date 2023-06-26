from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import requests


app = Flask(__name__)


# Variables globales para almacenar los resultados de la limpieza de datos
ancheta_mas_vendida = ""
cantidad_mas_vendida = 0
ancheta_menos_vendida = ""
cantidad_menos_vendida = 0

@app.route("/", methods=["GET", "POST"])
def inicio():
    global ancheta_mas_vendida, cantidad_mas_vendida, ancheta_menos_vendida, cantidad_menos_vendida

    if request.method == "POST":

        archivo = request.files["archivo"]
                # Obtener la ruta de la carpeta donde deseas borrar los archivos
        ruta_carpeta = "data/"

        # Eliminar todos los archivos en la carpeta
        for nombre_archivo in os.listdir(ruta_carpeta):
            ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)
            os.remove(ruta_archivo)

        archivo.save("data/" + archivo.filename)
        
        # Realizar la limpieza de datos utilizando pandas
        ruta_archivo = os.path.join(ruta_carpeta, archivo.filename)
        df = pd.read_csv(ruta_archivo)

        # Se eliminan los valores nulos
        df_limpio = df.dropna()

        # Se hace un diccionario en donde se almacena el nombre de la ancheta y las veces que esta se repite en el df
        ventas_por_ancheta = df_limpio.groupby('Nombre_Ancheta')['ID'].count()

        ancheta_mas_vendida = ventas_por_ancheta[ventas_por_ancheta == ventas_por_ancheta.max()]
        cantidad_mas_vendida = ventas_por_ancheta.max()

        ancheta_menos_vendida = ventas_por_ancheta[ventas_por_ancheta == ventas_por_ancheta.min()].index[0]
        cantidad_menos_vendida = ventas_por_ancheta.min()

        return redirect(url_for('chat'))


    return render_template("index.html")


# Ruta para interactuar con la API de ChatGPT
@app.route("/chat", methods=["GET","POST"])
def chat():
    global ancheta_mas_vendida, cantidad_mas_vendida, ancheta_menos_vendida, cantidad_menos_vendida
    peticion = "Quiero saber más sobre las estrategias de marketing para promover la ancheta más vendida."
    
    prompt = f"La ancheta más vendida es '{ancheta_mas_vendida}' con {cantidad_mas_vendida} ventas. ¿Puedes darme recomendaciones y qué medidas puedo tomar para que esta ancheta siga siendo igual de popular o qué estrategias puedo implementar?"
    peticion_usuario = prompt + " " + peticion
    
    URL = "https://api.openai.com/v1/chat/completions"
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    PARAMS = {
        "model": "gpt-3.5-turbo-0301",
        "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": peticion_usuario}]
    }
    
    response = requests.post(URL, headers=HEADERS, json=PARAMS)
    respuesta_json = response.json()
    
    if response.status_code == 200:
        respuesta = respuesta_json["choices"][0]["message"]["content"]
        return render_template("index.html", respuesta_chat=respuesta)
    else:
        print("Error al enviar la petición a la API.")
        return render_template("index.html", respuesta_chat="Error al enviar la petición a la API.")



if __name__ == "__main__":
    app.run(debug=True)