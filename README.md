# checkerV2-CC / Validor de tarjetas de credito / BSZ v2
Este proyecto es un **validador de tarjetas de crédito** desarrollado en HTML, CSS y JavaScript. Utiliza la **API CHKR** para validar tarjetas de crédito de manera rápida y eficiente. El sistema permite pegar una lista de tarjetas de crédito en un área de texto y validar cada una de ellas para determinar si son válidas, no válidas o desconocidas.

## Descripción

Este validador toma una lista de tarjetas de crédito (una por línea), las valida y las clasifica en tres categorías:

- **Vivas (Live)**: Tarjetas válidas.
- **Muertas (Die)**: Tarjetas no válidas.
- **Desconocidas (Unknown)**: Tarjetas cuya información no pudo ser validada.

El resultado de la validación se muestra en tiempo real, y se pueden copiar los resultados al portapapeles para su posterior uso.

### Características

- **Interfaz fácil de usar**: Con un diseño minimalista y botones claros.
- **Progress bar**: Muestra el progreso de la validación de tarjetas.
- **Resumen**: Muestra la cantidad de tarjetas vivas, muertas y desconocidas.
- **Resultados**: Muestra los resultados de cada tarjeta con información detallada.
- **Copiar resultados**: Permite copiar los resultados validados al portapapeles.

## API Utilizada

Este proyecto utiliza la **API de CHKR** para validar las tarjetas de crédito. La API recibe las tarjetas a través de una solicitud `POST` y devuelve información sobre su estado (válida, no válida o desconocida).

### Endpoint de la API

- URL: `https://api.chkr.cc/`
- Método: `POST`
- Parámetros:
  - `data`: La tarjeta de crédito a validar (en formato `card_number|expiration|cvv`).
  - `charge`: Configurado como `'false'` para solo realizar la validación sin generar un cargo.

### Límite de Validaciones

La API tiene un **límite gratuito** de **10 validaciones por hora**. Si se alcanza este límite, el sistema devolverá un error indicando que se ha superado el número máximo de validaciones permitidas. Para obtener más validaciones, es necesario suscribirse a un plan premium de la API.

## Instrucciones

1. **Pegar las tarjetas de crédito**: Copia una lista de tarjetas de crédito (una por línea) en el área de texto.
2. **Validar tarjetas**: Haz clic en el botón "Validar Todas" para iniciar la validación de todas las tarjetas.
3. **Ver los resultados**: Los resultados se mostrarán debajo del área de texto, indicando si cada tarjeta es válida, no válida o desconocida.
4. **Copiar resultados**: Haz clic en el botón "Copiar Resultados" para copiar los resultados al portapapeles.

## Instalación

Este proyecto está desarrollado completamente en HTML, CSS y JavaScript, por lo que no se necesita ninguna instalación. Simplemente descarga el archivo `index.html` y ábrelo en tu navegador.

## Bot Telegram Requerimientos : 
```bash
pip install python-telegram-bot==22.0

python3 -m venv env

source env/bin/activate

pip install aiohttp
```
