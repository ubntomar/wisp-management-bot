#!/usr/bin/env python3
"""
Script para extraer direcciones ARP activas (flag DC) desde dispositivos de red
Uso: python arp_extractor.py <IP_ADDRESS> [device_type]
"""

import sys
import os
import time
import re
import ipaddress
import paramiko
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ARPExtractor:
    def __init__(self):
        """Inicializa el extractor con credenciales desde .env"""
        self.mikrotik_credentials = [
            {'username': 'admin', 'password': os.getenv('ADMIN_PASS', '')},
            {'username': 'admin', 'password': os.getenv('ADMIN_PASS2', '')},
            {'username': 'agingenieria', 'password': os.getenv('AGINGENIERIA_PASS', '')},
            {'username': 'agingenieria', 'password': os.getenv('AGINGENIERIA_PASS2', '')}
        ]
        
        self.ubiquiti_credentials = [
            {'username': os.getenv('UBNT_USER', 'ubnt'), 'password': os.getenv('UBNT_PASS', '')},
            {'username': os.getenv('UBNT_USER', 'ubnt'), 'password': os.getenv('UBNT_PASS2', '')},
            {'username': os.getenv('UBNT_USER', 'ubnt'), 'password': os.getenv('UBNT_PASS3', '')},
            {'username': os.getenv('UBNT_USER', 'ubnt'), 'password': os.getenv('UBNT_PASS4', '')}
        ]
        
        # Filtrar credenciales vacías
        self.mikrotik_credentials = [c for c in self.mikrotik_credentials if c['password']]
        self.ubiquiti_credentials = [c for c in self.ubiquiti_credentials if c['password']]
        
        # Configuración SSH
        self.ssh_timeout = 20
        
        # Configuración WhatsApp
        self.whatsapp_endpoint = os.getenv('WHATSAPP_API_ENDPOINT', 'http://45.61.59.204:8050/api/send-message')
        self.whatsapp_target = os.getenv('WHATSAPP_TARGET_NUMBER', '')
        self.whatsapp_timeout = 30

    def is_valid_ip(self, ip_str):
        """Valida si una cadena es una dirección IP válida"""
        try:
            ipaddress.IPv4Address(ip_str.strip())
            return True
        except ipaddress.AddressValueError:
            return False

    def sort_ips(self, ip_list):
        """Ordena lista de IPs numéricamente"""
        try:
            return sorted(ip_list, key=lambda ip: ipaddress.IPv4Address(ip))
        except:
            return sorted(ip_list)

    def establish_ssh_connection(self, target_ip, credentials):
        """Establece conexión SSH con múltiples credenciales"""
        print(f"🔌 Conectando a {target_ip}...")
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        for i, cred in enumerate(credentials, 1):
            if not cred['password']:  # Saltar credenciales vacías
                continue
                
            print(f"   Intento {i}/{len(credentials)}: {cred['username']}:{'*' * len(cred['password'])}")
            
            try:
                ssh.connect(
                    hostname=target_ip,
                    port=22,
                    username=cred['username'],
                    password=cred['password'],
                    timeout=self.ssh_timeout,
                    allow_agent=False,
                    look_for_keys=False,
                    banner_timeout=30
                )
                
                print(f"✅ Conexión exitosa con {cred['username']}")
                return ssh
                
            except paramiko.AuthenticationException:
                print(f"❌ Autenticación fallida para {cred['username']}")
            except paramiko.SSHException as e:
                print(f"❌ Error SSH con {cred['username']}: {str(e)}")
            except Exception as e:
                print(f"❌ Error de conexión con {cred['username']}: {str(e)}")
        
        raise Exception(f"No se pudo establecer conexión SSH con {target_ip}")

    def execute_ssh_command(self, ssh, command, timeout=30):
        """Ejecuta comando SSH y retorna stdout, stderr"""
        try:
            stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
            
            stdout_data = stdout.read().decode('utf-8', errors='ignore').strip()
            stderr_data = stderr.read().decode('utf-8', errors='ignore').strip()
            
            return stdout_data, stderr_data
            
        except Exception as e:
            raise Exception(f"Error ejecutando comando: {str(e)}")

    def extract_mikrotik_arp(self, ssh):
        """Extrae direcciones ARP activas de MikroTik (flag DC)"""
        print("📡 Extrayendo ARP activas de MikroTik...")
        
        # Comando para obtener solo entradas ARP con flags Dynamic y Complete
        arp_command = ':foreach i in=[/ip arp find where dynamic=yes and complete=yes] do={ :put [/ip arp get $i address] }'
        
        print(f"   Comando: {arp_command}")
        
        try:
            stdout, stderr = self.execute_ssh_command(ssh, arp_command)
            
            if stderr:
                print(f"⚠️  Advertencia: {stderr}")
            
            if not stdout:
                print("ℹ️  No se encontraron entradas ARP activas")
                return []
            
            # Procesar las IPs
            raw_ips = stdout.strip().split('\n')
            active_ips = []
            
            for ip in raw_ips:
                cleaned_ip = ip.strip().replace('\r', '')
                if cleaned_ip and self.is_valid_ip(cleaned_ip):
                    active_ips.append(cleaned_ip)
            
            # Ordenar numéricamente
            active_ips = self.sort_ips(active_ips)
            
            print(f"✅ {len(active_ips)} direcciones ARP activas encontradas")
            return active_ips
            
        except Exception as e:
            print(f"❌ Error extrayendo ARP de MikroTik: {str(e)}")
            return []

    def extract_ubiquiti_arp(self, ssh):
        """Extrae direcciones ARP activas de Ubiquiti/Linux"""
        print("📡 Extrayendo ARP activas de Ubiquiti...")
        
        # Comando que filtra por estados REACHABLE y STALE (equivalente a DC)
        arp_command = 'ip neigh show | grep -E "lladdr [0-9a-f]{2}(:[0-9a-f]{2}){5}" | grep -E "REACHABLE|STALE" | awk \'{print $1}\''
        
        print(f"   Comando: {arp_command}")
        
        try:
            stdout, stderr = self.execute_ssh_command(ssh, arp_command)
            
            if stderr:
                print(f"⚠️  Advertencia: {stderr}")
            
            if not stdout:
                print("ℹ️  No se encontraron entradas ARP activas con método principal")
                print("🔄 Intentando método alternativo...")
                
                # Método alternativo con arp clásico
                alt_command = 'arp -e | tail -n +2 | awk \'{print $1}\''
                stdout, stderr = self.execute_ssh_command(ssh, alt_command)
                
                if not stdout:
                    print("ℹ️  No se encontraron entradas ARP activas")
                    return []
                else:
                    print("✅ Datos obtenidos con método alternativo")
            
            # Procesar las IPs
            raw_ips = stdout.strip().split('\n')
            active_ips = []
            
            for ip in raw_ips:
                cleaned_ip = ip.strip()
                if cleaned_ip and self.is_valid_ip(cleaned_ip):
                    active_ips.append(cleaned_ip)
            
            # Ordenar numéricamente
            active_ips = self.sort_ips(active_ips)
            
            print(f"✅ {len(active_ips)} direcciones ARP activas encontradas")
            return active_ips
            
        except Exception as e:
            print(f"❌ Error extrayendo ARP de Ubiquiti: {str(e)}")
            return []

    def detect_device_type(self, ssh):
        """Detecta automáticamente el tipo de dispositivo"""
        print("🔍 Detectando tipo de dispositivo...")
        
        # Probar si es MikroTik
        try:
            stdout, stderr = self.execute_ssh_command(ssh, '/system resource print', timeout=10)
            if 'RouterOS' in stdout or 'mikrotik' in stdout.lower():
                print("📋 Dispositivo detectado: MikroTik RouterOS")
                return 'mikrotik'
        except:
            pass
        
        # Probar si es Ubiquiti/Linux
        try:
            stdout, stderr = self.execute_ssh_command(ssh, 'uname -a', timeout=10)
            if stdout and not stderr:
                print("📋 Dispositivo detectado: Ubiquiti/Linux")
                return 'ubiquiti'
        except:
            pass
        
        print("⚠️  Tipo de dispositivo no detectado automáticamente")
        return 'unknown'

    def generate_summary(self, arp_list):
        """Genera resumen estadístico si hay muchas IPs"""
        if len(arp_list) <= 10:
            return None
        
        subnet_count = {}
        for ip in arp_list:
            try:
                network = str(ipaddress.IPv4Network(f"{ip}/24", strict=False).network_address)
                subnet = network.replace('.0', '.0/24')
                subnet_count[subnet] = subnet_count.get(subnet, 0) + 1
            except:
                continue
        
        # Ordenar por cantidad descendente
        sorted_subnets = sorted(subnet_count.items(), key=lambda x: x[1], reverse=True)
        return [f"{subnet}: {count} dispositivos" for subnet, count in sorted_subnets]

    def check_subnet_alerts(self, summary, target_ip):
        """Verifica si hay alertas en las subredes críticas - SOLO para 192.168.26.1"""
        
        # Solo aplicar validación para la IP específica
        if target_ip != '192.168.26.1':
            return None
            
        if not summary:
            return None
            
        # Subredes críticas que deben tener al menos 10 dispositivos
        critical_subnets = {
            '192.168.26.0/24': 10,
            '192.168.20.0/24': 10, 
            '192.168.30.0/24': 10
        }
        
        alerts = []
        
        # Parsear el resumen para extraer datos de las subredes
        subnet_data = {}
        for line in summary:
            # Formato esperado: "192.168.26.0/24: 63 dispositivos"
            parts = line.split(': ')
            if len(parts) == 2:
                subnet = parts[0]
                try:
                    count = int(parts[1].split(' ')[0])
                    subnet_data[subnet] = count
                except ValueError:
                    continue
        
        # Verificar subredes críticas
        for subnet, min_devices in critical_subnets.items():
            current_count = subnet_data.get(subnet, 0)
            if current_count < min_devices:
                if current_count == 0:
                    alerts.append(f"❌ {subnet}: SIN DISPOSITIVOS")
                else:
                    alerts.append(f"⚠️ {subnet}: {current_count} dispositivos (< {min_devices})")
        
        return alerts if alerts else None

    def format_whatsapp_message(self, target_ip, result):
        """Formatea el resultado para envío por WhatsApp"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        if not result['success']:
            return f"""🚨 ERROR - Extracción ARP
