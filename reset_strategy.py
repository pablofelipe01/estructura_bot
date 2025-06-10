#!/usr/bin/env python3
# reset_strategy.py - Resetear estado para la nueva estrategia con lógica invertida

import os
import json
from datetime import datetime

def reset_strategy():
    """Resetear el estado para comenzar con la nueva estrategia"""
    
    print("=" * 60)
    print("   RESET PARA NUEVA ESTRATEGIA RSI INVERTIDA")
    print("=" * 60)
    
    state_file = "strategy_state.json"
    backup_file = f"strategy_state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print("\n⚡ CAMBIOS IMPORTANTES:")
    print("- Lógica INVERTIDA: PUT en sobreventa (RSI≤35)")
    print("- Lógica INVERTIDA: CALL en sobrecompra (RSI≥65)")
    print("- Esta es una estrategia completamente diferente")
    
    if os.path.exists(state_file):
        print(f"\n📁 Archivo de estado encontrado: {state_file}")
        
        # Hacer backup
        try:
            with open(state_file, 'r') as f:
                state_data = f.read()
            
            with open(backup_file, 'w') as f:
                f.write(state_data)
            
            print(f"✅ Backup creado: {backup_file}")
            
            # Mostrar estadísticas actuales
            state = json.loads(state_data)
            total_wins = sum(state.get('wins', {}).values())
            total_losses = sum(state.get('losses', {}).values())
            total_profit = state.get('total_profit', 0)
            
            print(f"\n📊 Estadísticas anteriores:")
            print(f"   Victorias: {total_wins}")
            print(f"   Derrotas: {total_losses}")
            print(f"   Profit: ${total_profit:,.2f}")
            
        except Exception as e:
            print(f"⚠️ Error creando backup: {e}")
        
        # Preguntar si resetear
        response = input("\n¿Deseas resetear el estado para la nueva estrategia? (s/n): ")
        
        if response.lower() == 's':
            try:
                os.remove(state_file)
                print(f"\n✅ Estado reseteado exitosamente")
                print("📌 La estrategia comenzará desde cero con la lógica invertida")
                
                # Crear archivo de marca para indicar nueva estrategia
                with open("strategy_version.txt", "w") as f:
                    f.write("RSI_INVERTED_v2.0\n")
                    f.write(f"Reset date: {datetime.now().isoformat()}\n")
                    f.write("Logic: PUT on oversold, CALL on overbought\n")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("\n❌ Reset cancelado")
            print("⚠️ ADVERTENCIA: Usar el estado anterior con la nueva lógica puede dar resultados inesperados")
    else:
        print("\n✅ No hay estado previo. Listo para comenzar con la nueva estrategia")
        
        # Crear archivo de marca
        with open("strategy_version.txt", "w") as f:
            f.write("RSI_INVERTED_v2.0\n")
            f.write(f"Start date: {datetime.now().isoformat()}\n")
            f.write("Logic: PUT on oversold, CALL on overbought\n")
    
    print("\n📌 Próximos pasos:")
    print("1. Revisa config.py para confirmar los parámetros")
    print("2. Ejecuta: python main.py")
    print("3. Monitorea las primeras operaciones cuidadosamente")
    print("\n⚡ Recuerda: Esta estrategia opera AL REVÉS de la anterior")

if __name__ == "__main__":
    reset_strategy()