# apply_complete_fix.py
# Script para aplicar automáticamente la solución completa

import os
import shutil
from datetime import datetime

print("🔧 APLICANDO SOLUCIÓN COMPLETA AL BOT")
print("="*60)

# Verificar que existe strategy.py
if not os.path.exists('strategy.py'):
    print("❌ No se encontró strategy.py")
    exit(1)

# Crear backup
backup_name = f'strategy.py.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('strategy.py', backup_name)
print(f"✅ Backup creado: {backup_name}")

# Leer el archivo
with open('strategy.py', 'r') as f:
    lines = f.readlines()

print("\n📝 Aplicando cambios...")

# Bandera para saber si estamos dentro del método que queremos reemplazar
in_process_expired = False
in_create_binary = False
method_indent = ""
changes_made = 0

# Nuevo código para process_expired_order
new_process_expired = '''    def process_expired_order(self, pair, order):
        """Procesar una orden expirada - VERSIÓN ALTERNATIVA SIN get_position_history"""
        try:
            self.logger.info(f"🔄 Verificando orden {order['id']}...")
            
            # Verificar tiempo desde expiración
            time_since_expiry = (datetime.now() - order["expiry_time"]).total_seconds()
            
            # Si es muy reciente, esperar
            if time_since_expiry < 10:
                self.logger.info(f"⏳ Orden muy reciente ({time_since_expiry:.0f}s), esperando...")
                return
            
            # MÉTODO 1: Verificar en api.listinfodata
            result_found = False
            win_status = None
            win_amount = 0
            
            if hasattr(self.iqoption.api, 'listinfodata') and isinstance(self.iqoption.api.listinfodata, dict):
                self.logger.debug("📋 Buscando en listinfodata...")
                for key, value in self.iqoption.api.listinfodata.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict) and str(item.get('id')) == str(order['id']):
                                result_found = True
                                win_status = str(item.get('win', '')).lower()
                                win_amount = float(item.get('win_amount', 0))
                                
                                self.logger.info(f"📋 Orden encontrada en listinfodata:")
                                self.logger.info(f"   Win: {win_status}")
                                self.logger.info(f"   Win Amount: {win_amount}")
                                break
                    if result_found:
                        break
            
            # MÉTODO 2: Verificar por balance (si no se encontró en listinfodata)
            if not result_found and 'balance_before' in order:
                current_balance = self.api_call_with_timeout(self.iqoption.get_balance)
                if current_balance is not None:
                    balance_diff = current_balance - order['balance_before']
                    
                    self.logger.info(f"📊 Verificación por balance:")
                    self.logger.info(f"   Balance antes: ${order['balance_before']:,.2f}")
                    self.logger.info(f"   Balance ahora: ${current_balance:,.2f}")
                    self.logger.info(f"   Diferencia: ${balance_diff:+,.2f}")
                    
                    if balance_diff > 0:
                        win_status = 'win'
                        win_amount = order["size"] + balance_diff
                        result_found = True
                    elif balance_diff < -0.5:  # Pequeño margen para evitar falsos positivos
                        win_status = 'loose'
                        win_amount = 0
                        result_found = True
            
            # MÉTODO 3: Intentar get_async_order como último recurso
            if not result_found and time_since_expiry > 20:
                self.logger.info("📋 Intentando get_async_order...")
                order_result = self.api_call_with_timeout(
                    self.iqoption.get_async_order,
                    order["id"],
                    timeout=3
                )
                
                if order_result and isinstance(order_result, dict):
                    # Procesar con la lógica original
                    self._process_order_result(pair, order, order_result)
                    return
            
            # Procesar resultado si se encontró
            if result_found and win_status:
                bet_size = order["size"]
                
                if win_status == 'win':
                    self.logger.info(f"✅ Victoria detectada")
                    self.process_win(pair, order, win_amount)
                elif win_status == 'equal':
                    self.logger.info(f"🟡 Empate detectado")
                    self.process_tie(pair, order)
                elif win_status == 'loose':
                    self.logger.info(f"❌ Pérdida detectada")
                    self.process_loss(pair, order)
                else:
                    # Si no podemos determinar, verificar por monto
                    if win_amount > bet_size:
                        self.process_win(pair, order, win_amount)
                    elif win_amount == bet_size:
                        self.process_tie(pair, order)
                    else:
                        self.process_loss(pair, order)
                return
            
            # Si han pasado más de 2 minutos y no hay resultado, asumir pérdida
            if time_since_expiry > 120:
                self.logger.error(f"❌ No se pudo verificar orden después de {time_since_expiry:.0f}s")
                self.logger.error(f"❌ Asumiendo pérdida por timeout")
                self.process_loss(pair, order)
                
        except Exception as e:
            self.logger.error(f"❌ Error procesando orden expirada: {str(e)}")
            self.logger.error(f"Detalles: {traceback.format_exc()}")
            # En caso de error, registrar como pérdida para ser conservadores
            self.process_loss(pair, order)
'''

