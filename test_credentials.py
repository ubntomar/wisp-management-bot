#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

print("=== TEST CREDENCIALES ===")
print(f"ADMIN_PASS: {'SET' if os.getenv('ADMIN_PASS') else 'NOT SET'}")
print(f"ADMIN_PASS2: {'SET' if os.getenv('ADMIN_PASS2') else 'NOT SET'}")
print(f"AGINGENIERIA_PASS: {'SET' if os.getenv('AGINGENIERIA_PASS') else 'NOT SET'}")
print(f"AGINGENIERIA_PASS2: {'SET' if os.getenv('AGINGENIERIA_PASS2') else 'NOT SET'}")
print(f"UBNT_PASS: {'SET' if os.getenv('UBNT_PASS') else 'NOT SET'}")
print(f"UBNT_PASS2: {'SET' if os.getenv('UBNT_PASS2') else 'NOT SET'}")
print(f"UBNT_PASS3: {'SET' if os.getenv('UBNT_PASS3') else 'NOT SET'}")
print(f"UBNT_PASS4: {'SET' if os.getenv('UBNT_PASS4') else 'NOT SET'}")
print(f"WHATSAPP_TARGET_NUMBER: {'SET' if os.getenv('WHATSAPP_TARGET_NUMBER') else 'NOT SET'}")

# Crear instancia del extractor para ver cuántas credenciales filtra
import sys
sys.path.append('.')

try:
    from arp_extractor import ARPExtractor
    extractor = ARPExtractor()
    print(f"\nCredenciales MikroTik cargadas: {len(extractor.mikrotik_credentials)}")
    print(f"Credenciales Ubiquiti cargadas: {len(extractor.ubiquiti_credentials)}")
    print(f"Total credenciales: {len(extractor.mikrotik_credentials + extractor.ubiquiti_credentials)}")
except Exception as e:
    print(f"Error: {e}")
