# 🔄 CAMBIOS IMPORTANTES EN LA ESTRATEGIA RSI

## ⚡ LÓGICA INVERTIDA (NUEVO)

La estrategia ahora usa una **lógica invertida** basada en el algoritmo de QuantConnect:

### Señales de Trading:

| RSI | Señal Anterior | Señal NUEVA | Razonamiento |
|-----|----------------|-------------|--------------|
| ≤ 35 | CALL | **PUT** 🔴 | Sobreventa → Se espera reversión bajista |
| ≥ 65 | PUT | **CALL** 🟢 | Sobrecompra → Se espera reversión alcista |

### ¿Por qué la inversión?

Esta lógica sigue el principio de **momentum** en lugar de reversión a la media:
- Cuando RSI está muy bajo (sobreventa), el momentum es bajista → PUT
- Cuando RSI está muy alto (sobrecompra), el momentum es alcista → CALL

## 📊 Otros Cambios Importantes

### 1. **Niveles RSI Ajustados**
- **Antes**: 30/70
- **Ahora**: 35/65
- Niveles más conservadores para reducir señales falsas

### 2. **Timeframe RSI**
- Confirmado en **5 minutos** (300 segundos)
- Consistente con el algoritmo de QuantConnect

### 3. **Lista de Pares Reducida**
- **Antes**: 17 pares
- **Ahora**: 14 pares
- Removidos: EURNZD, GBPJPY, EURUSD

### 4. **Horario de Trading**
- Mantiene operación 24/7 (sin restricciones)
- Puedes ajustar si prefieres horario específico

## 🚀 Cómo Ejecutar

```bash
# 1. Actualizar configuración si es necesario
nano config.py

# 2. Ejecutar estrategia
python main.py
```

## ⚠️ IMPORTANTE

**Esta es una estrategia completamente diferente** a la anterior. Los resultados históricos no son comparables. Se recomienda:

1. **Probar primero en cuenta PRACTICE**
2. **Monitorear cuidadosamente las primeras operaciones**
3. **Ajustar tamaño de posición si es necesario**

## 📈 Expectativas

- **Mayor frecuencia de operaciones** en tendencias fuertes
- **Mejor desempeño** en mercados con momentum claro
- **Posibles pérdidas** en mercados laterales

## 🔧 Ajustes Opcionales

Si quieres volver a la lógica tradicional, cambia en `config.py`:

```python
# Para lógica tradicional (reversión a la media)
OVERSOLD_LEVEL = 30    # CALL en sobreventa
OVERBOUGHT_LEVEL = 70  # PUT en sobrecompra
```

Y ajusta las señales en `strategy.py` líneas ~280-290.