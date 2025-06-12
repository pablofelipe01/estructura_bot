# verify_orders_fixed.py
# Verificación de órdenes evitando métodos que causan bloqueos

import sys
import time
import threading
from datetime import datetime, timedelta
from iqoptionapi.stable_api import IQ_Option
from config import IQ_EMAIL, IQ_PASSWORD, ACCOUNT_TYPE

class OrderVerifier:
    def __init__(self, iqoption):
        self.iq = iqoption
        self.result = None
        
    def check_with_timeout(self, func, args, timeout=5):
        """Ejecutar función con timeout para evitar bloqueos"""
        self.result = None
        
        def target():
            try:
                self.result = func(*args)
            except Exception as e:
                self.result = f"Error: {str(e)}"
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            return None, "Timeout"
        return self.result, "OK"

def verify_order_safe(iq, order_id):
    """Verificar orden de forma segura sin bloqueos"""
    print(f"\n🔍 Verificando orden: {order_id}")
    print("="*60)
    
    verifier = OrderVerifier(iq)
    
    # Método 1: Historial de posiciones (más confiable)
    print("\n📋 Método 1: Historial de posiciones")
    try:
        # Buscar en las últimas 24 horas
        history = iq.get_position_history("binary-option", 86400)
        
        if history and isinstance(history, dict) and 'positions' in history:
            found = False
            for position in history['positions']:
                if str(position.get('id')) == str(order_id):
                    found = True
                    print("   ✅ Orden encontrada:")
                    
                    # Extraer información clave
                    amount = position.get('amount', 0)
                    win_amount = position.get('win_amount', 0)
                    status = position.get('status', 'unknown')
                    win = position.get('win', 'unknown')
                    
                    print(f"   Asset: {position.get('active')}")
                    print(f"   Direction: {position.get('direction')}")
                    print(f"   Amount: ${amount:,.2f}")
                    print(f"   Status: {status}")
                    print(f"   Win: {win}")
                    print(f"   Win Amount: ${win_amount:,.2f}")
                    
                    # Interpretar resultado
                    if win == 'win':
                        profit = win_amount - amount
                        print(f"\n   🎯 RESULTADO: GANANCIA")
                        print(f"   Profit: ${profit:,.2f}")
                        print(f"   Retorno total: ${win_amount:,.2f}")
                    elif win == 'loose':
                        print(f"\n   🎯 RESULTADO: PÉRDIDA")
                        print(f"   Pérdida: ${amount:,.2f}")
                    elif win == 'equal':
                        print(f"\n   🎯 RESULTADO: EMPATE")
                        print(f"   Sin ganancia ni pérdida")
                    
                    print(f"\n   Created: {position.get('created')}")
                    print(f"   Expired: {position.get('expired')}")
                    break
            
            if not found:
                print("   ❌ Orden no encontrada en historial de 24h")
                print("\n   📋 Mostrando últimas 5 órdenes como referencia:")
                for i, pos in enumerate(history['positions'][:5]):
                    print(f"   {i+1}. ID: {pos.get('id')}, Asset: {pos.get('active')}, Status: {pos.get('status')}")
        else:
            print("   ❌ No se pudo obtener historial")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Método 2: all_deals_closed
    print("\n📋 Método 2: Deals cerrados")
    try:
        if hasattr(iq, 'get_all_deals_closed'):
            deals = iq.get_all_deals_closed()
            if deals:
                found = False
                for deal in deals:
                    if str(deal.get('id')) == str(order_id):
                        found = True
                        print(f"   ✅ Deal encontrado: {deal}")
                        break
                if not found:
                    print("   ❌ No encontrado en deals cerrados")
        else:
            print("   ⚠️ Método no disponible")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Método 3: get_order_info (si existe)
    print("\n📋 Método 3: Order info directo")
    try:
        if hasattr(iq, 'get_order'):
            result, status = verifier.check_with_timeout(iq.get_order, (order_id,), timeout=3)
            if status == "Timeout":
                print("   ⏱️ Timeout (método bloqueado)")
            elif result:
                print(f"   ✅ Resultado: {result}")
            else:
                print("   ❌ Sin resultado")
        else:
            print("   ⚠️ Método no disponible")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "="*60)

def get_recent_orders_safe(iq):
    """Obtener órdenes recientes de forma segura"""
    print("\n📋 Órdenes recientes (últimas 2 horas)")
    print("="*60)
    
    try:
        history = iq.get_position_history("binary-option", 7200)  # 2 horas
        
        if history and 'positions' in history:
            positions = history['positions']
            print(f"Total encontradas: {len(positions)}\n")
            
            # Mostrar hasta 10
            for i, pos in enumerate(positions[:10]):
                amount = pos.get('amount', 0)
                win_amount = pos.get('win_amount', 0)
                win = pos.get('win', 'unknown')
                
                # Determinar resultado
                if win == 'win':
                    result = f"✅ WIN +${win_amount - amount:.2f}"
                    color = '\033[92m'  # Verde
                elif win == 'loose':
                    result = f"❌ LOSS -${amount:.2f}"
                    color = '\033[91m'  # Rojo
                elif win == 'equal':
                    result = "🟡 TIE $0"
                    color = '\033[93m'  # Amarillo
                else:
                    result = f"❓ {win}"
                    color = '\033[0m'   # Normal
                
                print(f"{i+1}. ID: {pos.get('id')}")
                print(f"   Asset: {pos.get('active')} | Direction: {pos.get('direction')}")
                print(f"   Amount: ${amount:,.2f} | {color}{result}\033[0m")
                print(f"   Created: {pos.get('created')}")
                print()
                
        else:
            print("❌ No se encontraron posiciones")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_live_order(iq):
    """Hacer una orden de prueba y verificar resultado"""
    print("\n🧪 PRUEBA EN VIVO")
    print("="*60)
    
    # Configuración
    amount = 1  # $1
    asset = "EURUSD-OTC"
    direction = "call"
    duration = 1  # 1 minuto
    
    print(f"Configuración: {asset} | ${amount} | {direction} | {duration}min")
    
    # Hacer orden
    print("\n📊 Colocando orden...")
    check, order_id = iq.buy(amount, asset, direction, duration)
    
    if not check:
        print(f"❌ Error: {order_id}")
        return
    
    print(f"✅ Orden creada: {order_id}")
    print(f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
    
    # Esperar
    wait_time = 75  # 1min + 15s
    print(f"\n⏳ Esperando {wait_time} segundos...")
    
    for i in range(wait_time, 0, -5):
        print(f"   {i} segundos restantes...", end='\r')
        time.sleep(5)
    
    print("\n")
    
    # Verificar con método seguro
    verify_order_safe(iq, order_id)

def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python verify_orders_fixed.py <order_id>  - Verificar orden")
        print("  python verify_orders_fixed.py recent      - Ver recientes")
        print("  python verify_orders_fixed.py test        - Prueba en vivo")
        sys.exit(1)
    
    # Conectar
    print("🔗 Conectando a IQ Option...")
    iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
    check, reason = iq.connect()
    
    if not check:
        print(f"❌ Error: {reason}")
        sys.exit(1)
    
    print("✅ Conectado")
    iq.change_balance(ACCOUNT_TYPE)
    print(f"💰 Balance: ${iq.get_balance():,.2f}")
    
    command = sys.argv[1].lower()
    
    if command == "recent":
        get_recent_orders_safe(iq)
    elif command == "test":
        test_live_order(iq)
    else:
        verify_order_safe(iq, command)

if __name__ == "__main__":
    main()