🎯 Dispositivo: {target_ip}
⏰ Fecha: {timestamp}
❌ Error: {result.get('error', 'Error desconocido')}"""
        
        arp_list = result['arp_list']
        device_type = result['device_type']
        summary = result.get('summary', [])
        
        # Verificar alertas de subredes críticas (solo para 192.168.26.1)
        subnet_alerts = self.check_subnet_alerts(summary, target_ip)
        
        # Encabezado con alertas si existen
        if subnet_alerts:
            alert_section = "🚨 ADVERTENCIA DE FALLO EN LA RED! 🚨\n"
            for alert in subnet_alerts:
                alert_section += f"{alert}\n"
            alert_section += "\n"
        else:
            alert_section = ""
        
        # Mensaje principal
        message = f"""{alert_section}📡 REPORTE ARP ACTIVAS
🎯 Dispositivo: {target_ip}
📋 Tipo: {device_type.upper()}
⏰ Fecha: {timestamp}
🔢 Total: {len(arp_list)} IPs activas
"""
        
        if not arp_list:
            message += "\n❓ No se encontraron direcciones ARP activas"
            return message
        
        # Lista de IPs (limitada para WhatsApp)
        message += "\n📋 Direcciones IP:"
        max_ips_to_show = 6  # Limitar para evitar mensajes muy largos
        
        for i, ip in enumerate(arp_list[:max_ips_to_show], 1):
            message += f"\n  {i:2d}. {ip}"
        
        if len(arp_list) > max_ips_to_show:
            remaining = len(arp_list) - max_ips_to_show
            message += f"\n  ... y {remaining} IPs más"
        
        # Resumen por subred si existe
        if summary:
            message += "\n\n📊 Resumen por subred:"
            for line in summary[:5]:  # Máximo 5 subredes
                message += f"\n  • {line}"
            
            if len(summary) > 5:
                message += f"\n  ... y {len(summary) - 5} subredes más"
        
        return message

    def send_whatsapp_message(self, message, custom_target=None):
        """Envía mensaje a WhatsApp usando el endpoint configurado"""
        target = custom_target or self.whatsapp_target
        
        if not target:
            print("⚠️  No se configuró número de WhatsApp en .env (WHATSAPP_TARGET_NUMBER)")
            return False
        
        if not self.whatsapp_endpoint:
            print("⚠️  No se configuró endpoint de WhatsApp en .env (WHATSAPP_API_ENDPOINT)")
            return False
        
        payload = {
            "target": target,
            "message": message
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        print(f"📱 Enviando mensaje a WhatsApp ({target})...")
        
        try:
            response = requests.post(
                self.whatsapp_endpoint,
                headers=headers,
                data=json.dumps(payload),
                timeout=self.whatsapp_timeout
            )
            
            if response.status_code == 200:
                print("✅ Mensaje enviado exitosamente a WhatsApp")
                return True
            else:
                print(f"❌ Error enviando mensaje: HTTP {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Timeout enviando mensaje a WhatsApp")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Error de conexión al endpoint de WhatsApp")
            return False
        except Exception as e:
            print(f"❌ Error inesperado enviando mensaje: {str(e)}")
            return False

    def extract_arp_from_device(self, target_ip, device_type='auto', send_whatsapp=True, whatsapp_target=None):
        """Función principal para extraer ARP de un dispositivo"""
        ssh = None
        
        try:
            print(f"\n🚀 Iniciando extracción de ARP para {target_ip}")
            print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Determinar credenciales según tipo de dispositivo
            if device_type == 'mikrotik':
                credentials = self.mikrotik_credentials
            elif device_type == 'ubiquiti':
                credentials = self.ubiquiti_credentials
            else:  # auto-detect
                credentials = self.mikrotik_credentials + self.ubiquiti_credentials
            
            if not credentials:
                raise Exception("No se encontraron credenciales válidas en el archivo .env")
            
            # Establecer conexión SSH
            ssh = self.establish_ssh_connection(target_ip, credentials)
            
            # Detectar tipo de dispositivo si es necesario
            if device_type == 'auto':
                detected_type = self.detect_device_type(ssh)
            else:
                detected_type = device_type
            
            # Extraer ARP según el tipo de dispositivo
            if detected_type == 'mikrotik':
                arp_list = self.extract_mikrotik_arp(ssh)
            elif detected_type == 'ubiquiti':
                arp_list = self.extract_ubiquiti_arp(ssh)
            else:
                # Intentar ambos métodos
                print("🔄 Intentando extracción con ambos métodos...")
                arp_list = self.extract_mikrotik_arp(ssh)
                if not arp_list:
                    arp_list = self.extract_ubiquiti_arp(ssh)
                detected_type = 'mikrotik' if arp_list else 'unknown'
            
            # Generar resumen
            summary = self.generate_summary(arp_list)
            
            # Crear resultado
            result = {
                'success': True,
                'device_type': detected_type,
                'arp_list': arp_list,
                'summary': summary,
                'total_count': len(arp_list)
            }
            
            # Mostrar resultados en consola
            print(f"\n📊 RESULTADOS PARA {target_ip}:")
            print(f"   Tipo de dispositivo: {detected_type}")
            print(f"   Total de ARP activas: {len(arp_list)}")
            
            if arp_list:
                print("\n📋 Direcciones IP activas:")
                for i, ip in enumerate(arp_list, 1):
                    print(f"   {i:3d}. {ip}")
                
                if summary:
                    print("\n📈 Resumen por subred:")
                    for line in summary:
                        print(f"   {line}")
            else:
                print("ℹ️  No se encontraron direcciones ARP activas")
            
            # Enviar mensaje por WhatsApp si está habilitado
            if send_whatsapp:
                whatsapp_message = self.format_whatsapp_message(target_ip, result)
                self.send_whatsapp_message(whatsapp_message, whatsapp_target)
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'arp_list': [],
                'total_count': 0
            }
            
            print(f"\n💥 ERROR: {str(e)}")
            
            # Enviar mensaje de error por WhatsApp si está habilitado
            if send_whatsapp:
                whatsapp_message = self.format_whatsapp_message(target_ip, error_result)
                self.send_whatsapp_message(whatsapp_message, whatsapp_target)
            
            return error_result
        
        finally:
            if ssh:
                ssh.close()
                print("🔐 Conexión SSH cerrada")

def main():
    """Función principal del script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extractor de direcciones ARP activas (flag DC)')
    parser.add_argument('ip', help='Dirección IP del dispositivo')
    parser.add_argument('device_type', nargs='?', default='auto', 
                       choices=['auto', 'mikrotik', 'ubiquiti'],
                       help='Tipo de dispositivo (auto por defecto)')
    parser.add_argument('--no-whatsapp', action='store_true',
                       help='No enviar mensaje por WhatsApp')
    parser.add_argument('--whatsapp-target', type=str,
                       help='Número específico para WhatsApp (sobrescribe .env)')
    
    args = parser.parse_args()
    
    target_ip = args.ip
    device_type = args.device_type
    send_whatsapp = not args.no_whatsapp
    whatsapp_target = args.whatsapp_target
    
    # Validar IP
    try:
        ipaddress.IPv4Address(target_ip)
    except ipaddress.AddressValueError:
        print(f"❌ Dirección IP inválida: {target_ip}")
        print("\n📝 Uso:")
        print("   python arp_extractor.py <IP_ADDRESS> [device_type] [--no-whatsapp] [--whatsapp-target NUMBER]")
        print("\n📝 Ejemplos:")
        print("   python arp_extractor.py 192.168.1.1")
        print("   python arp_extractor.py 192.168.1.254 mikrotik")
        print("   python arp_extractor.py 192.168.2.1 ubiquiti --no-whatsapp")
        print("   python arp_extractor.py 192.168.1.1 auto --whatsapp-target 573161234567")
        sys.exit(1)
    
    # Verificar que existe el archivo .env
    if not os.path.exists('.env'):
        print("⚠️  Advertencia: No se encontró archivo .env")
        print("   Asegúrate de que exista el archivo .env con las credenciales:")
        print("   # Credenciales SSH")
        print("   ADMIN_PASS=tu_password")
        print("   UBNT_USER=tu_usuario")
        print("   UBNT_PASS=tu_password")
        print("   # Configuración WhatsApp")
        print("   WHATSAPP_API_ENDPOINT=http://45.61.59.204:8050/api/send-message")
        print("   WHATSAPP_TARGET_NUMBER=573161234567")
    
    # Crear extractor y ejecutar
    extractor = ARPExtractor()
    result = extractor.extract_arp_from_device(target_ip, device_type, send_whatsapp, whatsapp_target)
    
    # Código de salida según resultado
    sys.exit(0 if result['success'] else 1)

if __name__ == '__main__':
    main()