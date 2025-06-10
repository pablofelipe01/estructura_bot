# config.py
# Configuración de la estrategia RSI para IQ Option

# Credenciales IQ Option
IQ_EMAIL = "pablofelipe@me.com"
IQ_PASSWORD = "DaMa0713"
ACCOUNT_TYPE = "REAL"  # "PRACTICE" o "REAL"

# Pares de divisas a operar (lista ajustada del algoritmo)
FOREX_PAIRS = [
    "AUDCHF", "CADCHF", "EURAUD", "EURCAD", "EURCHF",
    "GBPAUD", "GBPCAD", "GBPCHF", "GBPNZD", "NZDUSD",
    "EURGBP", "EURJPY", "GBPUSD", "USDJPY"
]

# Configuración RSI - LÓGICA INVERTIDA
RSI_PERIOD = 14
OVERSOLD_LEVEL = 35    # Nivel para señal PUT (invertido)
OVERBOUGHT_LEVEL = 65  # Nivel para señal CALL (invertido)

# Configuración de opciones binarias
EXPIRY_MINUTES = 5  # Tiempo de expiración en minutos
CANDLE_TIMEFRAME = 300  # 5 minutos en segundos (para RSI)

# Gestión de riesgo - Stop Loss
ABSOLUTE_STOP_LOSS_PERCENT = 0.75  # 75% de pérdida del capital inicial
MONTHLY_STOP_LOSS_PERCENT = 0.40   # 40% de pérdida mensual

# Tamaño de posición
POSITION_SIZE_PERCENT = 0.05  # 5% del capital disponible
MIN_POSITION_SIZE = 5000      # Mínimo $5,000
MAX_POSITION_SIZE = 10000     # Máximo $10,000

# Control de operaciones
MIN_TIME_BETWEEN_SIGNALS = 60  # Minutos entre señales del mismo par (1 hora)
MAX_CONSECUTIVE_LOSSES = 999   # Pérdidas consecutivas antes de bloquear el par (prácticamente desactivado)

# Configuración de activos
# Los sufijos más comunes en IQ Option son:
# - Sin sufijo: activo estándar (ej: "EURUSD")
# - "-OTC": Over The Counter, disponible 24/7
# - "-op": Opción estándar (a veces usado para diferenciar de CFDs)
ALLOWED_ASSET_SUFFIXES = ["-OTC", "-op", ""]  # Incluir cadena vacía para versión estándar
PRIORITY_SUFFIX = None  # None = no priorizar, usar el primero disponible

# Modo de estrategia
STRATEGY_MODE = "CALL_PUT"  # Estrategia original con CALL y PUT

# Configuración de logging
LOG_LEVEL = "INFO"
LOG_FILE = "iqoption_strategy.log"

# Configuración de caché y timeouts
OPCODE_CACHE_TTL = 3600  # 1 hora
ASSET_STATUS_CACHE_TTL = 300  # 5 minutos
API_TIMEOUT = 15  # Timeout para llamadas API en segundos
MAX_FREEZE_COUNT = 5  # Número máximo de timeouts antes de reiniciar

# Configuración de guardado de estado
STATE_FILE = "strategy_state.json"
SAVE_STATE_INTERVAL = 30  # Guardar estado cada N ciclos