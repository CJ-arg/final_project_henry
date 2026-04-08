# Casos de Prueba (Test Contracts)

Este directorio contiene contratos de prueba diseñados para evaluar la efectividad y precisión del **Agente Autónomo de Comparación de Contratos de LegalMove**.

Se componen de al menos dos pares de documentos que el sistema procesa.

## Caso de Prueba 1: Contrato de Alquiler en PDF
- **Original**: `CONTRATO DE ALQUILER version 1 henry.pdf`
- **Adenda**: `CONTRATO DE ALQUILER version 2 henry.pdf`
- **Descripción**: Evalúa la capacidad técnica del motor de Visión Multimodal en la conversión de archivos PDF a lista de imágenes dinámicas. En la extracción de cambios, el sistema debe ser capaz de identificar modificaciones sutiles en la duración (extensión a 3 años), alteraciones en precios y pagos (ajustes del IPC y la cuota inicial), así como modificaciones puramente legales, como la jurisdicción (cambio a La Plata).

## Caso de Prueba 2: Contrato Genérico en Imagen
- **Original**: `original.jpg`
- **Adenda**: `amendment.jpg`
- **Descripción**: Evalúa el sistema frente a escaneos nativos e imágenes simples (JPEG). Demuestra las aptitudes del sistema multi-agente frente a la asimetría documental directa donde la estructura de las cláusulas se correlaciona con la memoria temporal inyectada desde el Agente Analista (Contextualization) hacia el Agente Auditor (Extraction).

---
*Para procesar estos contratos en la plataforma, asegúrate de proveer las rutas relativas en la configuración del archivo `main.py` antes de su ejecución puntual.*
