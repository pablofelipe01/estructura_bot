#!/usr/bin/env python3
# test_bot_corrected.py - Prueba con sintaxis corregida

import time
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from config import *

print("🧪 PRUEBA DEL BOT - VERSIÓN CORREGIDA")
print("="*50)

# Conectar
print("\n🔗 Conectando...")
iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
check, reason = iq.connect()

if not check:
    print(f"❌ Error: {reason}")
    exit()

iq.change_balance(ACCOUNT_TYPE)
balance_inicial = iq.get_balance()
print(f"✅ Conectado. Balance: ${balance_inicial:,.2f}")

# Hacer operación pequeña
print("\n📊 Haciendo operación de prueba ($1)...")
check, order_id = iq.buy(1, "EURUSD-OTC", "call", 1)

if check:
    print(f"✅ Orden creada: {order_id}")
    print(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
    print("⏳ Esperando 75 segundos...")
    
    for i in range(75, 0, -5):
        print(f"   {i}s...", end="\r")
        time.sleep(5)
    
    print("\n\n🔍 Verificando resultado...")
    
    # Método 1: get_position_history sin argumentos
    print("📋 Método 1: get_position_history()")
    try:
        history = iq.get_position_history()
        
        if history:
            found = False
            # Verificar si es dict con 'positions' o lista directa
            positions = history.get('positions', []) if isinstance(history, dict) else history
            
            for pos in positions[:20]:  # Revisar las últimas 20
                if str(pos.get('id')) == str(order_id):
                    found = True
                    print(f"\n✅ Orden encontrada!")
                    
                    # Extraer datos
                    win = pos.get('win', 'unknown')
                    amount = pos.get('amount', 0)
                    win_amount = pos.get('win_amount', 0)
                    status = pos.get('status', 'unknown')
                    
                    print(f"   Status: {status}")
                    print(f"   Win: {win}")
                    print(f"   Amount: ${amount}")
                    print(f"   Win Amount: ${win_amount}")
                    
                    # Interpretar resultado
                    if win == 'win':
                        profit = win_amount - amount
                        print(f"\n   🎯 RESULTADO: ✅ GANANCIA +${profit:.2f}")
                    elif win == 'loose':
                        print(f"\n   🎯 RESULTADO: ❌ PÉRDIDA -${amount:.2f}")
                    elif win == 'equal':
                        print(f"\n   🎯 RESULTADO: 🟡 EMPATE $0")
                    else:
                        print(f"\n   🎯 RESULTADO: ❓ {win}")
                    break
            
            if not found:
                print("❌ Orden no encontrada en historial")
                print("\n📋 Mostrando últimas 5 órdenes:")
                for i, pos in enumerate(positions[:5]):
                    print(f"   {i+1}. ID: {pos.get('id')}, Asset: {pos.get('active')}")
        else:
            print("❌ No se obtuvo historial")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Método 2: Verificar cambio en balance
    print("\n📋 Método 2: Verificación por balance")
    time.sleep(2)  # Esperar un poco más
    balance_final = iq.get_balance()
    diferencia = balance_final - balance_inicial
    
    print(f"   Balance inicial: ${balance_inicial:,.2f}")
    print(f"   Balance final: ${balance_final:,.2f}")
    print(f"   Diferencia: ${diferencia:+,.2f}")
    
    if diferencia > 0:
        print(f"   🎯 RESULTADO: ✅ GANANCIA")
    elif diferencia < 0:
        print(f"   🎯 RESULTADO: ❌ PÉRDIDA")
    else:
        print(f"   🎯 RESULTADO: 🟡 EMPATE")
    
else:
    print(f"❌ Error creando orden: {order_id}")

print("\n✅ Prueba completada")
print("="*50)