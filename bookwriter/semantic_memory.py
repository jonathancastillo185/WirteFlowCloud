import faiss
import numpy as np
import ollama
from pathlib import Path

# Modelo de embedding y dimensión vectorial (ajustado para snowflake-arctic-embed)
EMBEDDING_MODEL = 'snowflake-arctic-embed:335m'
VECTOR_DIMENSION = 1024

class SemanticMemory:
    """
    Gestiona la memoria a largo plazo del libro utilizando embeddings vectoriales
    con Ollama y una base de datos FAISS local.
    """
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.index_path = self.project_path / 'semantic_index.faiss'
        self.metadata_path = self.project_path / 'semantic_metadata.json'
        
        self.index = None
        self.metadata = []
        self.is_available = self._check_ollama_connection()
        
        if self.is_available:
            self._load_index()

    def _check_ollama_connection(self) -> bool:
        """Verifica si el servicio de Ollama está activo y el modelo está disponible."""
        try:
            ollama.list() # Un simple ping para ver si el servidor responde
            print("✅ Conexión con Ollama y modelo de embeddings verificada.")
            return True
        except Exception as e:
            print(f"🔴 ADVERTENCIA: No se pudo conectar a Ollama. La memoria a largo plazo estará desactivada. Asegúrate de que Ollama esté en ejecución.")
            print(f"Error: {e}")
            return False

    def _load_index(self):
        """Carga el índice FAISS y los metadatos desde el disco si existen."""
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            import json
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"🧠 Memoria semántica cargada con {self.index.ntotal} fragmentos.")

    def _save_index(self):
        """Guarda el índice FAISS y los metadatos en el disco."""
        if self.index:
            faiss.write_index(self.index, str(self.index_path))
            import json
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def add_chapter(self, chapter_number: int, chapter_text: str):
        """Procesa un capítulo, lo divide en fragmentos, genera embeddings y los añade al índice."""
        if not self.is_available:
            return

        print(f"🧠 Procesando Capítulo {chapter_number} para memoria semántica...")
        # Dividir el texto en fragmentos (chunks) de un tamaño razonable
        chunks = self._split_text(chapter_text)
        
        if not chunks:
            return

        # Generar embeddings para cada fragmento
        embeddings = []
        for chunk in chunks:
            response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=chunk)
            embeddings.append(response["embedding"])
        
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Crear o actualizar el índice FAISS
        if self.index is None:
            self.index = faiss.IndexFlatL2(VECTOR_DIMENSION)
        
        self.index.add(embeddings_np)
        
        # Guardar metadatos para cada fragmento
        for chunk in chunks:
            self.metadata.append({"chapter": chapter_number, "content": chunk})
            
        self._save_index()
        print(f"✅ Capítulo {chapter_number} añadido a la memoria semántica con {len(chunks)} fragmentos.")

    def _split_text(self, text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
        """Divide un texto largo en fragmentos más pequeños con solapamiento."""
        if not text: return []
        words = text.split()
        if not words: return []
        
        chunks = []
        i = 0
        while i < len(words):
            end = i + chunk_size
            chunk_words = words[i:end]
            chunks.append(" ".join(chunk_words))
            i += chunk_size - overlap
        return chunks

    def search_relevant_context(self, query: str, k: int = 4) -> str:
        """Busca los fragmentos más relevantes para una consulta dada."""
        if not self.index or not self.is_available or self.index.ntotal == 0:
            return "No hay contexto disponible en la memoria a largo plazo."

        # Generar embedding para la consulta
        response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=query)
        query_embedding = np.array([response["embedding"]]).astype('float32')

        # Buscar en el índice FAISS
        distances, indices = self.index.search(query_embedding, k)
        
        # Recuperar y formatear los resultados
        results = [self.metadata[i]["content"] for i in indices[0]]
        return "\n\n---\n\n".join(results)

