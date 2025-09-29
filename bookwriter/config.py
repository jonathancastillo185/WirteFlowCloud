import os
from dotenv import load_dotenv
from groq import Groq
from pathlib import Path

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- Claves de API ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# --- Rutas del Proyecto ---
# Define la ruta base del proyecto y el directorio para guardar los libros
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_PATH = BASE_DIR / "projects"
PROJECTS_PATH.mkdir(exist_ok=True)

# --- Configuración del Cliente Groq ---
if not GROQ_API_KEY:
    print("❌ ADVERTENCIA: La variable de entorno GROQ_API_KEY no está configurada.")
    groq_client = None
else:
    groq_client = Groq(api_key=GROQ_API_KEY)

# --- Parámetros del Modelo de Lenguaje (Groq) ---
MODEL = os.getenv("MODEL_NAME", "llama-3.1-70b-versatile")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
TOP_P = float(os.getenv("TOP_P", 0.9))
STOP_SEQUENCES_STR = os.getenv("STOP_SEQUENCES", "")
STOP_SEQUENCES = [stop.strip() for stop in STOP_SEQUENCES_STR.split(',')] if STOP_SEQUENCES_STR else None

