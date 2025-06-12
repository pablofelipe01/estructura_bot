# check_order_improved.py
# Script mejorado para verificar órdenes con mejor manejo de errores

import sys
import time
from datetime import datetime, timedelta
from iqoptionapi.stable_api import IQ_Option
from config import IQ_EMAIL, IQ_PASSWORD, ACCOUNT_TYPE

def check_order_multiple_methods(iqoption, order_id):
    """Probar múltiples métodos para obtener información de una orden"""
    print(f"\n🔍 Verificando orden: {order_id}")
    print("="*60)
    
    # Convertir ID a diferentes formatos por si acaso
    order_id_int = None
    try:
        order_id_int = int(order_id)
    except:
        pass
    
    # Método 1: check_win_v3 con timeout más corto
    print("\n📋 Método 1: check_win_v3")
    try:
        result = iqoption.check_win_v3(order_id)
        if result is not None:
            print(f"   ✅ Resultado: {result}")
            if result > 0:
                print(f"   Interpretación: GANANCIA (profit: ${result:,.2f})")
            elif result == 0:
                print(f"   Interpretación: EMPATE")
            else:
                print(f"   Interpretación: PÉRDIDA (${result:,.2f})")
        else:
            print("   ❌ Sin resultado")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Método 2: check_win (sin v3)
    print("\n📋 Método 2: check_win")
    try:
        if hasattr(iqoption, 'check_win'):
            result = iqoption.check_win(order_id)
            print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Método 3: get_optioninfo_v2
    print("\n📋 Método 3: get_optioninfo_v2")
    try:
        if hasattr(iqoption, 'get_optioninfo_v2'):
            result = iqoption.get_optioninfo_v2(10)  # Últimas 10 órdenes
            if result and isinstance(result, dict):
                # Buscar nuestra orden
                for key, value in result.items():
                    if str(key) == str(order_id) or (order_id_int and int(key) == order_id_int):
                        print(f"   ✅ Orden encontrada:")
                        print(f"   {value}")
                        break
                else:
                    print("   ❌ Orden no encontrada en las últimas operaciones")
        else:
            print("   ⚠️ Método no disponible")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Método 4: get_order (directo)
    print("\n📋 Método 4: get_order")
    try:
        if hasattr(iqoption, 'get_order'):
            result = iqoption.get_order(order_id)
            if result:
                print(f"   ✅ Resultado: {result}")
        else:
            print("   ⚠️ Método no disponible")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Método 5: Buscar en historial de posiciones
    print("\n📋 Método 5: Buscar en historial de posiciones")
    try:
        # Obtener historial de las últimas 24 horas
        history = iqoption.get_position_history("binary-option", 86400)  # 24 horas
        if history and isinstance(history, dict) and 'positions' in history:
            found = False
            for position in history['positions']:
                if str(position.get('id')) == str(order_id):
                    found = True
                    print(f"   ✅ Orden encontrada en historial:")
                    print(f"   Status: {position.get('status')}")
                    print(f"   Win: {position.get('win')}")
                    print(f"   Amount: ${position.get('amount', 0):,.2f}")
                    print(f"   Win Amount: ${position.get('win_amount', 0):,.2f}")
                    print(f"   Created: {position.get('created')}")
                    print(f"   Expired: {position.get('expired')}")
                    break
            if not found:
                print("   ❌ Orden no encontrada en historial de 24h")
        else:
            print("   ❌ No se pudo obtener historial")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def get_recent_orders_detailed(iqoption):
    """Obtener órdenes recientes con más detalle"""
    print("\n🔍 Buscando órdenes recientes...")
    print("="*60)
    
    try:
        # Método 1: get_position_history
        print("\n📋 Historial de posiciones (últimas 2 horas):")
        history = iqoption.get_position_history("binary-option", 7200)  # 2 horas
        
        if history and isinstance(history, dict):
            if 'positions' in history:
                positions = history['positions']
                print(f"   Total encontradas: {len(positions)}")
                
                # Mostrar las últimas 10
                for i, pos in enumerate(positions[:10]):
                    print(f"\n   Orden {i+1}:")
                    print(f"   ID: {pos.get('id')}")
                    print(f"   Asset: {pos.get('active')}")
                    print(f"   Direction: {pos.get('direction')}")
                    print(f"   Amount: ${pos.get('amount', 0):,.2f}")
                    print(f"   Status: {pos.get('status')}")
                    print(f"   Win: {pos.get('win')}")
                    print(f"   Win Amount: ${pos.get('win_amount', 0):,.2f}")
                    print(f"   Created: {pos.get('created')}")
                    print(f"   Expired: {pos.get('expired')}")
                    print(f"   Option Type: {pos.get('option_type')}")
            else:
                print("   ❌ No se encontraron posiciones")
        
        # Método 2: get_optioninfo_v2
        print("\n📋 Información de opciones recientes:")
        if hasattr(iqoption, 'get_optioninfo_v2'):
            options = iqoption.get_optioninfo_v2(10)
            if options:
                for order_id, info in list(options.items())[:5]:
                    print(f"\n   ID: {order_id}")
                    print(f"   Info: {info}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python check_order_improved.py <order_id>  - Verificar una orden")
        print("  python check_order_improved.py recent      - Ver órdenes recientes")
        print("  python check_order_improved.py test        - Hacer una operación de prueba")
        sys.exit(1)
    
    # Conectar
    print("🔗 Conectando a IQ Option...")
    iqoption = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
    check, reason = iqoption.connect()
    
    if not check:
        print(f"❌ Error al conectar: {reason}")
        sys.exit(1)
    
    print("✅ Conectado exitosamente")
    iqoption.change_balance(ACCOUNT_TYPE)
    
    command = sys.argv[1].lower()
    
    if command == "recent":
        get_recent_orders_detailed(iqoption)
    elif command == "test":
        # Hacer una operación de prueba pequeña
        print("\n🧪 Haciendo operación de prueba...")
        print("   Asset: EURUSD-OTC")
        print("   Amount: $1")
        print("   Direction: call")
        print("   Duration: 1 minuto")
        
        check, order_id = iqoption.buy(1, "EURUSD-OTC", "call", 1)
        if check:
            print(f"✅ Orden creada: {order_id}")
            print("⏳ Esperando 75 segundos para verificar resultado...")
            time.sleep(75)
            check_order_multiple_methods(iqoption, order_id)
        else:
            print(f"❌ Error creando orden: {order_id}")
    else:
        # Verificar orden específica
        check_order_multiple_methods(iqoption, command)

if __name__ == "__main__":
    main()