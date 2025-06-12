# minimal_test.py
# Test mínimo para verificar que no hay bloqueos

import time
from iqoptionapi.stable_api import IQ_Option
from config import IQ_EMAIL, IQ_PASSWORD, ACCOUNT_TYPE

print("🧪 TEST MÍNIMO - SIN BLOQUEOS")
print("="*40)

# Conectar
iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
check, reason = iq.connect()

if not check:
    print(f"❌ Error: {reason}")
    exit()

iq.change_balance(ACCOUNT_TYPE)
print(f"✅ Conectado. Balance: ${iq.get_balance():,.2f}")

# Test 1: Historial (método seguro)
print("\n📋 Test 1: Historial de posiciones (SEGURO)")
try:
    start = time.time()
    history = iq.get_position_history("binary-option", 300)
    elapsed = time.time() - start
    
    if history and 'positions' in history:
        print(f"✅ Funciona! ({elapsed:.2f}s)")
        print(f"   Órdenes encontradas: {len(history['positions'])}")
    else:
        print(f"⚠️ Sin datos ({elapsed:.2f}s)")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 2: get_async_order (generalmente seguro)
print("\n📋 Test 2: get_async_order")
try:
    start = time.time()
    # Usar un ID ficticio
    result = iq.get_async_order("12345678900")
    elapsed = time.time() - start
    print(f"✅ No se bloqueó ({elapsed:.2f}s)")
    print(f"   Resultado: {result}")
except Exception as e:
    print(f"⚠️ Error controlado: {str(e)}")

# Test 3: check_win_v3 (PELIGROSO - con timeout manual)
print("\n📋 Test 3: check_win_v3 (PELIGROSO)")
print("⚠️ Este método puede bloquearse...")

import threading
result = [None]
error = [None]

def test_check_win():
    try:
        result[0] = iq.check_win_v3("12345678900")
    except Exception as e:
        error[0] = str(e)

# Ejecutar en thread con timeout
thread = threading.Thread(target=test_check_win)
thread.daemon = True
thread.start()
thread.join(3)  # Esperar máximo 3 segundos

if thread.is_alive():
    print("❌ BLOQUEADO! El método check_win_v3 causa bloqueos")
    print("🚨 NO USES check_win_v3 en el bot")
else:
    if error[0]:
        print(f"⚠️ Error: {error[0]}")
    else:
        print(f"✅ Completó sin bloqueo: {result[0]}")

print("\n" + "="*40)
print("📊 RESUMEN:")
print("✅ USA: get_position_history (seguro y confiable)")
print("⚠️ EVITA: check_win_v3 (causa bloqueos)")
print("="*40)