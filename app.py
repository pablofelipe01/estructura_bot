# app.py
# Backend API para controlar la estrategia de trading

import os
import sys
import json
import asyncio
import threading
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Importar la estrategia
from strategy import MultiCurrencyRSIBinaryOptionsStrategy
from config import *
from utils import setup_logger

# Configuración de seguridad
API_KEY = os.getenv("API_KEY", "your-secure-api-key-here")  # Cambiar en producción
security = HTTPBearer()

# Logger para el backend
logger = setup_logger('backend', 'backend.log')

# Estado global de la aplicación
class TradingBotState:
    def __init__(self):
        self.strategy: Optional[MultiCurrencyRSIBinaryOptionsStrategy] = None
        self.strategy_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.websocket_clients = []
        self.last_update = {}
        self.config = {
            "email": IQ_EMAIL,
            "password": IQ_PASSWORD,
            "account_type": ACCOUNT_TYPE,
            "position_size_percent": POSITION_SIZE_PERCENT,
            "min_position_size": MIN_POSITION_SIZE,
            "max_position_size": MAX_POSITION_SIZE,
            "oversold_level": OVERSOLD_LEVEL,
            "overbought_level": OVERBOUGHT_LEVEL,
            "min_time_between_signals": MIN_TIME_BETWEEN_SIGNALS,
            "forex_pairs": FOREX_PAIRS,
            "monthly_stop_loss_percent": MONTHLY_STOP_LOSS_PERCENT,
            "absolute_stop_loss_percent": ABSOLUTE_STOP_LOSS_PERCENT
        }

bot_state = TradingBotState()

# Modelos Pydantic
class ConfigUpdate(BaseModel):
    position_size_percent: Optional[float] = None
    min_position_size: Optional[float] = None
    max_position_size: Optional[float] = None
    oversold_level: Optional[int] = None
    overbought_level: Optional[int] = None
    min_time_between_signals: Optional[int] = None
    forex_pairs: Optional[List[str]] = None
    monthly_stop_loss_percent: Optional[float] = None
    absolute_stop_loss_percent: Optional[float] = None

class LoginCredentials(BaseModel):
    email: str
    password: str
    account_type: str = "PRACTICE"

# Verificación de API Key
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication credentials",
        )
    return credentials.credentials

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Trading Bot Backend")
    # Iniciar tarea de broadcast de estado
    asyncio.create_task(broadcast_status())
    yield
    # Shutdown
    logger.info("🛑 Shutting down Trading Bot Backend")
    if bot_state.is_running:
        stop_strategy()

