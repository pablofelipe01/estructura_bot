# diagnose_fix.py
# Diagnosticar y arreglar el error de sintaxis

print("🔍 DIAGNOSTICANDO ERROR DE SINTAXIS")
print("="*60)

# Leer el archivo
with open('strategy.py', 'r') as f:
    lines = f.readlines()

# Mostrar contexto alrededor de la línea 736
print("\n📋 Contexto alrededor de la línea 736:")
print("-" * 40)

for i in range(max(0, 730), min(742, len(lines))):
    line_num = i + 1
    marker = ">>>" if line_num == 736 else "   "
    print(f"{marker} {line_num}: {lines[i].rstrip()}")

print("-" * 40)

# Buscar el patrón exacto del problema
print("\n🔧 Buscando y arreglando el problema...")

# Buscar líneas que necesiten coma
fixed = False
for i in range(len(lines)):
    line = lines[i]
    next_line = lines[i+1] if i+1 < len(lines) else ""
    
    # Si la línea actual NO termina en coma y la siguiente línea empieza con comillas
    if ('"rsi": rsi_value' in line and 
        not line.rstrip().endswith(',') and 
        '"balance_before"' in next_line):
        print(f"✅ Encontrado en línea {i+1}: falta coma")
        lines[i] = line.rstrip() + ',\n'
        fixed = True
        break
    
    # Patrón alternativo: cualquier línea antes de balance_before que no tenga coma
    if (i > 0 and '"balance_before": current_balance' in line):
        prev_line = lines[i-1]
        if prev_line.strip() and not prev_line.rstrip().endswith(',') and not prev_line.rstrip().endswith('{'):
            print(f"✅ Agregando coma en línea {i}: {prev_line.strip()}")
            lines[i-1] = prev_line.rstrip() + ',\n'
            fixed = True
            break

if fixed:
    # Guardar el archivo corregido
    with open('strategy.py', 'w') as f:
        f.writelines(lines)
    print("✅ Archivo corregido y guardado")
    
    # Mostrar el contexto corregido
    print("\n📋 Contexto después de la corrección:")
    print("-" * 40)
    
    # Releer para mostrar
    with open('strategy.py', 'r') as f:
        lines = f.readlines()
    
    for i in range(max(0, 730), min(742, len(lines))):
        line_num = i + 1
        marker = ">>>" if line_num == 736 else "   "
        print(f"{marker} {line_num}: {lines[i].rstrip()}")
else:
    print("❌ No se encontró el patrón esperado")
    print("\n💡 Solución manual:")
    print("1. Abre strategy.py")
    print("2. Ve a la línea 735 (la línea ANTES de balance_before)")
    print("3. Agrega una coma al final de esa línea")
    print("4. Guarda el archivo")

# Verificar sintaxis
print("\n🔍 Verificando sintaxis...")
try:
    import ast
    with open('strategy.py', 'r') as f:
        ast.parse(f.read())
    print("✅ ¡Sintaxis correcta!")
except SyntaxError as e:
    print(f"❌ Error de sintaxis en línea {e.lineno}")
    if e.lineno:
        print(f"   Contenido: {lines[e.lineno-1].strip()}")

print("\n" + "="*60)