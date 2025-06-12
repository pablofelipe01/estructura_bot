# find_history.py
# Encontrar el método correcto para obtener el historial

import time
from iqoptionapi.stable_api import IQ_Option
from config import *

print("🔍 BUSCANDO EL MÉTODO CORRECTO PARA HISTORIAL")
print("="*60)

# Conectar
iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
check, reason = iq.connect()

if not check:
    print(f"❌ Error: {reason}")
    exit()

iq.change_balance(ACCOUNT_TYPE)
balance = iq.get_balance()
print(f"✅ Conectado. Balance: ${balance:,.2f}")

# Hacer una operación pequeña para tener algo que buscar
print("\n📊 Haciendo operación de prueba...")
check, order_id = iq.buy(1, "EURUSD-OTC", "call", 1)

if check:
    print(f"✅ Orden creada: {order_id}")
    print("⏳ Esperando 75 segundos...")
    
    for i in range(75, 0, -5):
        print(f"   {i}s...", end="\r")
        time.sleep(5)
else:
    print(f"❌ Error: {order_id}")
    order_id = None

print("\n\n🔍 PROBANDO TODOS LOS MÉTODOS POSIBLES:")

# Lista de métodos relacionados con historial
methods_to_try = []

# Buscar todos los métodos que puedan tener historial
for attr in dir(iq):
    if not attr.startswith('_'):
        lower_attr = attr.lower()
        if any(word in lower_attr for word in ['history', 'position', 'order', 'deal', 'option']):
            methods_to_try.append(attr)

print(f"\n📋 Métodos encontrados: {len(methods_to_try)}")

# Probar cada método
for method_name in sorted(methods_to_try):
    print(f"\n🔹 {method_name}:")
    
    method = getattr(iq, method_name)
    
    # Si no es callable, es una propiedad
    if not callable(method):
        try:
            result = method
            print(f"   Tipo: {type(result)} (propiedad)")
            if result:
                if isinstance(result, (list, dict, tuple)):
                    print(f"   Contenido: {str(result)[:200]}...")
                else:
                    print(f"   Valor: {result}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        continue
    
    # Si es callable, probar con diferentes argumentos
    # Sin argumentos
    try:
        result = method()
        print(f"   Sin args: {type(result)}")
        if result and order_id:
            # Buscar nuestra orden
            if isinstance(result, dict):
                if str(order_id) in str(result):
                    print(f"   ✅ ENCONTRÓ LA ORDEN {order_id}!")
            elif isinstance(result, list):
                for item in result:
                    if str(order_id) in str(item):
                        print(f"   ✅ ENCONTRÓ LA ORDEN {order_id}!")
                        print(f"   Item: {item}")
                        break
    except TypeError:
        # Necesita argumentos
        # Probar con "binary-option"
        try:
            result = method("binary-option")
            print(f"   Con 'binary-option': {type(result)}")
            
            # Si es tupla, analizar
            if isinstance(result, tuple):
                print(f"   Tupla con {len(result)} elementos")
                for i, elem in enumerate(result):
                    print(f"      Elemento {i}: {type(elem)}")
                    if isinstance(elem, list) and elem:
                        if isinstance(elem[0], dict):
                            print(f"         Lista con {len(elem)} dicts")
                            # Buscar nuestra orden
                            if order_id:
                                for item in elem:
                                    if str(order_id) in str(item.get('id', '')):
                                        print(f"         ✅ ORDEN {order_id} ENCONTRADA!")
                                        print(f"         Datos: {item}")
                                        break
                                        
        except Exception as e:
            # Probar con más argumentos
            if "missing" in str(e):
                print(f"   Necesita más argumentos: {str(e)}")
            else:
                print(f"   Error: {str(e)[:100]}")
    except Exception as e:
        print(f"   Error: {str(e)[:100]}")

# Verificar balance final
print("\n\n📊 VERIFICACIÓN POR BALANCE:")
new_balance = iq.get_balance()
diff = new_balance - balance
print(f"Balance inicial: ${balance:,.2f}")
print(f"Balance final: ${new_balance:,.2f}")
print(f"Diferencia: ${diff:+,.2f}")

if diff > 0:
    print("✅ La operación fue GANADORA")
elif diff < 0:
    print("❌ La operación fue PERDEDORA")
else:
    print("🟡 La operación fue EMPATE o aún no se procesó")

print("\n✅ Búsqueda completada")
print("="*60)