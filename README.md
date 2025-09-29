📚 BookWriter AI - Asistente de Escritura Local

BookWriter AI es una aplicación de escritorio que utiliza el poder de los grandes modelos de lenguaje (LLMs) para ayudarte a escribir novelas completas, manteniendo una coherencia profunda en la trama y los personajes de principio a fin.

El sistema combina la velocidad de la API de Groq para la generación de texto, una memoria semántica local con Ollama y FAISS para la coherencia a largo plazo, y la API de Stability AI para generar portadas únicas para tus libros.
✨ Características

    Generación de Outlines Detallados: Proporciona una premisa y la IA creará una estructura completa para tu libro, incluyendo el mundo, los personajes y un resumen de cada capítulo.

    Memoria a Largo Plazo: Utiliza embeddings vectoriales para "recordar" detalles de capítulos anteriores, asegurando que los personajes y la trama se mantengan consistentes.

    Escritura Asistida: Genera el libro página por página o ponlo en "piloto automático" para que escriba todo el libro por ti.

    Creación de Resúmenes: Genera automáticamente un resumen de contraportada (blurb) atractivo y comercial.

    Generación de Portadas con IA: Crea una portada única y artística para tu libro basada en su contenido.

    Exportación Profesional: Exporta tu manuscrito a un PDF con formato de e-book, incluyendo portada, índice de contenidos interactivo y resumen.

    Totalmente Local y Privado: La memoria semántica y la generación de embeddings se ejecutan en tu propia máquina gracias a Ollama, garantizando tu privacidad.

🛠️ Instalación

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.
Prerrequisitos

Necesitas tener Python 3.10 o superior y Git instalados en tu sistema.
1. Clonar el Repositorio

Abre una terminal y clona este repositorio:

git clone <URL_DEL_REPOSITORIO>
cd BookWriter_Groq_Local

2. Crear un Entorno Virtual

Es altamente recomendable usar un entorno virtual para aislar las dependencias del proyecto.

python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate

3. Instalar Dependencias de Python

Instala todas las librerías necesarias con un solo comando:

pip install -r requirements.txt

4. Configurar Ollama (Para la Memoria a Largo Plazo)

Ollama es el motor que nos permite ejecutar modelos de embeddings localmente. Es crucial para la coherencia del libro.

    Descarga e Instala Ollama: Ve a ollama.com y descarga la aplicación para tu sistema operativo (macOS, Linux, Windows).

    Ejecuta Ollama: Asegúrate de que la aplicación de Ollama esté en ejecución en segundo plano.

    Descarga el Modelo de Embeddings: Abre tu terminal y ejecuta el siguiente comando para descargar el modelo que usaremos para la memoria semántica:

    ollama pull snowflake-arctic-embed:335m

5. Configurar las Claves de API

El proyecto necesita claves de API para funcionar.

    Crea el archivo .env: Renombra el archivo .env.example a .env.

    mv .env.example .env

    Añade tus claves: Abre el archivo .env con un editor de texto y pega tus claves de API:

        GROQ_API_KEY: Obligatoria. Consíguela registrándote en GroqCloud.

        STABILITY_API_KEY: Opcional. Necesaria solo si quieres generar portadas. Consíguela registrándote en Stability AI Platform.

🚀 Cómo Usar la Aplicación

Una vez que todo esté instalado y configurado, ¡lanzar la aplicación es muy fácil!

    Asegúrate de que tu entorno virtual esté activado y que Ollama esté en ejecución.

    Desde la raíz del proyecto, ejecuta el siguiente comando:

    python app.py

