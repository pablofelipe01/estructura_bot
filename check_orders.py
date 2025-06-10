#!/usr/bin/env python3
# check_orders.py - Verificar resultados de órdenes específicas

from iqoptionapi.stable_api import IQ_Option
from config import IQ_EMAIL, IQ_PASSWORD, ACCOUNT_TYPE
import time
import json
from datetime import datetime

def check_order(iq, order_id):
    """Verificar el resultado de una orden específica"""
    
    print(f"\n🔍 Verificando orden {order_id}...")
    
    # Método 1: get_async_order
    print("\n📋 Método 1: get_async_order")
    try:
        result = iq.get_async_order(order_id)
        if result:
            print("✅ Resultado encontrado:")
            print(json.dumps(result, indent=2))
            return result
        else:
            print("❌ No se encontró resultado con get_async_order")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Método 2: check_win_v3
    print("\n📋 Método 2: check_win_v3")
    try:
        result = iq.check_win_v3(order_id)
        if result is not None:
            print(f"✅ Resultado: {result}")
            if result > 0:
                print("✅ GANADORA")
            elif result == 0:
                print("🟡 EMPATE o ❌ PERDIDA")
            else:
                print("❌ PERDIDA")
            return result
        else:
            print("❌ No se encontró resultado con check_win_v3")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Método 3: get_order
    print("\n📋 Método 3: get_order")
    try:
        result = iq.get_order(order_id)
        if result:
            print("✅ Resultado encontrado:")
            print(json.dumps(result, indent=2))
            return result
        else:
            print("❌ No se encontró resultado con get_order")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Método 4: Historial de operaciones
    print("\n📋 Método 4: Buscando en historial...")
    try:
        # Obtener historial reciente
        end_time = time.time()
        start_time = end_time - (24 * 60 * 60)  # Últimas 24 horas
        
        history = iq.get_position_history_v2("binary-option", 100, start_time, end_time, 0, 0)
        
        if history and "positions" in history:
            print(f"📊 Total de posiciones en historial: {len(history['positions'])}")
            
            # Buscar la orden específica
            for position in history["positions"]:
                if position.get("id") == order_id or position.get("order_id") == order_id:
                    print("\n✅ Orden encontrada en historial:")
                    print(json.dumps(position, indent=2))
                    return position
            
            print(f"❌ Orden {order_id} no encontrada en las últimas 100 operaciones")
            
            # Mostrar algunas órdenes recientes para referencia
            print("\n📋 Últimas 5 órdenes:")
            for i, position in enumerate(history["positions"][:5]):
                order_time = datetime.fromtimestamp(position.get("create_time", 0))
                print(f"  {i+1}. ID: {position.get('id')} - {position.get('active')} - {order_time} - ${position.get('amount')}")
        else:
            print("❌ No se pudo obtener el historial")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Método 5: Buscar en operaciones cerradas
    print("\n📋 Método 5: Buscando en operaciones cerradas...")
    try:
        # Intentar obtener las operaciones cerradas del día
        closed_options = iq.get_optioninfo_v2(10)  # Últimas 10 operaciones
        
        if closed_options and "msg" in closed_options:
            options = closed_options["msg"]
            for opt in options:
                if opt.get("id") == order_id:
                    print("\n✅ Orden encontrada en operaciones cerradas:")
                    print(json.dumps(opt, indent=2))
                    return opt
        else:
            print("❌ No se encontró en operaciones cerradas")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return None

def check_recent_trades(iq):
    """Mostrar operaciones recientes"""
    print("\n📊 OPERACIONES RECIENTES:")
    print("=" * 60)
    
    try:
        # get_position_history_v2 solo necesita tipo de asset y límite
        history = iq.get_position_history_v2("binary-option", 20)
        
        if history and "positions" in history:
            positions = history["positions"]
            print(f"📋 Mostrando las últimas {len(positions)} operaciones:\n")
            
            for i, position in enumerate(positions):
                order_id = position.get("id")
                active = position.get("active")
                amount = position.get("amount", 0)
                create_time = position.get("create_time", 0)
                close_time = position.get("close_time", 0)
                
                # Determinar el resultado
                win_amount = position.get("win_amount", 0)
                profit = win_amount - amount if win_amount > 0 else -amount
                
                if win_amount > amount:
                    status = "✅ WIN"
                elif win_amount == amount:
                    status = "🟡 TIE"
                elif win_amount > 0:
                    status = "❓ PARTIAL"
                else:
                    status = "❌ LOSS"
                
                create_dt = datetime.fromtimestamp(create_time) if create_time else "N/A"
                close_dt = datetime.fromtimestamp(close_time) if close_time else "N/A"
                
                print(f"{i+1}. {active} - {status}")
                print(f"   ID: {order_id}")
                print(f"   Monto: ${amount:,.2f}")
                print(f"   Creada: {create_dt}")
                print(f"   Cerrada: {close_dt}")
                print(f"   Win Amount: ${win_amount:,.2f}")
                print(f"   Resultado: ${profit:+,.2f}")
                print("-" * 40)
        else:
            print("❌ No se pudo obtener el historial")
            print(f"Respuesta: {history}")
    except Exception as e:
        print(f"❌ Error obteniendo historial: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal"""
    print("=" * 60)
    print("   VERIFICADOR DE ÓRDENES IQ OPTION")
    print("=" * 60)
    
    # Conectar a IQ Option
    print("\n🔗 Conectando a IQ Option...")
    iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
    login_status, login_reason = iq.connect()
    
    if not login_status:
        print(f"❌ Error al conectar: {login_reason}")
        return
    
    print("✅ Conexión exitosa")
    iq.change_balance(ACCOUNT_TYPE)
    balance = iq.get_balance()
    print(f"💰 Balance actual: ${balance:,.2f}")
    
    while True:
        print("\n" + "=" * 60)
        print("Opciones:")
        print("1. Verificar orden por ID")
        print("2. Ver operaciones recientes")
        print("3. Salir")
        
        choice = input("\nElige una opción (1-3): ").strip()
        
        if choice == "1":
            order_id = input("Ingresa el ID de la orden: ").strip()
            try:
                check_order(iq, int(order_id))
            except ValueError:
                print("❌ ID inválido. Debe ser un número.")
        
        elif choice == "2":
            check_recent_trades(iq)
        
        elif choice == "3":
            break
        
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()