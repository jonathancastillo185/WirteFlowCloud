import requests
import os
from bookwriter.config import STABILITY_API_KEY

# Se define el host de la API de Stability AI.
API_HOST = 'https://api.stability.ai'

def generate_image_with_stability(prompt: str, output_path: str) -> tuple[str | None, str]:
    """
    Genera una imagen usando la API v2beta de Stability AI (modelo Ultra) 
    y la guarda en la ruta especificada.

    Este método utiliza el formato multipart/form-data y maneja una respuesta
    de imagen binaria directa.

    Devuelve una tupla (ruta_de_la_imagen, mensaje_de_estado).
    """
    # Verifica que la clave de la API esté disponible en la configuración.
    if not STABILITY_API_KEY:
        return None, "❌ No se encontró la clave de API de Stability AI en el archivo .env."

    print(f"🎨 Generando imagen con el modelo Ultra y el prompt: '{prompt[:80]}...'")

    try:
        # Realiza la llamada a la API usando el endpoint del modelo 'Ultra'.
        response = requests.post(
            f"{API_HOST}/v2beta/stable-image/generate/ultra",
            headers={
                # El header de autorización utiliza un Bearer token.
                "authorization": f"Bearer {STABILITY_API_KEY}",
                # Se especifica que se acepta una imagen PNG como respuesta.
                "accept": "image/png"
            },
            # Se utiliza el formato multipart/form-data para la solicitud.
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "png",
                # Se establece la relación de aspecto a 2:3, ideal para portadas de libros.
                "aspect_ratio": "2:3",
            },
            # Se establece un tiempo de espera para la respuesta.
            timeout=45
        )

        # Si la respuesta es exitosa (código 200), se procesa la imagen.
        if response.status_code == 200:
            # El contenido de la respuesta (response.content) son los bytes de la imagen.
            # Se escribe el contenido binario directamente en el archivo de salida.
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"✅ Imagen guardada en: {output_path}")
            return output_path, "✅ Portada generada con éxito con el modelo Ultra."
        else:
            # Si la respuesta no es 200, contiene un JSON con información del error.
            error_data = response.json()
            error_message = f"❌ Error de API de Stability (Ultra): {response.status_code} - {error_data.get('errors', [str(error_data)])[0]}"
            print(error_message)
            return None, error_message

    # Manejo de excepciones de conexión.
    except requests.exceptions.RequestException as e:
        error_message = f"❌ Error de conexión con Stability AI: {e}"
        print(error_message)
        return None, error_message
    # Manejo de otras excepciones inesperadas.
    except Exception as e:
        error_message = f"❌ Ocurrió un error inesperado al generar la imagen: {e}"
        print(error_message)
        return None, error_message