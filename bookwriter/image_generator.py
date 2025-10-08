import requests
import os
from bookwriter.config import STABILITY_API_KEY
from PIL import Image
from io import BytesIO

# Se define el host de la API de Stability AI.
API_HOST = 'https://api.stability.ai'

def generate_image_with_stability(prompt: str, output_path: str, is_frame: bool = False) -> tuple[str | None, str]:
    """
    Genera una imagen usando la API v2beta de Stability AI (modelo Ultra)
    y la guarda en la ruta especificada.
    Devuelve una tupla (ruta_de_la_imagen, mensaje_de_estado).
    """
    if not STABILITY_API_KEY:
        return None, "❌ No se encontró la clave de API de Stability AI en el archivo .env."

    model_name = "ultra"
    print(f"🎨 Generando imagen con el modelo {model_name} y el prompt: '{prompt[:80]}...'")

    try:
        response = requests.post(
            f"{API_HOST}/v2beta/stable-image/generate/{model_name}",
            headers={
                "authorization": f"Bearer {STABILITY_API_KEY}",
                # --- LÍNEA CORREGIDA ---
                # Cambiamos "image/png" por "image/*" para cumplir con la API
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "png",
                "aspect_ratio": "2:3",
            },
            timeout=60
        )

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Imagen guardada en: {output_path}")
            return output_path, f"✅ Imagen generada con éxito con el modelo {model_name}."
        else:
            error_data = response.json()
            error_message = f"❌ Error de API de Stability ({model_name}): {response.status_code} - {error_data.get('errors', [str(error_data)])[0]}"
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

def create_composite_cover(main_prompt: str, frame_prompt: str, final_output_path: str, temp_folder: str) -> tuple[str | None, str]:
    """
    Crea una portada compuesta generando una imagen principal y un marco, y luego combinándolos.
    """
    main_image_path = os.path.join(temp_folder, "main_image.png")
    frame_image_path = os.path.join(temp_folder, "frame_image.png")

    # 1. Generar la imagen principal
    print("--- Paso 1: Generando imagen principal de la portada ---")
    main_path, main_status = generate_image_with_stability(main_prompt, main_image_path)
    if not main_path:
        return None, f"Error al generar la imagen principal: {main_status}"

    # 2. Generar el marco
    print("--- Paso 2: Generando el marco de la portada ---")
    frame_path, frame_status = generate_image_with_stability(frame_prompt, frame_image_path)
    if not frame_path:
        return None, f"Error al generar el marco: {frame_status}"

    # 3. Combinar las imágenes con Pillow
    print("--- Paso 3: Combinando las imágenes para crear la portada final ---")
    try:
        with Image.open(main_path).convert("RGBA") as main_img:
            with Image.open(frame_path).convert("RGBA") as frame_img:
                if main_img.size != frame_img.size:
                    frame_img = frame_img.resize(main_img.size, Image.Resampling.LANCZOS)
                
                composite_image = Image.alpha_composite(main_img, frame_img)
                composite_image.save(final_output_path, "PNG")

        print(f"✅ Portada compuesta guardada en: {final_output_path}")
        return final_output_path, "✅ Portada compuesta generada con éxito."

    except Exception as e:
        error_message = f"❌ Ocurrió un error al combinar las imágenes de la portada: {e}"
        print(error_message)
        return None, error_message