# codigoTFG

Este proyecto contiene:
- archivo app.py correspondiente con la API implementada
- dos archivos .h5 correspondientes a los dos ensembles desarrollados, utilizados por la API para predecir
- cuaderno Kaggle utilizado para la experimentación con las redes neuronales
- carpeta que contiene el código realizado para el desarrollo de la App UWP

Para hacer uso del trabajo hay que:
(1)- abrir la CMD del dispositivo en la ruta en la que se encuentre el archivo app.py, y ejecutar el siguiente comando para lanzar el servidor y poner la API a la escucha: 
	
		uvicorn app:app --reload

   - para ello se debe tener instalado FastAPI previamente, y comprobar en el archivo app.py que la ruta que hace referencia a la localización de los modelos de los ensembles es la correcta.

(2)- ejecutar el proyecto de la App UWP con Visual Studio
