📚 BookWriter AI - Asistente de Escritura Local con Memoria a Largo Plazo

BookWriter AI es una aplicación de escritorio construida con Python y Gradio que te permite escribir novelas y libros largos con la ayuda de modelos de lenguaje de última generación a través de la API de Groq.

Su característica principal es un sistema de memoria dual:

    Memoria a Corto Plazo: Recuerda lo último que se escribió para una continuidad fluida.

    Memoria a Largo Plazo (Semántica): Utiliza embeddings vectoriales y una base de datos local (FAISS) gestionada por Ollama para recordar detalles clave de toda la novela, garantizando una consistencia profunda en tramas complejas y arcos de personajes largos.

Características

    Interfaz Gráfica Sencilla: Gestiona tus proyectos, genera contenido y visualiza tu libro, todo desde una interfaz web local.

    Generación de Outlines: Proporciona una premisa y la IA diseñará la estructura completa de tu libro, incluyendo el mundo, los personajes y un resumen de cada capítulo.

    Escritura Asistida por IA: Genera el libro página por página, manteniendo siempre el contexto y la coherencia.

    Memoria Semántica Local: Gracias a Ollama, el sistema comprende el contenido de los capítulos ya escritos y utiliza esa información para guiar la escritura de los nuevos, evitando contradicciones.

    Configuración Flexible: Controla qué modelo de Groq usar y ajusta sus parámetros (temperatura, top_p, etc.) directamente desde un archivo .env.

    Exportación a PDF: Convierte tu manuscrito en un PDF listo para compartir.

    Privacidad: Todo tu trabajo y la memoria semántica se guardan localmente en tu computadora.

🛠️ Instalación y Configuración

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.
Paso 1: Requisitos Previos (Instalar Ollama)

La memoria a largo plazo de esta aplicación depende de Ollama. Debes instalarlo primero.

    Descarga Ollama: Ve a ollama.com y descarga la aplicación para tu sistema operativo (macOS, Linux, Windows).

    Inicia Ollama: Una vez instalado, asegúrate de que la aplicación de Ollama esté en ejecución. Deberías ver un ícono en tu barra de tareas o menú.

    Descarga el Modelo de Embeddings: Abre una terminal o línea de comandos y ejecuta el siguiente comando. Este modelo es el "cerebro" que permitirá a la aplicación entender el significado de tu libro.

    ollama pull snowflake-arctic-embed:335m

    La descarga tardará unos minutos. Una vez completada, puedes dejar Ollama corriendo en segundo plano.

Paso 2: Clonar el Repositorio

git clone [https://github.com/tu_usuario/BookWriter_Groq_Local.git](https://github.com/tu_usuario/BookWriter_Groq_Local.git)
cd BookWriter_Groq_Local

Paso 3: Crear un Entorno Virtual y Instalar Dependencias

Es una buena práctica usar un entorno virtual para aislar las dependencias del proyecto.

# Crear un entorno virtual
python3 -m venv env

# Activar el entorno virtual
# En macOS / Linux:
source env/bin/activate
# En Windows:
.\env\Scripts\activate

# Instalar las librerías necesarias
pip install -r requirements.txt

Paso 4: Configurar tus Variables de Entorno

    Crea tu API Key de Groq: Ve a console.groq.com/keys y crea una nueva clave de API.

    Configura el archivo .env:

        Renombra el archivo .env.example a .env.

        Abre el archivo .env y pega tu clave de API de Groq donde se indica.

        Puedes ajustar opcionalmente los otros parámetros del modelo si lo deseas.

▶️ Ejecución de la Aplicación

Con Ollama corriendo en segundo plano y tu entorno virtual activado, inicia la aplicación con el siguiente comando:

python app.py

Abre tu navegador web y ve a la dirección URL que aparece en la terminal (normalmente http://127.0.0.1:7860).

¡Y listo! Ya puedes empezar a crear tu próxima gran novela.