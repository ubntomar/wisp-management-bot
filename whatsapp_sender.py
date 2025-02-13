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
        """
        Envía un mensaje y opcionalmente una imagen a través del bot de WhatsApp.
        
        Args:
            phone_number (str): Número de teléfono del destinatario
            message (str): Mensaje a enviar
            image_path (str, optional): Ruta al archivo de imagen
        
        Returns:
            dict: Respuesta del servidor
        """
        try:
            # Preparar los datos
            data = {
                'phone_number': phone_number,
                'message': message
            }
            
            files = {}
            if image_path and os.path.exists(image_path):
                files = {
                    'image': ('image.jpg', open(image_path, 'rb'), 'image/jpeg')
                }
            
            # Hacer la solicitud POST
            response = requests.post(
                self.send_message_endpoint,
                data=data,
                files=files
            )
            
            # Cerrar el archivo si se abrió
            if files and 'image' in files:
                files['image'][1].close()
            
            return response.json()
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia del sender
    sender = WhatsAppSender()
    
    # Ejemplo 1: Enviar solo mensaje
    result = sender.send_message(
        phone_number="3001234567",
        message="¡Hola! Este es un mensaje de prueba 👋"
    )
    print("Resultado mensaje texto:", result)
    
    # # Ejemplo 2: Enviar mensaje con imagen
    # result = sender.send_message(
    #     phone_number="3001234567",
    #     message="¡Mira esta imagen! 📸",
    #     image_path="./test_image.jpg"
    # )
    # print("Resultado mensaje con imagen:", result)