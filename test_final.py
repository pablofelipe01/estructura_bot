# test_final.py
# Prueba final con detección mejorada

import time
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from config import *

print("🧪 PRUEBA FINAL - DETECCIÓN COMPLETA")
print("="*60)

# Conectar
iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
check, reason = iq.connect()

if not check:
    print(f"❌ Error: {reason}")
    exit()

iq.change_balance(ACCOUNT_TYPE)
balance_inicial = iq.get_balance()
print(f"✅ Conectado. Balance: ${balance_inicial:,.2f}")
print(f"📊 Tipo de cuenta: {'DEMO' if ACCOUNT_TYPE == 'PRACTICE' else 'REAL'}")

# Hacer operación
print("\n📊 Haciendo operación de prueba ($1)...")
check, order_id = iq.buy(1, "EURUSD-OTC", "call", 1)

if check:
    print(f"✅ Orden creada: {order_id}")
    print("⏳ Esperando 75 segundos...")
    
    for i in range(75, 0, -5):
        print(f"   {i}s...", end="\r")
        time.sleep(5)
    
    print("\n\n🔍 Verificando resultado...")
    
    # Verificar en order_binary
    if hasattr(iq.api, 'order_binary') and order_id in iq.api.order_binary:
        order_data = iq.api.order_binary[order_id]
        print(f"\n✅ Orden encontrada en order_binary:")
        
        # Mostrar campos clave
        result = order_data.get('result', 'unknown')
        amount = order_data.get('amount', 0)
        profit_percent = order_data.get('profit_percent', 0)
        win_amount = order_data.get('win_enrolled_amount', 0)
        
        print(f"   Result: {result}")
        print(f"   Amount: ${amount}")
        print(f"   Profit %: {profit_percent}%")
        print(f"   Win Amount: ${win_amount}")
        
        # Interpretar resultado
        print(f"\n🎯 RESULTADO FINAL:")
        if result == 'win':
            profit = amount * (profit_percent / 100)
            print(f"   ✅ VICTORIA")
            print(f"   Profit: ${profit:.2f}")
            print(f"   Retorno total: ${amount + profit:.2f}")
        elif result == 'loose':
            print(f"   ❌ PÉRDIDA")
            print(f"   Pérdida: ${amount}")
        elif result == 'equal':
            print(f"   🟡 EMPATE")
            print(f"   Sin ganancia ni pérdida")
        else:
            print(f"   ❓ Resultado desconocido: {result}")
    else:
        print("❌ Orden no encontrada en order_binary")
    
    # Verificar balance también
    print(f"\n📊 Verificación por balance:")
    balance_final = iq.get_balance()
    diff = balance_final - balance_inicial
    print(f"   Inicial: ${balance_inicial:,.2f}")
    print(f"   Final: ${balance_final:,.2f}")
    print(f"   Diferencia: ${diff:+,.2f}")
    
    if ACCOUNT_TYPE == "PRACTICE" and diff == 0:
        print("   ℹ️ Nota: En cuenta DEMO el balance puede no cambiar inmediatamente")

else:
    print(f"❌ Error: {order_id}")

print("\n✅ Prueba completada")
print("="*60)