#!/usr/bin/env python3
# test_working_bot.py - Versión funcional con el formato correcto

import time
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from config import *

print("🧪 BOT DE PRUEBA - VERSIÓN FUNCIONAL")
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
    
    # Obtener historial
    history = iq.get_position_history("binary-option")
    
    # Manejar el formato tupla
    positions = []
    if isinstance(history, tuple):
        # Buscar la lista de posiciones en la tupla
        for element in history:
            if isinstance(element, list) and element:
                # Verificar si es una lista de posiciones
                if isinstance(element[0], dict) and 'id' in element[0]:
                    positions = element
                    print(f"✅ Encontradas {len(positions)} posiciones")
                    break
    elif isinstance(history, list):
        positions = history
    
    # Buscar nuestra orden
    found = False
    if positions:
        for pos in positions[:30]:  # Revisar las últimas 30
            if str(pos.get('id')) == str(order_id):
                found = True
                print(f"\n✅ ORDEN ENCONTRADA!")
                
                # Extraer todos los datos
                win = pos.get('win', 'unknown')
                amount = pos.get('amount', 0)
                win_amount = pos.get('win_amount', 0)
                status = pos.get('status', 'unknown')
                active = pos.get('active', 'unknown')
                direction = pos.get('direction', 'unknown')
                
                print(f"\n📊 Detalles de la orden:")
                print(f"   ID: {order_id}")
                print(f"   Asset: {active}")
                print(f"   Direction: {direction}")
                print(f"   Status: {status}")
                print(f"   Amount: ${amount:.2f}")
                print(f"   Win: {win}")
                print(f"   Win Amount: ${win_amount:.2f}")
                
                # Interpretar resultado
                print(f"\n🎯 RESULTADO FINAL:")
                if win == 'win':
                    profit = win_amount - amount
                    print(f"   ✅ GANANCIA: +${profit:.2f}")
                    print(f"   Retorno total: ${win_amount:.2f}")
                elif win == 'loose':
                    print(f"   ❌ PÉRDIDA: -${amount:.2f}")
                elif win == 'equal':
                    print(f"   🟡 EMPATE: $0")
                else:
                    print(f"   ❓ Estado desconocido: {win}")
                break
    
    if not found:
        print("\n❌ Orden no encontrada")
        print("\n📋 Mostrando últimas 5 órdenes:")
        for i, pos in enumerate(positions[:5]):
            win = pos.get('win', '?')
            emoji = "✅" if win == 'win' else "❌" if win == 'loose' else "🟡"
            print(f"   {i+1}. {emoji} ID: {pos.get('id')} | {pos.get('active')} | ${pos.get('amount', 0):.2f}")
    
    # Verificación por balance
    print("\n📊 Verificación por balance:")
    balance_final = iq.get_balance()
    diferencia = balance_final - balance_inicial
    
    print(f"   Balance inicial: ${balance_inicial:,.2f}")
    print(f"   Balance final: ${balance_final:,.2f}")
    print(f"   Diferencia: ${diferencia:+,.2f}")
    
else:
    print(f"❌ Error creando orden: {order_id}")

print("\n✅ Prueba completada")
print("="*50)