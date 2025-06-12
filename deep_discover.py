# deep_discover.py
# Descubrir la estructura EXACTA de la tupla

import json
from iqoptionapi.stable_api import IQ_Option
from config import *

print("🔍 DESCUBRIENDO ESTRUCTURA EXACTA DE LA TUPLA")
print("="*60)

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

print(f"\n📊 ANÁLISIS PROFUNDO:")
print(f"Tipo principal: {type(history)}")

if isinstance(history, tuple):
    print(f"Longitud de la tupla: {len(history)}")
    
    # Analizar cada elemento de la tupla
    for i, element in enumerate(history):
        print(f"\n🔹 ELEMENTO {i}:")
        print(f"   Tipo: {type(element)}")
        
        # Si es None
        if element is None:
            print("   Valor: None")
            continue
            
        # Si es string
        if isinstance(element, str):
            print(f"   Valor: '{element}'")
            continue
            
        # Si es número
        if isinstance(element, (int, float)):
            print(f"   Valor: {element}")
            continue
            
        # Si es bool
        if isinstance(element, bool):
            print(f"   Valor: {element}")
            continue
            
        # Si es lista
        if isinstance(element, list):
            print(f"   Longitud lista: {len(element)}")
            if element:
                print(f"   Tipo del primer elemento: {type(element[0])}")
                
                # Si el primer elemento es dict
                if isinstance(element[0], dict):
                    print("   🎯 POSIBLE LISTA DE POSICIONES!")
                    print(f"   Claves del primer dict: {list(element[0].keys())}")
                    
                    # Mostrar primer elemento completo
                    print("\n   📊 PRIMER ELEMENTO COMPLETO:")
                    for key, value in element[0].items():
                        print(f"      {key}: {value}")
                    
                    # Verificar si tiene campos esperados
                    expected_fields = ['id', 'win', 'amount', 'win_amount', 'active']
                    has_fields = all(field in element[0] for field in expected_fields)
                    
                    if has_fields:
                        print("\n   ✅ CONFIRMADO: Esta es la lista de posiciones!")
                        print(f"   Total posiciones: {len(element)}")
                        
                        # Mostrar últimas 3 posiciones
                        print("\n   📋 ÚLTIMAS 3 POSICIONES:")
                        for j, pos in enumerate(element[:3]):
                            win = pos.get('win', '?')
                            emoji = "✅" if win == 'win' else "❌" if win == 'loose' else "🟡"
                            print(f"      {j+1}. {emoji} ID: {pos.get('id')} | {pos.get('active')} | ${pos.get('amount', 0)}")
                else:
                    # Mostrar primeros elementos
                    print(f"   Primeros 3 elementos: {element[:3]}")
                    
        # Si es dict
        elif isinstance(element, dict):
            print(f"   Claves del dict: {list(element.keys())}")
            # Si es pequeño, mostrarlo completo
            if len(element) < 10:
                print(f"   Contenido: {element}")
        
        # Si es otro tipo
        else:
            print(f"   Valor: {str(element)[:100]}...")

# También probar otros métodos
print("\n\n📋 PROBANDO MÉTODOS ALTERNATIVOS:")

# get_positions
if hasattr(iq, 'get_positions'):
    print("\n🔹 get_positions:")
    try:
        # Probar con diferentes argumentos
        for arg in ["binary-option", "turbo-option", "all"]:
            try:
                result = iq.get_positions(arg)
                print(f"   get_positions('{arg}'): {type(result)}")
                if result:
                    print(f"   Contenido: {result}")
                    break
            except:
                pass
    except Exception as e:
        print(f"   Error: {str(e)}")

# all_positions_closed
if hasattr(iq, 'all_positions_closed'):
    print("\n🔹 all_positions_closed:")
    try:
        result = iq.all_positions_closed
        print(f"   Tipo: {type(result)}")
        if result:
            print(f"   Contenido: {result}")
    except Exception as e:
        print(f"   Error: {str(e)}")

print("\n✅ Análisis completado")
print("="*60)