# test_orders.py
# Script para probar la detección de resultados de órdenes

import sys
import time
from iqoptionapi.stable_api import IQ_Option
from config import IQ_EMAIL, IQ_PASSWORD, ACCOUNT_TYPE

def test_order_detection(order_id):
    """Probar diferentes métodos de detección de resultados"""
    print(f"\n🔍 Probando detección de resultados para orden: {order_id}")
    print("="*60)
    
    # Conectar a IQ Option
    print("🔗 Conectando a IQ Option...")
    iqoption = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
    check, reason = iqoption.connect()
    
    if not check:
        print(f"❌ Error al conectar: {reason}")
        return
    
    print("✅ Conectado exitosamente")
    iqoption.change_balance(ACCOUNT_TYPE)
    
    # Método 1: get_async_order
    print("\n📋 Método 1: get_async_order")
    try:
        result = iqoption.get_async_order(order_id)
        if result:
            print(f"   Tipo de resultado: {type(result)}")
            if isinstance(result, dict):
                for key, value in sorted(result.items()):
                    print(f"   {key}: {value}")
            else:
                print(f"   Resultado: {result}")
        else:
            print("   ❌ No se obtuvo resultado")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Método 2: check_win_v3
    print("\n📋 Método 2: check_win_v3")
    try:
        result = iqoption.check_win_v3(order_id)
        print(f"   Resultado: {result}")
        if result is not None:
            if result > 0:
                print(f"   ✅ GANANCIA - Profit: ${result:,.2f}")
            elif result == 0:
                print(f"   🟡 EMPATE - Sin ganancia ni pérdida")
            else:
                print(f"   ❌ PÉRDIDA - Monto: ${result:,.2f}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Método 3: check_win_v4 (si existe)
    print("\n📋 Método 3: check_win_v4")
    try:
        if hasattr(iqoption, 'check_win_v4'):
            result = iqoption.check_win_v4(order_id)
            print(f"   Resultado: {result}")
        else:
            print("   ⚠️ check_win_v4 no disponible")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "="*60)

def get_recent_orders():
    """Obtener órdenes recientes para pruebas"""
    print("\n🔍 Buscando órdenes recientes...")
    print("="*60)
    
    # Conectar a IQ Option
    print("🔗 Conectando a IQ Option...")
    iqoption = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
    check, reason = iqoption.connect()
    
    if not check:
        print(f"❌ Error al conectar: {reason}")
        return
    
    print("✅ Conectado exitosamente")
    iqoption.change_balance(ACCOUNT_TYPE)
    
    # Intentar diferentes métodos para obtener historial
    methods = [
        ('get_position_history', lambda: iqoption.get_position_history("binary-option", 3600)),
        ('get_order_history', lambda: iqoption.get_order_history()),
        ('get_binary_options_history', lambda: iqoption.get_binary_options_history()),
        ('get_all_deals', lambda: iqoption.get_all_deals())
    ]
    
    for method_name, method in methods:
        if hasattr(iqoption, method_name):
            print(f"\n📋 Probando {method_name}...")
            try:
                result = method()
                if result:
                    print(f"✅ Encontradas órdenes:")
                    if isinstance(result, list):
                        for i, order in enumerate(result[:10]):  # Máximo 10
                            if isinstance(order, dict):
                                order_id = order.get('id', order.get('order_id', 'N/A'))
                                status = order.get('win', order.get('status', 'N/A'))
                                amount = order.get('amount', order.get('bet_amount', 'N/A'))
                                print(f"   {i+1}. ID: {order_id}, Status: {status}, Amount: {amount}")
                            else:
                                print(f"   {i+1}. {order}")
                    break
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python test_orders.py <order_id>  - Probar una orden específica")
        print("  python test_orders.py recent      - Ver órdenes recientes")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg.lower() == "recent":
        get_recent_orders()
    else:
        test_order_detection(arg)

if __name__ == "__main__":
    main()