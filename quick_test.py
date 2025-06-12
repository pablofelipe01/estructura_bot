# quick_test.py
# Script rápido para probar que la detección de resultados funciona

import time
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from config import IQ_EMAIL, IQ_PASSWORD, ACCOUNT_TYPE

def test_order_detection():
    """Hacer una operación de prueba y verificar el resultado"""
    print("="*60)
    print("🧪 PRUEBA DE DETECCIÓN DE RESULTADOS")
    print("="*60)
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Conectar
    print("\n🔗 Conectando a IQ Option...")
    iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
    check, reason = iq.connect()
    
    if not check:
        print(f"❌ Error al conectar: {reason}")
        return
    
    print("✅ Conexión exitosa")
    iq.change_balance(ACCOUNT_TYPE)
    balance = iq.get_balance()
    print(f"💰 Balance actual: ${balance:,.2f}")
    
    # Configuración de prueba
    test_amount = 1  # $1 para minimizar riesgo
    test_asset = "EURUSD-OTC"  # Asset confiable 24/7
    test_direction = "call"
    test_duration = 1  # 1 minuto
    
    print(f"\n📊 Configuración de prueba:")
    print(f"   Asset: {test_asset}")
    print(f"   Monto: ${test_amount}")
    print(f"   Dirección: {test_direction}")
    print(f"   Duración: {test_duration} minuto")
    
    # Hacer la operación
    print(f"\n🎯 Colocando orden...")
    check, order_id = iq.buy(test_amount, test_asset, test_direction, test_duration)
    
    if not check:
        print(f"❌ Error al colocar orden: {order_id}")
        return
    
    print(f"✅ Orden colocada exitosamente")
    print(f"📝 ID de orden: {order_id}")
    print(f"⏰ Hora de entrada: {datetime.now().strftime('%H:%M:%S')}")
    
    # Esperar a que expire + margen
    wait_time = (test_duration * 60) + 15  # duración + 15 segundos de margen
    print(f"\n⏳ Esperando {wait_time} segundos para que expire...")
    
    for i in range(wait_time, 0, -10):
        print(f"   Quedan {i} segundos...", end='\r')
        time.sleep(10)
    
    print("\n\n🔍 Verificando resultado...")
    print("-"*40)
    
    # Método 1: check_win_v3
    print("📋 Método 1: check_win_v3")
    try:
        result = iq.check_win_v3(order_id)
        print(f"   Resultado raw: {result}")
        
        if result is not None:
            if result > 0:
                print(f"   ✅ GANANCIA - Profit: ${result}")
                print(f"   Retorno total: ${test_amount + result}")
            elif result == 0:
                print(f"   🟡 EMPATE - Sin ganancia ni pérdida")
            else:
                print(f"   ❌ PÉRDIDA - Monto: ${abs(result)}")
        else:
            print("   ⚠️ No se obtuvo resultado")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Método 2: Buscar en historial
    print("\n📋 Método 2: Historial de posiciones")
    try:
        history = iq.get_position_history("binary-option", 300)  # Últimos 5 minutos
        
        if history and 'positions' in history:
            found = False
            for pos in history['positions']:
                if str(pos.get('id')) == str(order_id):
                    found = True
                    print(f"   ✅ Orden encontrada:")
                    print(f"   Win: {pos.get('win')}")
                    print(f"   Win Amount: ${pos.get('win_amount', 0)}")
                    print(f"   Status: {pos.get('status')}")
                    break
            
            if not found:
                print("   ❌ No encontrada en historial")
        else:
            print("   ❌ No se pudo obtener historial")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Balance final
    print("\n" + "-"*40)
    new_balance = iq.get_balance()
    profit_loss = new_balance - balance
    print(f"💰 Balance inicial: ${balance:,.2f}")
    print(f"💰 Balance final: ${new_balance:,.2f}")
    print(f"📊 Resultado neto: ${profit_loss:+,.2f}")
    
    print("\n" + "="*60)
    print("✅ Prueba completada")
    print("="*60)

if __name__ == "__main__":
    test_order_detection()