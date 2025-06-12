# test_api_methods.py
# Script para descubrir la sintaxis correcta de get_position_history

import inspect
from iqoptionapi.stable_api import IQ_Option
from config import IQ_EMAIL, IQ_PASSWORD, ACCOUNT_TYPE

print("🔍 DESCUBRIENDO LA SINTAXIS CORRECTA DE LA API")
print("="*50)

# Conectar
iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
check, reason = iq.connect()

if not check:
    print(f"❌ Error: {reason}")
    exit()

iq.change_balance(ACCOUNT_TYPE)
print(f"✅ Conectado. Balance: ${iq.get_balance():,.2f}")

# Inspeccionar get_position_history
print("\n📋 Inspeccionando get_position_history:")
try:
    # Ver la firma del método
    sig = inspect.signature(iq.get_position_history)
    print(f"   Firma: {sig}")
    
    # Ver el docstring si existe
    if iq.get_position_history.__doc__:
        print(f"   Doc: {iq.get_position_history.__doc__}")
    
    # Probar diferentes formas de llamarlo
    print("\n🧪 Probando diferentes sintaxis:")
    
    # Opción 1: Sin argumentos
    print("   1. Sin argumentos:")
    try:
        result = iq.get_position_history()
        print(f"      ✅ Funciona! Tipo: {type(result)}")
        if result:
            print(f"      Contenido: {list(result.keys()) if isinstance(result, dict) else 'Lista'}")
    except Exception as e:
        print(f"      ❌ Error: {str(e)}")
    
    # Opción 2: Solo tipo de instrumento
    print("\n   2. Solo tipo de instrumento:")
    for instrument in ["binary-option", "digital-option", "binary", "turbo"]:
        try:
            result = iq.get_position_history(instrument)
            print(f"      ✅ '{instrument}' funciona!")
            break
        except Exception as e:
            print(f"      ❌ '{instrument}': {str(e)}")
    
    # Opción 3: Con límite
    print("\n   3. Con límite (keyword argument):")
    try:
        result = iq.get_position_history(limit=10)
        print(f"      ✅ Funciona con limit!")
    except Exception as e:
        print(f"      ❌ Error: {str(e)}")
    
except Exception as e:
    print(f"❌ Error inspeccionando: {str(e)}")

# Buscar métodos alternativos
print("\n📋 Métodos alternativos para obtener historial:")
history_methods = [m for m in dir(iq) if 'history' in m.lower() or 'position' in m.lower()]
for method in history_methods:
    if not method.startswith('_'):
        print(f"   - {method}")

# Probar get_positions
print("\n🧪 Probando get_positions (si existe):")
if hasattr(iq, 'get_positions'):
    try:
        positions = iq.get_positions()
        print(f"   ✅ get_positions funciona!")
        print(f"   Tipo: {type(positions)}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

# Probar all_positions_closed
print("\n🧪 Probando all_positions_closed (si existe):")
if hasattr(iq, 'all_positions_closed'):
    try:
        closed = iq.all_positions_closed
        print(f"   ✅ all_positions_closed funciona!")
        print(f"   Tipo: {type(closed)}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

print("\n" + "="*50)