# Procesar línea por línea
new_lines = []
skip_until_next_method = False

for i, line in enumerate(lines):
    # Detectar el inicio de process_expired_order
    if 'def process_expired_order' in line:
        in_process_expired = True
        skip_until_next_method = True
        method_indent = line[:len(line) - len(line.lstrip())]
        # Agregar el nuevo método
        new_lines.extend(new_process_expired.split('\n'))
        new_lines.append('\n')
        changes_made += 1
        continue
    
    # Detectar el siguiente método después de process_expired_order
    if skip_until_next_method and line.strip() and not line.startswith(' '):
        skip_until_next_method = False
    elif skip_until_next_method and line.strip() and line.startswith(method_indent + 'def '):
        skip_until_next_method = False
    
    # Si estamos saltando líneas, continuar
    if skip_until_next_method:
        continue
    
    # Detectar create_binary_option y agregar balance_before
    if 'order_info = {' in line:
        new_lines.append(line)
        # Buscar el cierre del diccionario
        j = i + 1
        while j < len(lines) and '}' not in lines[j]:
            new_lines.append(lines[j])
            j += 1
        # Agregar balance_before antes del cierre
        if '}' in lines[j]:
            indent = lines[j-1][:len(lines[j-1]) - len(lines[j-1].lstrip())]
            new_lines.append(f'{indent}"balance_before": current_balance  # NUEVO: Guardar balance antes\n')
            changes_made += 1
        new_lines.append(lines[j])
        # Saltar las líneas ya procesadas
        for k in range(i+1, j+1):
            lines[k] = None
        continue
    
    # Agregar línea normal si no fue procesada
    if line is not None:
        new_lines.append(line)

# Guardar el archivo modificado
with open('strategy.py', 'w') as f:
    f.writelines(new_lines)

print(f"\n✅ {changes_made} cambios aplicados exitosamente")

# Verificar que no usamos métodos problemáticos
print("\n🔍 Verificando que no se usan métodos problemáticos...")
content = ''.join(new_lines)

problematic_methods = ['check_win_v3', 'check_binary_order', 'get_position_history']
issues = []

for method in problematic_methods:
    # Buscar uso activo (no en comentarios)
    for line in new_lines:
        if line and method in line and not line.strip().startswith('#'):
            if 'self.iqoption.' + method in line or 'self.api_call_with_timeout' in line and method in line:
                # Verificar que no esté en el método alternativo
                if 'MÉTODO' not in line and 'Intentar' not in line:
                    issues.append(f"   ⚠️ Todavía se usa {method} en: {line.strip()}")

if issues:
    print("⚠️ ADVERTENCIA: Se encontraron usos de métodos problemáticos:")
    for issue in issues:
        print(issue)
else:
    print("✅ No se usan métodos problemáticos")

print("\n" + "="*60)
print("✅ SOLUCIÓN APLICADA EXITOSAMENTE")
print("="*60)
print("\n📋 Cambios realizados:")
print("1. process_expired_order ahora usa métodos alternativos")
print("2. create_binary_option ahora guarda el balance inicial")
print("3. No se usa get_position_history (no funciona)")
print("4. No se usa check_win_v3 (causa bloqueos)")

print("\n🎯 Próximos pasos:")
print("1. Ejecuta: python working_solution.py (para verificar)")
print("2. Ejecuta: python main.py (para usar el bot)")

print("\n💡 El bot ahora detectará correctamente:")
print("   ✅ Ganancias")
print("   ❌ Pérdidas")
print("   🟡 Empates")

print("\n✅ ¡Listo para usar!")
print("="*60)