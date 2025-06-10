#!/usr/bin/env python3
# check_state.py - Verificar y opcionalmente limpiar el estado guardado

import json
import os
from datetime import datetime

def check_and_clean_state():
    """Verificar el estado guardado y limpiarlo si es necesario"""
    
    state_file = "strategy_state.json"
    
    if not os.path.exists(state_file):
        print("❌ No se encontró archivo de estado")
        return
    
    try:
        # Cargar estado
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        print("📊 ESTADO ACTUAL:")
        print("=" * 60)
        
        # Mostrar información general
        print(f"Última actualización: {state.get('timestamp', 'N/A')}")
        print(f"Último día operado: {state.get('last_date', 'N/A')}")
        print(f"Mes actual: {state.get('current_month', 'N/A')}")
        
        # Mostrar pérdidas consecutivas
        consecutive_losses = state.get('consecutive_losses', {})
        if consecutive_losses:
            print("\n📉 Pérdidas consecutivas por par:")
            for pair, losses in consecutive_losses.items():
                if losses > 0:
                    print(f"   {pair}: {losses} pérdidas")
        
        # Mostrar bloqueos diarios
        daily_lockouts = state.get('daily_lockouts', {})
        blocked_pairs = [pair for pair, blocked in daily_lockouts.items() if blocked]
        if blocked_pairs:
            print(f"\n🚫 Pares bloqueados: {', '.join(blocked_pairs)}")
        
        # Verificar si es un nuevo día
        last_date_str = state.get('last_date')
        if last_date_str:
            last_date = datetime.fromisoformat(last_date_str).date()
            current_date = datetime.now().date()
            
            if last_date < current_date:
                print(f"\n⚠️ NUEVO DÍA DETECTADO!")
                print(f"   Último día: {last_date}")
                print(f"   Día actual: {current_date}")
                
                response = input("\n¿Deseas limpiar pérdidas consecutivas y bloqueos? (s/n): ")
                
                if response.lower() == 's':
                    # Limpiar pérdidas consecutivas
                    state['consecutive_losses'] = {}
                    state['daily_lockouts'] = {}
                    state['last_date'] = current_date.isoformat()
                    state['timestamp'] = datetime.now().isoformat()
                    
                    # Guardar estado limpio
                    with open(state_file, 'w') as f:
                        json.dump(state, f, indent=4)
                    
                    print("\n✅ Estado limpiado exitosamente")
                    print("   - Pérdidas consecutivas: reseteadas")
                    print("   - Bloqueos diarios: eliminados")
                    print("   - Fecha actualizada")
        
        # Mostrar estadísticas
        wins = state.get('wins', {})
        losses = state.get('losses', {})
        total_wins = sum(wins.values())
        total_losses = sum(losses.values())
        
        print(f"\n📊 Estadísticas totales:")
        print(f"   Operaciones ganadas: {total_wins}")
        print(f"   Operaciones perdidas: {total_losses}")
        print(f"   Total profit: ${state.get('total_profit', 0):,.2f}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_and_clean_state()