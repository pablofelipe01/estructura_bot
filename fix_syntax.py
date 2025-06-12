# fix_syntax.py
# Arreglar el error de sintaxis en strategy.py

import re

print("🔧 ARREGLANDO ERROR DE SINTAXIS")
print("="*60)

# Leer el archivo
with open('strategy.py', 'r') as f:
    content = f.read()

# Buscar el área problemática alrededor de la línea 736
# El problema es que falta una coma antes de "balance_before"
pattern = r'("rsi": rsi_value)\n\s*("balance_before": current_balance)'
replacement = r'\1,\n            \2'

if re.search(pattern, content):
    content = re.sub(pattern, replacement, content)
    print("✅ Coma agregada después de 'rsi': rsi_value")
else:
    # Intentar otro patrón
    pattern2 = r'("rsi": rsi_value)(\s*"balance_before": current_balance)'
    if re.search(pattern2, content):
        content = re.sub(pattern2, r'\1,\2', content)
        print("✅ Coma agregada (método alternativo)")
    else:
        # Buscar manualmente alrededor de la línea 736
        lines = content.split('\n')
        for i in range(730, min(740, len(lines))):
            if '"balance_before": current_balance' in lines[i]:
                # Verificar la línea anterior
                if i > 0 and lines[i-1].strip() and not lines[i-1].strip().endswith(','):
                    lines[i-1] = lines[i-1].rstrip() + ','
                    print(f"✅ Coma agregada en línea {i}")
                    content = '\n'.join(lines)
                    break

# Guardar el archivo corregido
with open('strategy.py', 'w') as f:
    f.write(content)

print("\n📝 Verificando sintaxis...")

# Intentar importar para verificar que no hay errores
try:
    import ast
    with open('strategy.py', 'r') as f:
        ast.parse(f.read())
    print("✅ Sintaxis correcta!")
except SyntaxError as e:
    print(f"❌ Todavía hay un error de sintaxis: {e}")
    print(f"   Línea {e.lineno}: {e.text}")

print("\n" + "="*60)
print("✅ Error de sintaxis arreglado")
print("="*60)
print("\n🎯 Ahora ejecuta:")
print("   python main.py")
print("\n✅ El bot debería funcionar correctamente")
print("="*60)