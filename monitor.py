# monitor.py
# Script de monitoreo y mantenimiento para el Trading Bot

import os
import sys
import json
import time
import requests
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import schedule

# Configuración
MONITOR_CONFIG = {
    "api_url": os.getenv("BOT_URL", "http://localhost:8000"),
    "api_key": os.getenv("API_KEY", "your-api-key-here"),
    "check_interval": 300,  # 5 minutos
    "alert_email": os.getenv("ALERT_EMAIL", ""),
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "smtp_user": os.getenv("SMTP_USER", ""),
    "smtp_pass": os.getenv("SMTP_PASS", ""),
    "max_consecutive_losses": 5,
    "max_drawdown_percent": 20,
    "min_balance_alert": 10000,
    "log_file": "monitor.log"
}

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(MONITOR_CONFIG["log_file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingBotMonitor:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {MONITOR_CONFIG['api_key']}"
        }
        self.last_status = None
        self.alert_history = []
        self.initial_balance = None
        
    def check_bot_status(self) -> Optional[Dict]:
        """Verificar el estado del bot"""
        try:
            response = requests.get(
                f"{MONITOR_CONFIG['api_url']}/api/status",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo estado: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error conectando con el bot: {str(e)}")
            return None
    
    def send_alert(self, subject: str, message: str, priority: str = "normal"):
        """Enviar alerta por email"""
        if not MONITOR_CONFIG["alert_email"] or not MONITOR_CONFIG["smtp_user"]:
            logger.warning("Email no configurado, alerta no enviada")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = MONITOR_CONFIG["smtp_user"]
            msg['To'] = MONITOR_CONFIG["alert_email"]
            msg['Subject'] = f"[Trading Bot Alert - {priority.upper()}] {subject}"
            
            body = f"""
            Trading Bot Alert
            =================
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Priority: {priority.upper()}
            
            {message}
            
            --
            This is an automated message from Trading Bot Monitor
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(MONITOR_CONFIG["smtp_server"], MONITOR_CONFIG["smtp_port"]) as server:
                server.starttls()
                server.login(MONITOR_CONFIG["smtp_user"], MONITOR_CONFIG["smtp_pass"])
                server.send_message(msg)
            
            logger.info(f"Alerta enviada: {subject}")
            self.alert_history.append({
                "time": datetime.now(),
                "subject": subject,
                "priority": priority
            })
            
        except Exception as e:
            logger.error(f"Error enviando alerta: {str(e)}")
    
    def check_trading_performance(self, status: Dict):
        """Verificar el rendimiento del trading"""
        alerts = []
        
        # Verificar drawdown
        if self.initial_balance and status.get("balance"):
            current_balance = status["balance"]
            drawdown_percent = ((self.initial_balance - current_balance) / self.initial_balance) * 100
            
            if drawdown_percent >= MONITOR_CONFIG["max_drawdown_percent"]:
                alerts.append({
                    "type": "drawdown",
                    "priority": "high",
                    "message": f"Drawdown crítico: {drawdown_percent:.2f}% (Límite: {MONITOR_CONFIG['max_drawdown_percent']}%)"
                })
        
        # Verificar balance mínimo
        if status.get("balance", 0) < MONITOR_CONFIG["min_balance_alert"]:
            alerts.append({
                "type": "low_balance",
                "priority": "high",
                "message": f"Balance bajo: ${status.get('balance', 0):,.2f} (Mínimo: ${MONITOR_CONFIG['min_balance_alert']:,.2f})"
            })
        
        # Verificar pérdidas consecutivas por par
        if status.get("pair_stats"):
            for pair, stats in status["pair_stats"].items():
                if stats.get("consecutive_losses", 0) >= MONITOR_CONFIG["max_consecutive_losses"]:
                    alerts.append({
                        "type": "consecutive_losses",
                        "priority": "medium",
                        "message": f"{pair}: {stats['consecutive_losses']} pérdidas consecutivas"
                    })
        
        # Verificar tasa de éxito
        if status.get("win_rate", 100) < 40:
            alerts.append({
                "type": "low_win_rate",
                "priority": "medium",
                "message": f"Tasa de éxito baja: {status.get('win_rate', 0):.2f}%"
            })
        
        return alerts
    
    def check_system_health(self, status: Dict):
        """Verificar la salud del sistema"""
        alerts = []
        
        # Bot detenido
        if status.get("status") != "running":
            alerts.append({
                "type": "bot_stopped",
                "priority": "critical",
                "message": "El bot no está en ejecución"
            })
        
        # Conexión perdida
        if not status.get("connected", False):
            alerts.append({
                "type": "connection_lost",
                "priority": "high",
                "message": "Bot desconectado de IQ Option"
            })
        
        # Stop loss activo
        if status.get("stop_loss_active", False):
            alerts.append({
                "type": "stop_loss",
                "priority": "high",
                "message": "Stop loss activado"
            })
        
        return alerts
    
    def generate_daily_report(self):
        """Generar reporte diario"""
        status = self.check_bot_status()
        if not status:
            return
        
        report = f"""
        REPORTE DIARIO - TRADING BOT
        ============================
        Fecha: {datetime.now().strftime('%Y-%m-%d')}
        
        RESUMEN GENERAL
        ---------------
        Estado: {status.get('status', 'unknown').upper()}
        Balance: ${status.get('balance', 0):,.2f}
        Capital Inicial: ${status.get('initial_capital', 0):,.2f}
        Beneficio Total: ${status.get('total_profit', 0):,.2f}
        Beneficio Diario: ${status.get('daily_profit', 0):,.2f}
        
        ESTADÍSTICAS DE TRADING
        -----------------------
        Total Operaciones: {status.get('total_trades', 0)}
        Victorias: {status.get('wins', 0)}
        Derrotas: {status.get('losses', 0)}
        Empates: {status.get('ties', 0)}
        Tasa de Éxito: {status.get('win_rate', 0):.2f}%
        
        ÓRDENES ACTIVAS: {len(status.get('active_orders', []))}
        """
        
        if status.get('pair_stats'):
            report += "\n\nESTADÍSTICAS POR PAR\n--------------------\n"
            for pair, stats in status['pair_stats'].items():
                total = stats['wins'] + stats['losses'] + stats['ties']
                if total > 0:
                    report += f"{pair}: {total} trades | {stats['wins']}W/{stats['losses']}L/{stats['ties']}T\n"
        
        report += f"\n\nALERTAS ENVIADAS HOY: {len([a for a in self.alert_history if a['time'].date() == datetime.now().date()])}"
        
        self.send_alert("Reporte Diario", report, "normal")
        logger.info("Reporte diario enviado")
    
    def run_check(self):
        """Ejecutar verificación completa"""
        logger.info("Ejecutando verificación...")
        
        status = self.check_bot_status()
        if not status:
            self.send_alert(
                "Bot No Responde",
                "No se puede conectar con el bot. Verifica que esté en ejecución.",
                "critical"
            )
            return
        
        # Guardar balance inicial
        if self.initial_balance is None and status.get("initial_capital"):
            self.initial_balance = status["initial_capital"]
        
        # Verificar rendimiento
        performance_alerts = self.check_trading_performance(status)
        
        # Verificar salud del sistema
        system_alerts = self.check_system_health(status)
        
        # Procesar alertas
        all_alerts = performance_alerts + system_alerts
        
        # Filtrar alertas ya enviadas recientemente (últimas 2 horas)
        recent_cutoff = datetime.now() - timedelta(hours=2)
        recent_alerts = [a['subject'] for a in self.alert_history if a['time'] > recent_cutoff]
        
        for alert in all_alerts:
            alert_key = f"{alert['type']}_{alert['message'][:20]}"
            if alert_key not in recent_alerts:
                self.send_alert(
                    f"Trading Bot - {alert['type'].replace('_', ' ').title()}",
                    alert['message'],
                    alert['priority']
                )
        
        # Log estado actual
        logger.info(f"Estado: {status.get('status')} | Balance: ${status.get('balance', 0):,.2f} | Win Rate: {status.get('win_rate', 0):.2f}%")
        
        # Guardar último estado
        self.last_status = status
    
    def cleanup_old_logs(self):
        """Limpiar logs antiguos"""
        try:
            # Mantener solo los últimos 7 días de logs
            cutoff_date = datetime.now() - timedelta(days=7)
            
            # Leer y filtrar logs
            with open(MONITOR_CONFIG["log_file"], 'r') as f:
                lines = f.readlines()
            
            filtered_lines = []
            for line in lines:
                try:
                    # Extraer fecha del log
                    date_str = line.split(' - ')[0]
                    log_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S,%f')
                    if log_date > cutoff_date:
                        filtered_lines.append(line)
                except:
                    # Si no se puede parsear, mantener la línea
                    filtered_lines.append(line)
            
            # Escribir logs filtrados
            with open(MONITOR_CONFIG["log_file"], 'w') as f:
                f.writelines(filtered_lines)
            
            logger.info("Logs antiguos limpiados")
            
        except Exception as e:
            logger.error(f"Error limpiando logs: {str(e)}")
    
    def start(self):
        """Iniciar el monitor"""
        logger.info("=== Trading Bot Monitor Iniciado ===")
        logger.info(f"URL: {MONITOR_CONFIG['api_url']}")
        logger.info(f"Intervalo de verificación: {MONITOR_CONFIG['check_interval']} segundos")
        
        # Verificación inicial
        self.run_check()
        
        # Programar tareas
        schedule.every(MONITOR_CONFIG["check_interval"]).seconds.do(self.run_check)
        schedule.every().day.at("09:00").do(self.generate_daily_report)
        schedule.every().day.at("00:00").do(self.cleanup_old_logs)
        
        # Loop principal
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Monitor detenido por el usuario")
                break
            except Exception as e:
                logger.error(f"Error en el loop principal: {str(e)}")
                time.sleep(60)  # Esperar antes de reintentar

def main():
    """Función principal"""
    monitor = TradingBotMonitor()
    monitor.start()

if __name__ == "__main__":
    main()