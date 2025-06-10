# analyzer.py
# Analizador de resultados para la estrategia RSI

import json
import os
from datetime import datetime
from collections import defaultdict
from config import STATE_FILE
from utils import format_currency, calculate_win_rate, calculate_profit_factor

class StrategyAnalyzer:
    """Analizador de resultados de la estrategia"""
    
    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file
        self.state = None
        self.load_state()
    
    def load_state(self):
        """Cargar estado desde archivo"""
        if not os.path.exists(self.state_file):
            print(f"❌ No se encontró archivo de estado: {self.state_file}")
            return False
        
        try:
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
            print(f"✅ Estado cargado desde: {self.state.get('timestamp', 'N/A')}")
            return True
        except Exception as e:
            print(f"❌ Error cargando estado: {str(e)}")
            return False
    
    def analyze_overall_performance(self):
        """Analizar rendimiento general"""
        if not self.state:
            return
        
        print("\n" + "=" * 60)
        print("📊 ANÁLISIS DE RENDIMIENTO GENERAL")
        print("=" * 60)
        
        # Estadísticas generales
        wins = self.state.get('wins', {})
        losses = self.state.get('losses', {})
        
        total_wins = sum(wins.values())
        total_losses = sum(losses.values())
        total_trades = total_wins + total_losses
        
        print(f"📈 Total de operaciones: {total_trades}")
        print(f"✅ Operaciones ganadoras: {total_wins}")
        print(f"❌ Operaciones perdedoras: {total_losses}")
        
        if total_trades > 0:
            win_rate = calculate_win_rate(total_wins, total_losses)
            print(f"🎯 Tasa de éxito: {win_rate:.2f}%")
            
            # Análisis de rentabilidad
            avg_payout = 1.80  # 80% según el script original
            breakeven_wr = 1 / avg_payout * 100
            print(f"📊 Tasa de éxito necesaria para breakeven: {breakeven_wr:.2f}%")
            
            if win_rate > breakeven_wr:
                print(f"✅ Estrategia RENTABLE (+{win_rate - breakeven_wr:.2f}% sobre breakeven)")
            else:
                print(f"❌ Estrategia NO RENTABLE ({win_rate - breakeven_wr:.2f}% bajo breakeven)")
        
        # Beneficio total
        total_profit = self.state.get('total_profit', 0)
        print(f"\n💰 Beneficio neto total: {format_currency(total_profit)}")
        
        # Stop losses
        if self.state.get('absolute_stop_loss_activated'):
            print("\n🚨 ADVERTENCIA: Stop loss absoluto fue activado")
        
        if self.state.get('monthly_stop_loss'):
            print(f"🚨 ADVERTENCIA: Stop loss mensual activado en {self.state.get('stop_loss_triggered_month')}")
    
    def analyze_by_pair(self):
        """Analizar rendimiento por par de divisas"""
        if not self.state:
            return
        
        print("\n" + "=" * 60)
        print("📊 ANÁLISIS POR PAR DE DIVISAS")
        print("=" * 60)
        
        wins = self.state.get('wins', {})
        losses = self.state.get('losses', {})
        
        # Combinar todos los pares
        all_pairs = set(list(wins.keys()) + list(losses.keys()))
        
        if not all_pairs:
            print("No hay datos de operaciones por par")
            return
        
        # Analizar cada par
        pair_stats = []
        
        for pair in sorted(all_pairs):
            pair_wins = wins.get(pair, 0)
            pair_losses = losses.get(pair, 0)
            pair_total = pair_wins + pair_losses
            
            if pair_total > 0:
                pair_wr = (pair_wins / pair_total) * 100
                pair_profit = (pair_wins * 0.80) - pair_losses  # Asumiendo payout 80%
                
                pair_stats.append({
                    'pair': pair,
                    'total': pair_total,
                    'wins': pair_wins,
                    'losses': pair_losses,
                    'win_rate': pair_wr,
                    'profit': pair_profit
                })
        
        # Ordenar por rentabilidad
        pair_stats.sort(key=lambda x: x['profit'], reverse=True)
        
        # Mostrar mejores pares
        print("\n🏆 MEJORES PARES (por beneficio):")
        for i, stats in enumerate(pair_stats[:5], 1):
            print(f"{i}. {stats['pair']}: {stats['total']} trades | "
                  f"{stats['wins']}W/{stats['losses']}L | "
                  f"{stats['win_rate']:.1f}% WR | "
                  f"Profit: {format_currency(stats['profit'] * 1000)}")  # x1000 asumiendo $1 por trade
        
        # Mostrar peores pares
        print("\n⚠️ PEORES PARES (por beneficio):")
        for i, stats in enumerate(pair_stats[-5:], 1):
            print(f"{i}. {stats['pair']}: {stats['total']} trades | "
                  f"{stats['wins']}W/{stats['losses']}L | "
                  f"{stats['win_rate']:.1f}% WR | "
                  f"Profit: {format_currency(stats['profit'] * 1000)}")
    
    def analyze_monthly_performance(self):
        """Analizar rendimiento mensual"""
        if not self.state:
            return
        
        print("\n" + "=" * 60)
        print("📊 ANÁLISIS MENSUAL")
        print("=" * 60)
        
        monthly_profits = self.state.get('monthly_profits', {})
        monthly_starting_capital = self.state.get('monthly_starting_capital', {})
        
        if not monthly_profits:
            print("No hay datos mensuales disponibles")
            return
        
        for month in sorted(monthly_profits.keys()):
            profit = monthly_profits[month]
            start_capital = monthly_starting_capital.get(month, 0)
            
            print(f"\n📅 {month}:")
            print(f"  Capital inicial: {format_currency(start_capital)}")
            print(f"  Beneficio/Pérdida: {format_currency(profit)}")
            
            if start_capital > 0:
                monthly_return = (profit / start_capital) * 100
                print(f"  Rendimiento: {monthly_return:.2f}%")
            
            if month == self.state.get('stop_loss_triggered_month'):
                print(f"  ⚠️ Stop loss mensual activado")
    
    def generate_recommendations(self):
        """Generar recomendaciones basadas en el análisis"""
        if not self.state:
            return
        
        print("\n" + "=" * 60)
        print("💡 RECOMENDACIONES")
        print("=" * 60)
        
        wins = self.state.get('wins', {})
        losses = self.state.get('losses', {})
        
        # Calcular estadísticas generales
        total_wins = sum(wins.values())
        total_losses = sum(losses.values())
        total_trades = total_wins + total_losses
        
        if total_trades > 0:
            win_rate = calculate_win_rate(total_wins, total_losses)
            
            # Recomendaciones basadas en tasa de éxito
            if win_rate < 55.56:  # Breakeven para 80% payout
                print("❌ La tasa de éxito está por debajo del breakeven (55.56%)")
                print("   Considera:")
                print("   - Ajustar los niveles RSI (probar 25/75 o 35/65)")
                print("   - Filtrar pares con bajo rendimiento")
                print("   - Revisar el período RSI (probar 9 o 21)")
            elif win_rate < 60:
                print("⚠️ La tasa de éxito es marginal")
                print("   Considera:")
                print("   - Optimizar los pares operados")
                print("   - Ajustar el tamaño de posición")
            else:
                print("✅ Buena tasa de éxito, mantén la estrategia")
        
        # Recomendaciones por pares
        poor_pairs = []
        for pair in wins.keys():
            pair_total = wins.get(pair, 0) + losses.get(pair, 0)
            if pair_total >= 10:  # Solo pares con suficientes trades
                pair_wr = wins.get(pair, 0) / pair_total * 100
                if pair_wr < 50:
                    poor_pairs.append(pair)
        
        if poor_pairs:
            print(f"\n⚠️ Considera eliminar estos pares de bajo rendimiento:")
            print(f"   {', '.join(poor_pairs)}")
        
        # Recomendaciones de gestión de riesgo
        if self.state.get('absolute_stop_loss_activated'):
            print("\n🚨 El stop loss absoluto fue activado")
            print("   - Revisa completamente la estrategia antes de continuar")
            print("   - Considera reducir el tamaño de posición")
            print("   - Implementa filtros adicionales para las señales")
        
        print("\n📌 Recomendaciones generales:")
        print("   - Siempre opera primero en cuenta PRACTICE")
        print("   - Monitorea constantemente los resultados")
        print("   - Ajusta parámetros gradualmente, no drásticamente")
        print("   - Mantén un diario de trading para análisis cualitativo")

def main():
    """Función principal del analizador"""
    print("=" * 60)
    print("   ANALIZADOR DE ESTRATEGIA RSI")
    print("=" * 60)
    
    analyzer = StrategyAnalyzer()
    
    if analyzer.state:
        analyzer.analyze_overall_performance()
        analyzer.analyze_by_pair()
        analyzer.analyze_monthly_performance()
        analyzer.generate_recommendations()
    else:
        print("\n❌ No se pudo cargar el estado para análisis")
        print("Asegúrate de que la estrategia haya guardado al menos un estado")

if __name__ == "__main__":
    main()