# verify_all.py
# Script de verificación completa del sistema

import sys
from datetime import datetime
from iqoptionapi.stable_api import IQ_Option
from config import *

print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA")
print("="*60)
print(f"⏰ Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# Lista de verificaciones
checks = {
    "conexion": False,
    "balance": False,
    "historial": False,
    "formato": False,
    "config": False
}

# 1. Verificar configuración
print("\n1️⃣ VERIFICANDO CONFIGURACIÓN...")
try:
    # Verificar FOREX_PAIRS sin duplicados
    if len(FOREX_PAIRS) != len(set(FOREX_PAIRS)):
        print("   ❌ FOREX_PAIRS tiene duplicados")
    else:
        print("   ✅ FOREX_PAIRS sin duplicados")
        checks["config"] = True
    
    # Verificar timeouts
    if hasattr(sys.modules['config'], 'API_TIMEOUT'):
        print(f"   ✅ API_TIMEOUT = {API_TIMEOUT}s")
    else:
        print("   ⚠️ API_TIMEOUT no definido")
        
except Exception as e:
    print(f"   ❌ Error en config: {str(e)}")

# 2. Verificar conexión
print("\n2️⃣ VERIFICANDO CONEXIÓN...")
try:
    iq = IQ_Option(IQ_EMAIL, IQ_PASSWORD)
    check, reason = iq.connect()
    
    if check:
        print("   ✅ Conexión exitosa")
        checks["conexion"] = True
        
        # Verificar balance
        iq.change_balance(ACCOUNT_TYPE)
        balance = iq.get_balance()
        if balance and balance > 0:
            print(f"   ✅ Balance: ${balance:,.2f}")
            checks["balance"] = True
        else:
            print("   ❌ No se pudo obtener balance")
    else:
        print(f"   ❌ Error de conexión: {reason}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    sys.exit(1)

# 3. Verificar get_position_history
print("\n3️⃣ VERIFICANDO get_position_history...")
try:
    history = iq.get_position_history("binary-option")
    
    if history:
        print(f"   ✅ Funciona. Tipo: {type(history)}")
        
        # Verificar formato
        if isinstance(history, tuple):
            print("   ✅ Formato tupla detectado (correcto)")
            
            # Buscar lista de posiciones
            positions_found = False
            for element in history:
                if isinstance(element, list) and element:
                    if isinstance(element[0], dict) and 'id' in element[0]:
                        positions_found = True
                        print(f"   ✅ Lista de posiciones encontrada: {len(element)} posiciones")
                        checks["formato"] = True
                        
                        # Mostrar última posición
                        last_pos = element[0]
                        print(f"\n   📊 Última posición:")
                        print(f"      ID: {last_pos.get('id')}")
                        print(f"      Asset: {last_pos.get('active')}")
                        print(f"      Win: {last_pos.get('win')}")
                        print(f"      Amount: ${last_pos.get('amount', 0)}")
                        break
            
            if not positions_found:
                print("   ⚠️ No se encontró lista de posiciones en la tupla")
        else:
            print(f"   ⚠️ Formato inesperado: {type(history)}")
            
        checks["historial"] = True
    else:
        print("   ❌ No se obtuvo historial")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# 4. Verificar que NO usamos check_win_v3
print("\n4️⃣ VERIFICANDO QUE NO SE USA check_win_v3...")
try:
    with open('strategy.py', 'r') as f:
        strategy_content = f.read()
    
    # Buscar uso de check_win_v3 (excepto en comentarios)
    lines = strategy_content.split('\n')
    uses_check_win = False
    for i, line in enumerate(lines):
        if 'check_win_v3' in line and not line.strip().startswith('#'):
            # Verificar que no esté en un string o comentario
            if 'self.iqoption.check_win_v3' in line or 'iq.check_win_v3' in line:
                print(f"   ⚠️ Línea {i+1}: Todavía usa check_win_v3")
                uses_check_win = True
    
    if not uses_check_win:
        print("   ✅ No se usa check_win_v3 (correcto)")
    else:
        print("   ❌ ADVERTENCIA: Aún se usa check_win_v3 (puede causar bloqueos)")
        
except Exception as e:
    print(f"   ⚠️ No se pudo verificar strategy.py: {str(e)}")

# 5. Verificar formato tupla en strategy.py
print("\n5️⃣ VERIFICANDO MANEJO DE TUPLAS EN strategy.py...")
try:
    if "isinstance(history, tuple)" in strategy_content:
        print("   ✅ Manejo de formato tupla implementado")
    else:
        print("   ❌ Falta implementar manejo de formato tupla")
        print("   💡 Ejecuta: python quick_fix.py")
except:
    pass

# Resumen
print("\n" + "="*60)
print("📊 RESUMEN DE VERIFICACIÓN:")
print("="*60)

all_ok = True
for check, status in checks.items():
    emoji = "✅" if status else "❌"
    print(f"{emoji} {check.capitalize()}: {'OK' if status else 'FALLO'}")
    if not status:
        all_ok = False

print("\n🎯 RESULTADO FINAL:")
if all_ok:
    print("✅ ¡TODO LISTO! El bot está configurado correctamente.")
    print("\n💡 Próximo paso: python main.py")
else:
    print("❌ Hay problemas que resolver.")
    print("\n💡 Revisa los errores arriba y:")
    print("   1. Si falta manejo de tuplas: python quick_fix.py")
    print("   2. Si hay duplicados en config: edita config.py")
    print("   3. Si hay otros errores: revisa la documentación")

print("="*60)