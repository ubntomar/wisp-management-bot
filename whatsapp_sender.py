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
                     isGroup: bool,
                     image_path: Optional[str] = None) -> dict:
        try:
            # Asegurar que el número de teléfono tenga el formato correcto
            phone_number = phone_number.strip().replace('+', '')
            if not phone_number.startswith('57'):
                phone_number = '57' + phone_number  # Ajusta según el país

            # Construir los datos del mensaje
            payload = {
                'phone_number': phone_number,
                'message': message.strip(),
                'isGroup': isGroup
            }

            print(f"Enviando request a: {self.send_message_endpoint}")
            print(f"Payload: {payload}")

            # Verificar si la imagen existe antes de enviarla
            if image_path and os.path.exists(image_path):
                print(f"Adjuntando imagen: {image_path}")
                with open(image_path, 'rb') as image_file:
                    files = {'image': image_file}  # Enviar como 'image' según el backend
                    response = requests.post(
                        self.send_message_endpoint,
                        data=payload,  # Enviar el payload como 'data', no 'json'
                        files=files,   # Imagen como multipart/form-data
                        timeout=30
                    )
            else:
                print("Enviando solo mensaje sin imagen.")
                response = requests.post(
                    self.send_message_endpoint,
                    data=payload,  # Importante: 'data', no 'json'
                    timeout=30
                )

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return response.json()
            
        except Exception as e:
            print(f"Error en send_message: {str(e)}")
            return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    try:
        sender = WhatsAppSender()
        
        # Ruta de la imagen a enviar
        image_path = "img/voltage_last24hours.png"
        phone_number = "573147654655-1554480079"
        if(len(phone_number) == 10):
            isGroup = False
        else:
            isGroup = True     
        # Enviar mensaje con imagen adjunta
        result = sender.send_message(
            phone_number=phone_number,  # Reemplaza con tu número de WhatsApp
            message="🔋 Reporte de voltaje de las últimas 24 horas. ",
            isGroup=isGroup,
            image_path=image_path
        )
        print("Resultado del envío:", result)
        
    except Exception as e:
        print(f"Error general: {str(e)}")

#phone_number de telefono de prueba ="3147654655"
#phone_number de grupo Soportes de prueba ="573147654655-1554480079"
   
