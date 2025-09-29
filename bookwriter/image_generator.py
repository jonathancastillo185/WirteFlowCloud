import base64
import requests
import os
from PIL import Image
from io import BytesIO
from bookwriter.config import STABILITY_API_KEY

API_HOST = 'https://api.stability.ai'
# Usamos uno de los motores más nuevos y potentes.
# Puedes encontrar otros aquí: https://platform.stability.ai/docs/features/text-to-image
ENGINE_ID = "stable-diffusion-xl-1024-v1-0" 

def generate_image_with_stability(prompt: str, output_path: str) -> tuple[str | None, str]:
    """
    Genera una imagen usando la API de Stability AI y la guarda en la ruta especificada.
    Devuelve una tupla (ruta_de_la_imagen, mensaje_de_estado).
    """
    if not STABILITY_API_KEY:
        return None, "❌ No se encontró la clave de API de Stability AI en el archivo .env."

    print(f"🎨 Generando imagen con el prompt: '{prompt[:80]}...'")

    try:
        response = requests.post(
            f"{API_HOST}/v1/generation/{ENGINE_ID}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {STABILITY_API_KEY}"
            },
            json={
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 768, # Altura de la imagen
                "width": 512,  # Anchura de la imagen (formato vertical de libro)
                "samples": 1,
                "steps": 30,
                # Estilos para dar una apariencia más profesional
                "style_preset": "photographic" 
            },
            timeout=30 # Añadimos un timeout para evitar que se quede colgado
        )

        response.raise_for_status() # Lanza un error si la petición falla (ej. 4xx o 5xx)

        data = response.json()

        for i, image in enumerate(data["artifacts"]):
            image_data = base64.b64decode(image["base64"])
            
            # Guardar la imagen
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            print(f"✅ Imagen guardada en: {output_path}")
            return output_path, "✅ Portada generada con éxito."

    except requests.exceptions.HTTPError as err:
        error_message = f"❌ Error de API de Stability: {err.response.status_code} - {err.response.text}"
        print(error_message)
        return None, error_message
    except requests.exceptions.RequestException as e:
        error_message = f"❌ Error de conexión con Stability AI: {e}"
        print(error_message)
        return None, error_message
    except Exception as e:
        error_message = f"❌ Ocurrió un error inesperado al generar la imagen: {e}"
        print(error_message)
        return None, error_message
    
    return None, "❌ No se recibieron imágenes de la API."

