#!/usr/bin/env python3
# reset_consecutive_losses.py - Resetear pérdidas consecutivas rápidamente

import json
import os

# Cargar estado
if os.path.exists("strategy_state.json"):
    with open("strategy_state.json", 'r') as f:
        state = json.load(f)
    
    # Resetear pérdidas consecutivas y bloqueos
    state['consecutive_losses'] = {}
    state['daily_lockouts'] = {}
    
    # Guardar
    with open("strategy_state.json", 'w') as f:
        json.dump(state, f, indent=4)
    
    print("✅ Pérdidas consecutivas y bloqueos reseteados")
else:
    print("❌ No se encontró archivo de estado")