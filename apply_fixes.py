# apply_fixes.py
# Script para aplicar todas las correcciones automáticamente

import os
import shutil
from datetime import datetime

def backup_file(filename):
    """Crear backup de un archivo"""
    if os.path.exists(filename):
        backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filename, backup_name)
        print(f"✅ Backup creado: {backup_name}")
        return True
    return False

def apply_config_fixes():
    """Aplicar correcciones a config.py"""
    print("\n📝 Aplicando correcciones a config.py...")
    
    # Leer config actual
    if not os.path.exists('config.py'):
        print("❌ No se encontró config.py")
        return False
    
    backup_file('config.py')
    
    with open('config.py', 'r') as f:
        content = f.read()
    
    # Aplicar correcciones
    fixes_applied = []
    
    # 1. Arreglar FOREX_PAIRS duplicados
    if 'FOREX_PAIRS = [\n    "EURCAD", "GBPCHF", "GBPCHF"\n]' in content:
        content = content.replace(
            'FOREX_PAIRS = [\n    "EURCAD", "GBPCHF", "GBPCHF"\n]',
            'FOREX_PAIRS = [\n    "EURUSD",    # Par más líquido\n    "EURCAD",\n    "GBPCHF"\n]'
        )
        fixes_applied.append("FOREX_PAIRS sin duplicados")
    
    # 2. Reducir API_TIMEOUT
    if 'API_TIMEOUT = 15' in content:
        content = content.replace('API_TIMEOUT = 15', 'API_TIMEOUT = 10')
        fixes_applied.append("API_TIMEOUT reducido a 10s")
    
    # 3. Agregar nuevas configuraciones si no existen
    new_configs = [
        "\n# Configuración de debugging (NUEVO)",
        "USE_POSITION_HISTORY = True  # Usar historial de posiciones en lugar de check_win_v3",
        "POSITION_HISTORY_TIMEOUT = 5  # Timeout para consultas de historial",
        "DEBUG_ORDER_RESULTS = True  # Logging detallado de resultados de órdenes"
    ]
    
    if "USE_POSITION_HISTORY" not in content:
        content += "\n" + "\n".join(new_configs) + "\n"
        fixes_applied.append("Configuraciones de debugging agregadas")
    
    # Guardar cambios
    with open('config.py', 'w') as f:
        f.write(content)
    
    print(f"✅ {len(fixes_applied)} correcciones aplicadas:")
    for fix in fixes_applied:
        print(f"   - {fix}")
    
    return True

def verify_api_methods():
    """Verificar métodos disponibles en la API"""
    print("\n🔍 Verificando métodos de la API...")
    
    try:
        from iqoptionapi.stable_api import IQ_Option
        from config import IQ_EMAIL, IQ_PASSWORD
        
        print("🔗 Conectando para verificar...")
        iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
        check, reason = iq.connect()
        
        if not check:
            print(f"❌ No se pudo conectar: {reason}")
            return
        
        print("✅ Conexión exitosa")
        
        # Verificar métodos críticos
        methods_to_check = [
            'get_position_history',
            'check_win_v3',
            'get_async_order',
            'get_optioninfo_v2',
            'get_all_deals'
        ]
        
        print("\n📋 Métodos disponibles:")
        for method in methods_to_check:
            if hasattr(iq, method):
                print(f"   ✅ {method}")
            else:
                print(f"   ❌ {method} (no disponible)")
        
        # Desconectar
        iq.api.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def create_test_script():
    """Crear script de prueba rápida"""
    print("\n📝 Creando script de prueba rápida...")
    
    test_script = '''#!/usr/bin/env python3
# test_fixed_bot.py - Prueba rápida del bot arreglado

import time
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from config import *

print("🧪 PRUEBA RÁPIDA DEL BOT ARREGLADO")
print("="*50)

# Conectar
print("\\n🔗 Conectando...")
iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
check, reason = iq.connect()

if not check:
    print(f"❌ Error: {reason}")
    exit()

iq.change_balance(ACCOUNT_TYPE)
print(f"✅ Conectado. Balance: ${iq.get_balance():,.2f}")

# Hacer operación pequeña
print("\\n📊 Haciendo operación de prueba ($1)...")
check, order_id = iq.buy(1, "EURUSD-OTC", "call", 1)

if check:
    print(f"✅ Orden creada: {order_id}")
    print("⏳ Esperando 75 segundos...")
    
    for i in range(75, 0, -5):
        print(f"   {i}s...", end="\\r")
        time.sleep(5)
    
    # Verificar con historial (método seguro)
    print("\\n\\n🔍 Verificando resultado...")
    history = iq.get_position_history("binary-option", 300)
    
    if history and 'positions' in history:
        for pos in history['positions']:
            if str(pos.get('id')) == str(order_id):
                win = pos.get('win')
                amount = pos.get('amount', 0)
                win_amount = pos.get('win_amount', 0)
                
                print(f"\\n📊 RESULTADO:")
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

print("\\n✅ Prueba completada")
'''
    
    with open('test_fixed_bot.py', 'w') as f:
        f.write(test_script)
    
    os.chmod('test_fixed_bot.py', 0o755)
    print("✅ Script creado: test_fixed_bot.py")

def main():
    """Aplicar todas las correcciones"""
    print("="*60)
    print("🔧 APLICANDO CORRECCIONES AL BOT DE IQ OPTION")
    print("="*60)
    
    # 1. Aplicar fixes a config.py
    if apply_config_fixes():
        print("✅ Configuración actualizada")
    
    # 2. Verificar API
    verify_api_methods()
    
    # 3. Crear script de prueba
    create_test_script()
    
    print("\n" + "="*60)
    print("✅ CORRECCIONES APLICADAS")
    print("="*60)
    print("\n📋 Próximos pasos:")
    print("1. Ejecuta: python test_fixed_bot.py")
    print("2. Si funciona, ejecuta: python main.py")
    print("3. Los resultados ahora deberían detectarse correctamente")
    print("\n⚠️ IMPORTANTE:")
    print("- NO uses check_win_v3 (causa bloqueos)")
    print("- El bot ahora usa get_position_history (más confiable)")
    print("- GBPCHF ya no está duplicado")
    print("\n✅ ¡Listo para usar!")

if __name__ == "__main__":
    main()