import requests
import os
from typing import Optional

class WhatsAppSender:
    def __init__(self, api_url: str = "http://localhost:3124"):
        self.api_url = api_url
        self.send_message_endpoint = f"{api_url}/send-message"

    def send_message(self, 
                    phone_number: str, 
                    message: str, 
                    image_path: Optional[str] = None) -> dict:
        try:
            # Asegurar que el número de teléfono tiene el formato correcto
            phone_number = phone_number.strip().replace('+', '')
            if not phone_number.startswith('57'):
                phone_number = '57' + phone_number

            # Headers explícitos
            headers = {
                'Content-Type': 'application/json'
            }

            # Preparar los datos
            payload = {
                'phone_number': phone_number,
                'message': message.strip()
            }

            print(f"Enviando request a: {self.send_message_endpoint}")
            print(f"Headers: {headers}")
            print(f"Payload: {payload}")

            if image_path and os.path.exists(image_path):
                # Si hay imagen, usar multipart/form-data
                files = {
                    'image': ('image.jpg', open(image_path, 'rb'), 'image/jpeg')
                }
                response = requests.post(
                    self.send_message_endpoint,
                    data=payload,
                    files=files,
                    timeout=30
                )
            else:
                # Si no hay imagen, usar JSON
                response = requests.post(
                    self.send_message_endpoint,
                    json=payload,  # Usar json en lugar de data
                    headers=headers,
                    timeout=30
                )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            return response.json()
            
        except Exception as e:
            print(f"Error en send_message: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

if __name__ == "__main__":
    try:
        sender = WhatsAppSender()
        
        # Ejemplo: Enviar solo mensaje
        result = sender.send_message(
            phone_number="3147654655",  # Reemplaza con tu número
            message="¡Hola! Este es un mensaje de prueba 👋"
        )
        print("Resultado mensaje texto:", result)
        
    except Exception as e:
        print(f"Error general: {str(e)}")