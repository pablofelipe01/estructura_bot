# discover_format.py
# Script para descubrir el formato exacto de get_position_history

import time
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from config import *

print("🔍 DESCUBRIENDO FORMATO DE HISTORIAL")
print("="*50)

# Conectar
iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
check, reason = iq.connect()

if not check:
    print(f"❌ Error: {reason}")
    exit()

iq.change_balance(ACCOUNT_TYPE)
print(f"✅ Conectado. Balance: ${iq.get_balance():,.2f}")

# Obtener historial
print("\n📋 Obteniendo historial...")
history = iq.get_position_history("binary-option")

print(f"\n📊 Análisis del resultado:")
print(f"   Tipo: {type(history)}")
print(f"   Longitud: {len(history) if hasattr(history, '__len__') else 'N/A'}")

# Si es tupla, mostrar cada elemento
if isinstance(history, tuple):
    print(f"\n📋 Contenido de la tupla:")
    for i, element in enumerate(history):
        print(f"\n   Elemento {i}:")
        print(f"   Tipo: {type(element)}")
        
        # Si es lista o dict, mostrar más detalles
        if isinstance(element, list):
            print(f"   Longitud: {len(element)}")
            if element:
                print(f"   Primer elemento: {element[0]}")
                # Si el primer elemento es un dict con info de posición
                if isinstance(element[0], dict):
                    print(f"\n   📊 Campos disponibles:")
                    for key in element[0].keys():
                        print(f"      - {key}: {element[0][key]}")
                    
                    # Buscar órdenes ganadoras
                    print(f"\n   🎯 Últimas 5 posiciones:")
                    for j, pos in enumerate(element[:5]):
                        win = pos.get('win', 'unknown')
                        amount = pos.get('amount', 0)
                        win_amount = pos.get('win_amount', 0)
                        
                        # Determinar emoji según resultado
                        if win == 'win':
                            emoji = "✅"
                            result = f"+${win_amount - amount:.2f}"
                        elif win == 'loose':
                            emoji = "❌"
                            result = f"-${amount:.2f}"
                        else:
                            emoji = "🟡"
                            result = "$0"
                        
                        print(f"      {j+1}. {emoji} ID: {pos.get('id')} | {pos.get('active')} | {result}")
                        
        elif isinstance(element, dict):
            print(f"   Claves: {list(element.keys())}")
        else:
            print(f"   Valor: {element}")

# Probar get_position_history_v2 con argumentos
print("\n\n📋 Probando get_position_history_v2:")
if hasattr(iq, 'get_position_history_v2'):
    try:
        # Intentar con argumentos básicos
        limit = 10
        offset = 0
        start = int(time.time() - 3600)  # Hace 1 hora
        end = int(time.time())  # Ahora
        
        print(f"   Argumentos: limit={limit}, offset={offset}, start={start}, end={end}")
        history_v2 = iq.get_position_history_v2("binary-option", limit, offset, start, end)
        
        print(f"   ✅ Funciona!")
        print(f"   Tipo: {type(history_v2)}")
        
        if isinstance(history_v2, dict):
            print(f"   Claves: {list(history_v2.keys())}")
        elif isinstance(history_v2, list):
            print(f"   Longitud: {len(history_v2)}")
            if history_v2:
                print(f"   Primer elemento: {history_v2[0]}")
                
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

# Buscar métodos relacionados
print("\n\n📋 Otros métodos de posiciones disponibles:")
position_methods = [m for m in dir(iq) if 'position' in m.lower() and not m.startswith('_')]
for method in position_methods:
    print(f"   - {method}")

print("\n✅ Análisis completado")
print("="*50)