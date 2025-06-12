#!/usr/bin/env python3
# test_fixed_bot.py - Prueba rápida del bot arreglado

import time
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from config import *

print("🧪 PRUEBA RÁPIDA DEL BOT ARREGLADO")
print("="*50)

# Conectar
print("\n🔗 Conectando...")
iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
check, reason = iq.connect()

if not check:
    print(f"❌ Error: {reason}")
    exit()

iq.change_balance(ACCOUNT_TYPE)
print(f"✅ Conectado. Balance: ${iq.get_balance():,.2f}")

# Hacer operación pequeña
print("\n📊 Haciendo operación de prueba ($1)...")
check, order_id = iq.buy(1, "EURUSD-OTC", "call", 1)

if check:
    print(f"✅ Orden creada: {order_id}")
    print("⏳ Esperando 75 segundos...")
    
    for i in range(75, 0, -5):
        print(f"   {i}s...", end="\r")
        time.sleep(5)
    
    # Verificar con historial (método seguro)
    print("\n\n🔍 Verificando resultado...")
    history = iq.get_position_history("binary-option", 300)
    
    if history and 'positions' in history:
        for pos in history['positions']:
            if str(pos.get('id')) == str(order_id):
                win = pos.get('win')
                amount = pos.get('amount', 0)
                win_amount = pos.get('win_amount', 0)
                
                print(f"\n📊 RESULTADO:")
                print(f"   Status: {win}")
                print(f"   Monto: ${amount}")
                print(f"   Retorno: ${win_amount}")
                
                if win == 'win':
                    print(f"   ✅ GANANCIA: +${win_amount - amount:.2f}")
                elif win == 'loose':
                    print(f"   ❌ PÉRDIDA: -${amount:.2f}")
                elif win == 'equal':
                    print(f"   🟡 EMPATE: $0")
                break
        else:
            print("❌ Orden no encontrada en historial")
else:
    print(f"❌ Error creando orden: {order_id}")

print("\n✅ Prueba completada")