# Crear aplicación FastAPI
app = FastAPI(
    title="Trading Bot API",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funciones auxiliares
def get_strategy_status() -> Dict[str, Any]:
    """Obtener estado actual de la estrategia"""
    if not bot_state.strategy:
        return {
            "status": "stopped",
            "message": "Strategy not initialized"
        }
    
    try:
        balance = bot_state.strategy.iqoption.get_balance() if bot_state.strategy.iqoption.check_connect() else 0
        
        # Calcular estadísticas totales
        total_wins = sum(bot_state.strategy.wins.values())
        total_losses = sum(bot_state.strategy.losses.values())
        total_ties = sum(bot_state.strategy.ties.values())
        total_trades = total_wins + total_losses + total_ties
        win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
        
        # Obtener órdenes activas
        active_orders = []
        for pair, orders in bot_state.strategy.active_options.items():
            for order in orders:
                active_orders.append({
                    "pair": pair,
                    "type": order["type"],
                    "size": order["size"],
                    "entry_time": order["entry_time"].isoformat(),
                    "expiry_time": order["expiry_time"].isoformat(),
                    "rsi": order.get("rsi", 0)
                })
        
        # Estadísticas por par
        pair_stats = {}
        for pair in bot_state.strategy.forex_pairs:
            if pair in bot_state.strategy.wins or pair in bot_state.strategy.losses:
                pair_stats[pair] = {
                    "wins": bot_state.strategy.wins.get(pair, 0),
                    "losses": bot_state.strategy.losses.get(pair, 0),
                    "ties": bot_state.strategy.ties.get(pair, 0),
                    "consecutive_losses": bot_state.strategy.consecutive_losses.get(pair, 0)
                }
        
        return {
            "status": "running" if bot_state.is_running else "stopped",
            "connected": bot_state.strategy.iqoption.check_connect() if bot_state.strategy else False,
            "balance": balance,
            "initial_capital": bot_state.strategy.initial_capital,
            "total_profit": bot_state.strategy.total_profit,
            "daily_profit": bot_state.strategy.daily_profit,
            "total_trades": total_trades,
            "wins": total_wins,
            "losses": total_losses,
            "ties": total_ties,
            "win_rate": round(win_rate, 2),
            "active_orders": active_orders,
            "pair_stats": pair_stats,
            "valid_pairs": bot_state.strategy.valid_pairs,
            "stop_loss_active": bot_state.strategy.absolute_stop_loss_activated or bot_state.strategy.monthly_stop_loss,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def run_strategy_thread():
    """Ejecutar la estrategia en un thread separado"""
    try:
        bot_state.strategy.run()
    except Exception as e:
        logger.error(f"Strategy thread error: {str(e)}")
        bot_state.is_running = False

def stop_strategy():
    """Detener la estrategia"""
    if bot_state.strategy and bot_state.is_running:
        bot_state.is_running = False
        # La estrategia se detendrá en el próximo ciclo
        logger.info("Stopping strategy...")
        if bot_state.strategy_thread:
            bot_state.strategy_thread.join(timeout=10)
        bot_state.strategy = None
        bot_state.strategy_thread = None

async def broadcast_status():
    """Enviar actualizaciones de estado a todos los clientes WebSocket"""
    while True:
        if bot_state.is_running and bot_state.websocket_clients:
            status = get_strategy_status()
            # Enviar solo si hay cambios significativos
            if status != bot_state.last_update:
                bot_state.last_update = status
                disconnected_clients = []
                for client in bot_state.websocket_clients:
                    try:
                        await client.send_json(status)
                    except:
                        disconnected_clients.append(client)
                
                # Remover clientes desconectados
                for client in disconnected_clients:
                    bot_state.websocket_clients.remove(client)
        
        await asyncio.sleep(2)  # Actualizar cada 2 segundos

# Endpoints de la API
@app.get("/api")
async def api_root():
    return {"message": "Trading Bot API", "version": "1.0.0"}

@app.get("/api/status")
async def get_status(token: str = Depends(verify_token)):
    """Obtener estado actual del bot"""
    return get_strategy_status()

@app.post("/api/start")
async def start_bot(credentials: LoginCredentials, token: str = Depends(verify_token)):
    """Iniciar el bot de trading"""
    if bot_state.is_running:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    try:
        # Actualizar credenciales
        bot_state.config["email"] = credentials.email
        bot_state.config["password"] = credentials.password
        bot_state.config["account_type"] = credentials.account_type
        
        # Crear nueva instancia de la estrategia
        bot_state.strategy = MultiCurrencyRSIBinaryOptionsStrategy(
            email=credentials.email,
            password=credentials.password,
            account_type=credentials.account_type
        )
        
        # Aplicar configuración actual
        bot_state.strategy.position_size_percent = bot_state.config["position_size_percent"]
        bot_state.strategy.min_position_size = bot_state.config["min_position_size"]
        bot_state.strategy.max_position_size = bot_state.config["max_position_size"]
        bot_state.strategy.oversold_level = bot_state.config["oversold_level"]
        bot_state.strategy.overbought_level = bot_state.config["overbought_level"]
        bot_state.strategy.min_time_between_signals = bot_state.config["min_time_between_signals"]
        bot_state.strategy.forex_pairs = bot_state.config["forex_pairs"]
        
        # Iniciar en thread separado
        bot_state.is_running = True
        bot_state.strategy_thread = threading.Thread(target=run_strategy_thread, daemon=True)
        bot_state.strategy_thread.start()
        
        return {"status": "success", "message": "Bot started successfully"}
    
    except Exception as e:
        bot_state.is_running = False
        bot_state.strategy = None
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stop")
async def stop_bot(token: str = Depends(verify_token)):
    """Detener el bot de trading"""
    if not bot_state.is_running:
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    stop_strategy()
    return {"status": "success", "message": "Bot stopped successfully"}

@app.get("/api/config")
async def get_config(token: str = Depends(verify_token)):
    """Obtener configuración actual"""
    # No devolver credenciales sensibles
    safe_config = bot_state.config.copy()
    safe_config["email"] = safe_config["email"][:3] + "***" + safe_config["email"][-10:] if safe_config["email"] else ""
    safe_config["password"] = "***"
    return safe_config

@app.post("/api/config")
async def update_config(config: ConfigUpdate, token: str = Depends(verify_token)):
    """Actualizar configuración del bot"""
    # Actualizar solo los campos proporcionados
    for field, value in config.dict(exclude_unset=True).items():
        if value is not None:
            bot_state.config[field] = value
            # Si el bot está corriendo, actualizar también la estrategia
            if bot_state.strategy and bot_state.is_running:
                if field == "forex_pairs":
                    # Para forex_pairs, necesitamos revalidar
                    bot_state.strategy.forex_pairs = value
                    bot_state.strategy.check_valid_pairs()
                elif field == "monthly_stop_loss_percent":
                    # Actualizar el porcentaje de stop loss mensual
                    bot_state.strategy.monthly_stop_loss = False  # Reset flag
                    bot_state.strategy.stop_loss_triggered_month = None
                elif hasattr(bot_state.strategy, field):
                    setattr(bot_state.strategy, field, value)
    
    return {"status": "success", "config": bot_state.config}

@app.get("/api/available-pairs")
async def get_available_pairs(token: str = Depends(verify_token)):
    """Obtener todos los pares forex disponibles"""
    if bot_state.strategy:
        # Obtener todos los pares posibles de los activos disponibles
        all_pairs = []
        try:
            all_assets = bot_state.strategy.iqoption.get_all_open_time()
            if all_assets:
                for option_type in ["binary", "turbo"]:
                    if option_type in all_assets:
                        for asset_name in all_assets[option_type].keys():
                            # Extraer el par base sin sufijos
                            base_pair = asset_name.replace("-OTC", "").replace("-op", "")
                            if len(base_pair) == 6 and base_pair.isalpha():
                                if base_pair not in all_pairs:
                                    all_pairs.append(base_pair)
                all_pairs.sort()
        except:
            pass
        return {"pairs": all_pairs, "active_pairs": bot_state.strategy.forex_pairs}
    else:
        # Devolver lista por defecto
        from config import FOREX_PAIRS
        return {"pairs": FOREX_PAIRS, "active_pairs": FOREX_PAIRS}

@app.get("/api/logs")
async def get_logs(lines: int = 100, token: str = Depends(verify_token)):
    """Obtener últimas líneas del log"""
    try:
        with open(LOG_FILE, 'r') as f:
            all_lines = f.readlines()
            return {"logs": all_lines[-lines:]}
    except Exception as e:
        return {"logs": [], "error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para actualizaciones en tiempo real"""
    await websocket.accept()
    bot_state.websocket_clients.append(websocket)
    
    #try:
        # Enviar estado inicial
        #await websocket.send_json(get_strategy_status())
        
        # Mantener la conexión abierta
        #while True:
            # Esperar mensajes del cliente (ping/pong)
            #data = await websocket.receive_text()
            #if data == "ping":
                #await websocket.send_text("pong")
    
    #except WebSocketDisconnect:
        #bot_state.websocket_clients.remove(websocket)
    #except Exception as e:
        #logger.error(f"WebSocket error: {str(e)}")
        #if websocket in bot_state.websocket_clients:
            #bot_state.websocket_clients.remove(websocket)

# Servir archivos estáticos (frontend)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )