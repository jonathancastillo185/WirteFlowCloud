import ollama
import numpy as np
import faiss
import json
from pathlib import Path

# --- CAMBIO 1: Actualizamos al nuevo modelo recomendado ---
EMBEDDING_MODEL = 'snowflake-arctic-embed:335m'
# --- CAMBIO 2: Ajustamos la dimensión del vector para que coincida con el nuevo modelo ---
VECTOR_DIMENSION = 1024

class SemanticMemory:
    """
    Gestiona la memoria a largo plazo del libro utilizando embeddings y una base de datos vectorial (FAISS).
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.index_file = self.project_path / "semantic_index.faiss"
        self.chunks_file = self.project_path / "text_chunks.json"
        self.is_available = False  # Nuevo flag de estado

        # Inicializa el cliente de Ollama y verifica la conexión
        try:
            self.client = ollama.Client()
            # Pequeña prueba para ver si Ollama está corriendo y el modelo existe
            self.client.embeddings(model=EMBEDDING_MODEL, prompt="test")
            self.is_available = True
            print("✅ Conexión con Ollama y modelo de embeddings verificada.")
        except Exception as e:
            print(f"⚠️ ADVERTENCIA: No se pudo conectar con Ollama. La memoria a largo plazo estará desactivada.")
            print(f"   Asegúrate de que Ollama esté corriendo y que hayas ejecutado 'ollama pull {EMBEDDING_MODEL}'.")
            self.client = None

        self.index = None
        self.text_chunks = {}
        self._load()

    def _generate_embedding(self, text: str):
        """Genera un embedding para un fragmento de texto usando Ollama."""
        if not self.is_available:
            return None
        try:
            response = self.client.embeddings(model=EMBEDDING_MODEL, prompt=text)
            return response["embedding"]
        except Exception as e:
            print(f"❌ Error al generar embedding con Ollama: {e}")
            return None

    def _chunk_text(self, text: str, chunk_size: int = 250, overlap: int = 50):
        """Divide un texto largo en fragmentos más pequeños y superpuestos."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    def add_chapter(self, chapter_number: int, chapter_text: str):
        """Procesa un capítulo, lo divide en chunks, genera embeddings y los añade al índice."""
        if not self.is_available:
            print("Ollama no está disponible. No se puede procesar el capítulo para la memoria semántica.")
            return

        print(f"🧠 Procesando Capítulo {chapter_number} para memoria semántica...")
        chunks = self._chunk_text(chapter_text)
        
        new_vectors = []
        new_ids = []
        
        for i, chunk in enumerate(chunks):
            embedding = self._generate_embedding(chunk)
            if embedding:
                new_vectors.append(embedding)
                # El ID numérico será la clave para nuestro diccionario de chunks
                new_ids.append(len(self.text_chunks) + len(new_ids))

        if not new_vectors:
            print("No se generaron embeddings para este capítulo.")
            return

        # Crear índice si no existe
        if self.index is None:
            self.index = faiss.IndexFlatL2(VECTOR_DIMENSION)
            self.index = faiss.IndexIDMap(self.index)

        # Convertir embeddings a formato numpy y añadirlos al índice
        vectors_np = np.array(new_vectors).astype("float32")
        ids_np = np.array(new_ids).astype("int64")
        
        self.index.add_with_ids(vectors_np, ids_np)
        
        # Actualizar el diccionario de chunks
        for i, chunk_id in enumerate(new_ids):
             self.text_chunks[chunk_id] = chunks[i]
        
        self._save()
        print(f"✅ Capítulo {chapter_number} añadido a la memoria semántica con {len(chunks)} fragmentos.")

    def search_relevant_context(self, query_text: str, k: int = 4) -> str:
        """Busca los fragmentos de texto más relevantes para una consulta dada."""
        if not self.index or not self.is_available:
            return "Memoria a largo plazo no disponible (Ollama no conectado)."

        query_embedding = self._generate_embedding(query_text)
        if not query_embedding:
            return "No se pudo generar la consulta para la memoria a largo plazo."

        query_vector = np.array([query_embedding]).astype("float32")
        
        try:
            distances, ids = self.index.search(query_vector, k)
        except Exception as e:
            print(f"❌ Error durante la búsqueda en FAISS: {e}")
            return "Error al buscar en la memoria a largo plazo."

        # Recopilar los chunks de texto correspondientes a los IDs encontrados
        relevant_chunks = [self.text_chunks[id] for id in ids[0] if id in self.text_chunks]
        
        if not relevant_chunks:
            return "No se encontró contexto relevante en capítulos anteriores."
            
        # Formatear el resultado para inyectarlo en el prompt
        context = "\n".join([f"- ...{chunk}..." for chunk in relevant_chunks])
        return context

    def _save(self):
        """Guarda el índice de FAISS y el mapa de chunks en el disco."""
        if self.index:
            faiss.write_index(self.index, str(self.index_file))
        with open(self.chunks_file, 'w', encoding='utf-8') as f:
            # Convertir claves a int/str para JSON
            serializable_chunks = {int(k): v for k, v in self.text_chunks.items()}
            json.dump(serializable_chunks, f, ensure_ascii=False, indent=2)

    def _load(self):
        """Carga el índice y los chunks desde el disco si existen."""
        if self.index_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
            except Exception as e:
                print(f"⚠️ No se pudo cargar el índice de FAISS: {e}. Se creará uno nuevo.")
                self.index = None

        if self.chunks_file.exists():
            with open(self.chunks_file, 'r', encoding='utf-8') as f:
                try:
                    loaded_chunks = json.load(f)
                    # Convertir claves de string (de JSON) a int
                    self.text_chunks = {int(k): v for k, v in loaded_chunks.items()}
                except json.JSONDecodeError:
                    print(f"⚠️ No se pudo leer el archivo de chunks. Se creará uno nuevo.")
                    self.text_chunks = {}

