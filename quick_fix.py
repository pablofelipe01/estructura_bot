#!/usr/bin/env python3
# quick_fix.py - Corrección rápida basada en lo que viste en IQ Option

import json
import os
from datetime import datetime

def quick_fix():
    """Corregir las estadísticas basándose en lo que viste en IQ Option"""
    
    print("=" * 60)
    print("   CORRECCIÓN RÁPIDA DE ESTADÍSTICAS")
    print("=" * 60)
    
    state_file = "strategy_state.json"
    
    if not os.path.exists(state_file):
        print("❌ No se encontró archivo de estado")
        return
    
    try:
        # Cargar estado
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        print("\n📊 ESTADO ACTUAL:")
        print(f"Total profit: ${state.get('total_profit', 0):,.2f}")
        
        wins = state.get('wins', {})
        losses = state.get('losses', {})
        
        # Mostrar estadísticas de GBPUSD y EURUSD
        for pair in ['GBPUSD', 'EURUSD']:
            w = wins.get(pair, 0)
            l = losses.get(pair, 0)
            print(f"{pair}: {w} victorias, {l} derrotas")
        
        print("\n🔧 CORRECCIONES A APLICAR:")
        print("Según lo que viste en IQ Option:")
        print("- GBPUSD PUT @ 12:49 fue GANADORA (+$17,000)")
        print("- EURUSD CALL @ 12:31 fue PERDEDORA (-$20,000)")
        
        response = input("\n¿Aplicar estas correcciones? (s/n): ")
        
        if response.lower() == 's':
            # Corregir GBPUSD: cambiar de loss a win
            if 'GBPUSD' in losses and losses['GBPUSD'] > 0:
                losses['GBPUSD'] -= 1
                if 'GBPUSD' not in wins:
                    wins['GBPUSD'] = 0
                wins['GBPUSD'] += 1
                
                # Ajustar profit: recuperar los 20k perdidos + agregar 17k de ganancia
                state['total_profit'] = state.get('total_profit', 0) + 20000 + 17000
                print("✅ GBPUSD corregido: pérdida → victoria (+$37,000 al profit)")
            
            # EURUSD ya está correctamente marcado como pérdida
            print("✅ EURUSD ya está correcto como pérdida")
            
            # Actualizar el estado
            state['wins'] = wins
            state['losses'] = losses
            state['timestamp'] = datetime.now().isoformat()
            
            # Guardar
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=4)
            
            print("\n✅ Correcciones aplicadas")
            
            # Mostrar nuevo estado
            print("\n📊 NUEVO ESTADO:")
            print(f"Total profit: ${state.get('total_profit', 0):,.2f}")
            
            for pair in ['GBPUSD', 'EURUSD']:
                w = wins.get(pair, 0)
                l = losses.get(pair, 0)
                print(f"{pair}: {w} victorias, {l} derrotas")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    quick_fix()