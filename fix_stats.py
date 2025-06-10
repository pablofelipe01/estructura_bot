#!/usr/bin/env python3
# fix_stats.py - Corregir estadísticas si hay errores en el conteo

import json
import os
from datetime import datetime

def fix_statistics():
    """Corregir estadísticas manualmente"""
    
    state_file = "strategy_state.json"
    
    if not os.path.exists(state_file):
        print("❌ No se encontró archivo de estado")
        return
    
    try:
        # Cargar estado
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        print("📊 ESTADÍSTICAS ACTUALES:")
        print("=" * 60)
        
        # Mostrar estadísticas actuales
        wins = state.get('wins', {})
        losses = state.get('losses', {})
        ties = state.get('ties', {})
        
        total_wins = sum(wins.values())
        total_losses = sum(losses.values())
        total_ties = sum(ties.values())
        
        print(f"Total victorias: {total_wins}")
        print(f"Total derrotas: {total_losses}")
        print(f"Total empates: {total_ties}")
        print(f"Total operaciones: {total_wins + total_losses + total_ties}")
        print(f"Beneficio total: ${state.get('total_profit', 0):,.2f}")
        
        print("\nPor par:")
        all_pairs = set(list(wins.keys()) + list(losses.keys()) + list(ties.keys()))
        for pair in sorted(all_pairs):
            w = wins.get(pair, 0)
            l = losses.get(pair, 0)
            t = ties.get(pair, 0)
            if w + l + t > 0:
                print(f"  {pair}: {w}W / {l}L / {t}T")
        
        # Preguntar si quiere hacer correcciones
        print("\n" + "=" * 60)
        response = input("\n¿Deseas hacer correcciones? (s/n): ")
        
        if response.lower() == 's':
            print("\nEjemplo de corrección:")
            print("  - Para cambiar una pérdida a empate: GBPUSD loss->tie")
            print("  - Para cambiar un empate a victoria: EURUSD tie->win")
            print("  - Para salir: exit")
            
            while True:
                correction = input("\nIngresa corrección (o 'exit' para salir): ").strip()
                
                if correction.lower() == 'exit':
                    break
                
                try:
                    # Parsear la corrección
                    parts = correction.split()
                    if len(parts) != 2:
                        print("❌ Formato incorrecto. Usa: PAR from->to")
                        continue
                    
                    pair = parts[0].upper()
                    change = parts[1].lower()
                    
                    if '->' not in change:
                        print("❌ Usa el formato: loss->tie, win->loss, etc.")
                        continue
                    
                    from_type, to_type = change.split('->')
                    
                    # Validar tipos
                    valid_types = ['win', 'loss', 'tie']
                    if from_type not in valid_types or to_type not in valid_types:
                        print("❌ Tipos válidos: win, loss, tie")
                        continue
                    
                    # Aplicar corrección
                    made_change = False
                    
                    # Decrementar el contador origen
                    if from_type == 'win' and pair in wins and wins[pair] > 0:
                        wins[pair] -= 1
                        made_change = True
                    elif from_type == 'loss' and pair in losses and losses[pair] > 0:
                        losses[pair] -= 1
                        made_change = True
                        # Ajustar profit (recuperar la pérdida)
                        state['total_profit'] = state.get('total_profit', 0) + 20000
                    elif from_type == 'tie' and pair in ties and ties[pair] > 0:
                        ties[pair] -= 1
                        made_change = True
                    
                    if not made_change:
                        print(f"❌ No hay {from_type} para {pair}")
                        continue
                    
                    # Incrementar el contador destino
                    if to_type == 'win':
                        if pair not in wins:
                            wins[pair] = 0
                        wins[pair] += 1
                        # Ajustar profit (ganancia del 80%)
                        state['total_profit'] = state.get('total_profit', 0) + 16000  # 80% de 20k
                    elif to_type == 'loss':
                        if pair not in losses:
                            losses[pair] = 0
                        losses[pair] += 1
                        # Ajustar profit (pérdida)
                        state['total_profit'] = state.get('total_profit', 0) - 20000
                    elif to_type == 'tie':
                        if pair not in ties:
                            ties[pair] = 0
                        ties[pair] += 1
                    
                    print(f"✅ Corregido: {pair} {from_type} → {to_type}")
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
            
            # Actualizar el estado
            state['wins'] = wins
            state['losses'] = losses
            state['ties'] = ties
            state['timestamp'] = datetime.now().isoformat()
            
            # Guardar cambios
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=4)
            
            print("\n✅ Estadísticas actualizadas")
            
            # Mostrar nuevo resumen
            print("\n📊 NUEVAS ESTADÍSTICAS:")
            print("=" * 60)
            total_wins = sum(wins.values())
            total_losses = sum(losses.values())
            total_ties = sum(ties.values())
            print(f"Total victorias: {total_wins}")
            print(f"Total derrotas: {total_losses}")
            print(f"Total empates: {total_ties}")
            print(f"Beneficio total: ${state.get('total_profit', 0):,.2f}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    fix_statistics()