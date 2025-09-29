import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración de la API de Groq ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("No se encontró la variable de entorno GROQ_API_KEY. "
                     "Por favor, crea un archivo .env y añade tu clave.")

# Cliente de Groq reutilizable
groq_client = Groq(api_key=GROQ_API_KEY)

# --- Modelo de Lenguaje y Configuración ---
# Se obtienen del entorno para mayor flexibilidad.
# Si no se definen en el archivo .env, se usan valores por defecto razonables.
MODEL = os.getenv("MODEL_NAME", "llama-3.1-70b-versatile")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.75))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
TOP_P = float(os.getenv("TOP_P", 0.9))
STOP_SEQUENCES = os.getenv("STOP_SEQUENCES", "\n\n").split(",")

# --- Rutas del Proyecto ---
# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Directorio donde se guardarán todos los libros
PROJECTS_PATH = BASE_DIR / "projects"

# Asegurarse de que el directorio de proyectos exista
PROJECTS_PATH.mkdir(exist_ok=True)

