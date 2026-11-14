# SoundSausage — manual

Versión 0.23.0. Un editor de audio intuitivo y fácil de usar, con todas las herramientas donde las esperas. Este manual describe las funciones disponibles, los efectos y sus límites prácticos.

<!-- soundsausage-contents:start -->
<a id="ss-contents"></a>

## Índice

Haz clic en un tema para ir a él. El botón Índice de arriba permite volver aquí.

- [1. Idioma y ayuda](#ss-topic-1-idioma-y-ayuda)
- [2. Inicio rápido y espacio de trabajo](#ss-topic-2-inicio-rapido-y-espacio-de-trabajo)
- [3. Archivos, proyectos y recuperación](#ss-topic-3-archivos-proyectos-y-recuperacion)
  - [MP3 y WAV](#ss-topic-mp3-y-wav)
  - [Metadatos MP3 después de editar](#ss-topic-metadatos-mp3-despues-de-editar)
- [4. Reproducción, zoom y dispositivos](#ss-topic-4-reproduccion-zoom-y-dispositivos)
- [5. Grabar](#ss-topic-5-grabar)
- [6. Selección, canales y edición](#ss-topic-6-seleccion-canales-y-edicion)
  - [Editar muestras individuales](#ss-topic-editar-muestras-individuales)
  - [Dibujar forma de onda](#ss-topic-dibujar-forma-de-onda)
- [7. Aplicar efectos](#ss-topic-7-aplicar-efectos)
  - [Amplitud](#ss-topic-amplitud)
    - [Amplificar / fundido](#ss-topic-amplificar-fundido)
    - [Mezclador de canales](#ss-topic-mezclador-de-canales)
    - [Procesamiento de dinámica](#ss-topic-procesamiento-de-dinamica)
    - [Envolvente de volumen](#ss-topic-envolvente-de-volumen)
    - [Normalizar](#ss-topic-normalizar)
    - [Polaridad, sentido y silencio](#ss-topic-polaridad-sentido-y-silencio)
  - [Ecualización y filtros](#ss-topic-ecualizacion-y-filtros)
    - [Ecualizador gráfico](#ss-topic-ecualizador-grafico)
    - [Ecualizador paramétrico](#ss-topic-ecualizador-parametrico)
    - [Filtros](#ss-topic-filtros)
  - [Retardo, eco y reverberación](#ss-topic-retardo-eco-y-reverberacion)
    - [Efectos de retardo → Retardo](#ss-topic-efectos-de-retardo-retardo)
    - [Eco](#ss-topic-eco)
    - [Reverberación](#ss-topic-reverberacion)
  - [Reducción de ruido y clics](#ss-topic-reduccion-de-ruido-y-clics)
    - [Estimación del ruido → Perfil de ruido fijo](#ss-topic-estimacion-del-ruido-perfil-de-ruido-fijo)
    - [Eliminación de clics](#ss-topic-eliminacion-de-clics)
  - [Tiempo y tono](#ss-topic-tiempo-y-tono)
    - [Tiempo/tono → Estirar duración](#ss-topic-tiempo-tono-estirar-duracion)
    - [Cambio de tono](#ss-topic-cambio-de-tono)
  - [Efectos especiales](#ss-topic-efectos-especiales)
    - [Especial → Distorsión](#ss-topic-especial-distorsion)
    - [Convolución](#ss-topic-convolucion)
- [8. Generar, analizar y convertir](#ss-topic-8-generar-analizar-y-convertir)
- [9. Multipista y automatización](#ss-topic-9-multipista-y-automatizacion)
- [10. Efectos de pista, plug-ins y grabación](#ss-topic-10-efectos-de-pista-plug-ins-y-grabacion)
  - [VST3, LV2 y LADSPA](#ss-topic-vst3-lv2-y-ladspa)
  - [Compensación del retardo de plug-ins](#ss-topic-compensacion-del-retardo-de-plug-ins)
  - [Acompañamiento y sincronización](#ss-topic-acompanamiento-y-sincronizacion)
  - [Punch-in/out](#ss-topic-punch-in-out)
- [11. Grabar con acompañamiento](#ss-topic-11-grabar-con-acompanamiento)
- [12. Atajos, favoritos y solución de problemas](#ss-topic-12-atajos-favoritos-y-solucion-de-problemas)

<!-- soundsausage-contents:end -->

<a id="ss-topic-1-idioma-y-ayuda"></a>

## 1. Idioma y ayuda

En **Opciones → Idioma**, elige Nederlands, English, Deutsch, Français o Español. Los menús, ventanas, ayudas y el manual abierto cambian inmediatamente. La elección se conserva para el próximo inicio. Los nombres de archivos, pistas y complementos mantienen su escritura original.

**Ayuda → Manual** o **F1** abre este manual sin conexión junto al editor. **Ctrl+F** activa la búsqueda; **F3** busca la siguiente coincidencia y **Mayús+F3** la anterior, continuando desde el otro extremo. Solo los enlaces web abiertos expresamente necesitan internet. **Acerca de** muestra versión, autor, licencia, sitio web y componentes.

<a id="ss-topic-2-inicio-rapido-y-espacio-de-trabajo"></a>

## 2. Inicio rápido y espacio de trabajo

El icono del programa con fondo morado aparece en las barras de título y la barra de tareas. **Ayuda → Acerca de** muestra la mascota recortada junto a la información del programa.

Abre un WAV o MP3 con **Archivo → Abrir**. **Espacio** reproduce o detiene. Selecciona un fragmento, elige **Efectos → Amplitud → Normalizar**, escucha con **Escuchar** y confirma con **Aceptar**. **Ctrl+Z** deshace la edición. Usa **Guardar como** para guardar otro archivo. Para varias grabaciones, crea una **Nueva sesión multipista**, importa WAV o MP3 y termina con **Mezclar**.

**Editar forma de onda** edita una grabación; **Vista multipista** combina clips. Cambia con **Tab**, los botones superiores o **Ver**; ambos documentos siguen disponibles. Las ayudas explican los botones. **Mostrar etiquetas de herramientas** añade texto y **Opciones → Mostrar barra de estado** muestra u oculta la fina línea de información situada abajo del todo, debajo del medidor de nivel. Indica el estado de reproducción y los datos del archivo; la elección se conserva para el próximo inicio. **F11** alterna pantalla completa. El reloj sigue el audio; los campos de selección muestran inicio, fin y duración, y los de vista el intervalo visible. Los picos rojos indican sobrecarga y un asterisco cambios sin guardar.

Las ventanas y las escalas de los gráficos se adaptan al tamaño de letra del escritorio y al idioma elegido. Si un formulario no cabe en la pantalla, desplázate por sus ajustes; los botones para confirmar o cancelar siguen accesibles.

Dos finas líneas horizontales marcan el borde inferior del canal izquierdo y el superior del derecho. Terminan en los límites del gráfico, también durante la grabación en directo.

<a id="ss-topic-3-archivos-proyectos-y-recuperacion"></a>

## 3. Archivos, proyectos y recuperación

**Nuevo** crea una forma de onda mono o estéreo con el muestreo elegido. **Abrir** lee WAV y MP3. **Guardar** actualiza el archivo; **Guardar como** elige nombre y codificación; **Guardar selección** guarda solo el tiempo y los canales seleccionados. WAV permite PCM de 8/16/24/32 bits y float32. PCM16 facilita el intercambio; float32 conserva también picos internos superiores a 0 dBFS. Más bits no recuperan detalles perdidos. Los WAV antiguos ambiguos de 32 bits preguntan si son PCM o flotante antiguo; cancelar no cambia el archivo.

Se conservan textos WAV, marcadores y etiquetas. Los marcadores siguen las ediciones, pegados y exportaciones de selección; se mantiene el título de destino. Los campos específicos de grabadoras se conservan literalmente y no se recalculan después de efectos. Los metadatos adicionales tienen un límite de 16 MiB: se rechaza una entrada mayor y se confirman las omisiones al exportar. La mezcla no reúne todos los marcadores de origen. Los WAV grandes usan RF64 cuando hace falta.

**Nueva sesión multipista**, **Abrir sesión**, **Guardar sesión** y **Guardar sesión como** gestionan proyectos editables. Un proyecto SoundSausage (`.celp`) contiene audio, clips, curvas, ajustes de pistas, orden/omisión/colas de efectos y ajustes VST3. Guarda el proyecto además del WAV final para conservar las pistas separadas. Los proyectos SoundSausage anteriores siguen siendo legibles; los proyectos nuevos guardados requieren la aplicación 0.19.0 o posterior. La importación antigua `.ses` es limitada; continúa en un proyecto SoundSausage nuevo.

**Cerrar / Ctrl+W** cierra la forma de onda actual; en multipista se llama **Cerrar sesión**. Elige guardar, descartar o cancelar. La otra vista y el portapapeles siguen disponibles. **Salir / Ctrl+Q** cierra la aplicación y comprueba los cambios sin guardar.

Los archivos largos se procesan por bloques en disco, sin el antiguo límite de 128 MiB. Reserva espacio para copias de origen, resultados y deshacer. Las sesiones se limitan a 24 horas y 32 pistas. Las operaciones largas muestran progreso y cancelación; cancelar conserva audio, selección, historial y el archivo de exportación anterior. Cada efecto aplicado es un paso de deshacer.

Tras un cierre inesperado, recupera, elimina o pospón el último punto guardado. **Archivo → Recuperar trabajo** abre las copias conservadas. Los originales permanecen intactos; vuelven forma de onda, sesión, canales, clips, curvas y cadenas, pero el historial de deshacer se reinicia. Se guardan las ediciones confirmadas y, aproximadamente cada segundo, cursor y selección. Se omiten las instancias activas. Guardar o cerrar normalmente limpia la copia propia. Mantén tus copias de seguridad; un error de disco puede dejar un punto anterior.

<a id="ss-topic-mp3-y-wav"></a>

### MP3 y WAV

Abre MP3 con **Archivo → Abrir**, impórtalos a multipista o arrástralos a la línea de tiempo. La selección, edición y efectos trabajan con el audio decodificado. **Guardar como**, **Guardar selección** y **Mezclar** ofrecen WAV y MP3; la extensión sigue el formato elegido. Guardar un MP3 existente usa la codificación MP3 elegida; Guardar como permite crear una copia WAV.

MP3 ofrece 128, 192, 256 y 320 kb/s. Una tasa mayor ocupa más espacio y suele conservar más detalle. MP3 tiene pérdida: recomprimir puede perder más detalle. WAV evita otra compresión MP3, pero no recupera información perdida. Usa WAV float32 para seguir editando o PCM16 para intercambiar archivos. MP3 utiliza la frecuencia más cercana entre 32.000, 44.100 y 48.000 Hz y mantiene la duración; el documento conserva su frecuencia. Estas frecuencias admiten las cuatro tasas de bits MP3 ofrecidas; a frecuencias más bajas, el codificador puede usar una tasa de bits inferior a la solicitada. El mínimo de 2 ms evita que los fragmentos muy cortos se alarguen al decodificar el MP3. Usa WAV para selecciones de menos de 2 ms.

<a id="ss-topic-metadatos-mp3-despues-de-editar"></a>

### Metadatos MP3 después de editar

Se conservan título, artista, álbum, comentarios y portadas, también mediante WAV y proyectos SoundSausage. La duración se actualiza. Las etiquetas normales y los identificadores existentes permanecen en el archivo de destino.

Los **capítulos** siguen las ediciones automáticamente. Borrar adelanta los capítulos posteriores; insertar los retrasa. Recortar y exportar una selección conserva los capítulos que se solapan, con tiempos relativos al fragmento guardado. Los capítulos vacíos o eliminados por completo desaparecen y el índice conserva referencias válidas. Pegar incorpora los nombres y la jerarquía de los capítulos del fragmento y mantiene las etiquetas generales del destino. Estirar el tiempo adapta sus límites; cambiar la frecuencia de muestreo conserva los tiempos en milisegundos. Deshacer restaura también los metadatos originales.

La precisión es de un milisegundo; los restos que se redondean a duración cero desaparecen. Invertir refleja los capítulos enteramente dentro del intervalo. Un capítulo parcialmente invertido que describiría partes de audio separadas se elimina; los capítulos que contienen todo el intervalo invertido permanecen.

Las **mediciones** pueden quedar desactualizadas tras editar audio. Se eliminan los valores reconocidos de ReplayGain, R128, MP3Gain y picos, huellas, ajustes de volumen relativo y datos del codificador anterior. También desaparecen datos temporales incompatibles, como letras sincronizadas, índices de búsqueda antiguos y posiciones de sincronización. ReplayGain no se vuelve a calcular. Cambiar el tempo elimina el valor BPM existente; cambiar el tono elimina la tonalidad existente. Otras ediciones conservan ambos valores. Las letras normales sin tiempos y los campos privados desconocidos se conservan literalmente. Volver a codificar MP3 también elimina mediciones y posiciones antiguas, pues la compresión cambia el sonido y la estructura. Los datos del codificador proceden del nuevo archivo real.

**WAV a MP3:** se transfieren los campos INFO compatibles de título, artista, álbum, género, fecha, número de pista, derechos de autor y comentarios. Las etiquetas ID3 existentes tienen prioridad. Se avisa antes de exportar de campos incompatibles, INFO mal formado y valores en conflicto. **No** cancela y conserva un destino existente; **Sí** continúa con las omisiones indicadas. Las etiquetas ID3 adicionales de un WAV también se indican antes de omitirlas. La información del software anterior se sustituye por la del nuevo codificador. Los marcadores WAV y otros datos incompatibles requieren también esta elección.

Los metadatos adicionales siguen limitados a 16 MiB. Los ID3 WAV ilegibles se conservan sin interpretar; exportar MP3 informa de un error y mantiene el destino. La mezcla no reúne los metadatos de todas las pistas. Las conversiones largas muestran progreso y se pueden cancelar; reserva espacio para convertir y editar.


<a id="ss-topic-4-reproduccion-zoom-y-dispositivos"></a>

## 4. Reproducción, zoom y dispositivos

**Espacio** reproduce/detiene, **P** pausa/reanuda y **Esc** detiene. Se reproduce la selección o, sin ella, desde el cursor. **Bucle** repite ese intervalo, con una posible transición breve. **Inicio/Fin** van a los extremos; los botones saltan cinco segundos. Navegar o aplicar una edición detiene la reproducción. **Acercar / Alejar**, **Ctrl+rueda**, rueda y barra horizontal recorren la vista. **Vista completa / Ctrl+0** muestra todo; **Ampliar selección / Ctrl+Mayús+A** encuadra la selección. Sus iconos son distintos. De cerca se unen las muestras; de lejos se conservan mínimos y máximos por columna.

En **Opciones → Dispositivos de audio**, elige una salida o **Predeterminado del sistema**; se recuerda y sirve también para las vistas previas. El búfer predeterminado es de 100 ms: mayor tolera interrupciones y menor responde más rápido. El búfer real puede variar. Cambiarlo detiene reproducción y vistas previas. Si desaparece el dispositivo, reconecta o elige otra salida y reinicia. Comprueba volumen, ruta, silencio y solo. La conversión para la salida no cambia la grabación.

<a id="ss-topic-5-grabar"></a>

## 5. Grabar

Conecta un micrófono/interfaz, elige la entrada en **Dispositivos de audio** y pulsa **R**. Ajusta entrada, destino, mono/estéreo, primer canal y duración máxima. Una forma nueva graba aparte; insertar en cursor/reemplazar selección modifica una existente; multipista añade un clip en la pista elegida desde el cursor. Una entrada mono puede alimentar ambos canales estéreo. Una forma existente determina muestreo/canales; otro muestreo de entrada se convierte tras detener. **Hasta detener** continúa hasta detener o agotar el disco.

**Iniciar grabación** abre el micrófono; antes permanece cerrado. La forma en vivo muestra los últimos 20 segundos, el reloj la duración total y los medidores la entrada. **P** pausa/reanuda sin incluir el tiempo pausado. **Detener**, **Esc**, **Espacio** o **R** conserva la toma. Insertar/reemplazar o añadir un clip es un paso de deshacer; una forma nueva aún necesita guardarse. **Descartar grabación** pide confirmar para eliminar solo esta toma. Cerrar pregunta si conservar, descartar o continuar. Las demás ediciones quedan bloqueadas durante la grabación.

La entrada no se monitoriza por los altavoces. Ajusta la ganancia en la interfaz/micrófono o Linux; bajar después no repara una entrada saturada. Perder el dispositivo detiene y conserva el audio en lugar de cambiar de micrófono. Las tomas se escriben por bloques y se guardan aproximadamente cada segundo. Recuperar abre una forma aparte. Cancelar la conversión tras detener deja la toma en **Recuperar trabajo** y conserva el documento anterior.

**Omitir al inicio** elimina una vez los primeros milisegundos de cada toma para excluir un clic de arranque. El valor inicial es 50 ms, ajustable de 0 a 500 ms y recordado. Con 0 ms se conserva todo el inicio; después de una omisión se aplica una entrada gradual de 5 ms. El audio omitido no se graba. Reloj, vista, niveles y duración máxima siguen el audio conservado. Pausar/reanudar no repite la omisión. Con acompañamiento, la posición del clip tiene en cuenta el tiempo omitido para mantener la sincronización.

<a id="ss-topic-6-seleccion-canales-y-edicion"></a>

## 6. Selección, canales y edición

Pulsa para situar el cursor y arrastra para seleccionar. En estéreo, arrastra dentro de L o R para un canal o por ambos para estéreo. **Canales** o **Editar → Seleccionar canales** cambia canales conservando el intervalo: **Alt+B / Alt+L / Alt+R** eligen ambos/izquierda/derecha. Mayús+clic extiende conservando canales; doble clic selecciona el audio visible del canal pulsado; **Ctrl+A** toma toda la duración de esos canales. Mono tiene uno. **Definir selección** introduce tramas exactas; 44 100 tramas a 44 100 Hz son un segundo. **F4** mueve los bordes hacia dentro hasta cruces por cero (izquierdo si son ambos).

**Cortar / Ctrl+X** elimina y copia; **Copiar / Ctrl+C** copia; **Pegar / Ctrl+V** reemplaza la selección o inserta en el cursor. **Pegar mezclando / Ctrl+M** suma el audio del portapapeles y puede elevar los picos. **Supr** elimina el intervalo; **Recortar / Ctrl+T** conserva solo ese intervalo. **Ctrl+Z / Ctrl+Mayús+Z** deshace/rehace. Pegar convierte el muestreo sin cambiar el portapapeles. Con ambos canales debe coincidir su número. Copiar/exportar izquierda o derecha produce mono; guardar normalmente conserva toda la forma estéreo.

El estéreo conserva una línea temporal común. Con **Izquierda** o **Derecha**, cortar/eliminar, insertar, pegar con distinta duración, estirar, generar tonos/silencio y añadir colas desplaza solo el canal elegido. El otro conserva sus muestras en sus posiciones originales. El canal más corto se completa con silencio al final. **Ambos** desplaza los dos canales y sus marcadores comunes; **Efectos → Silencio** vacía sin desplazar.

Ejemplo: eliminar los segundos 2–3 de Izquierda adelanta un segundo el audio izquierdo posterior y añade un segundo de silencio final; Derecha permanece. **Recortar** coloca solo el fragmento seleccionado del canal elegido en el instante cero y completa el resto con silencio. El relleno es audio normal: se conserva al guardar/reabrir y se desplaza con inserciones posteriores. Elimina el silencio final sobrante con Ambos. Los marcadores y capítulos MP3 comunes mantienen sus tiempos al editar un canal; comprueba su significado después de desplazar audio.

Un portapapeles mono puede reemplazar intervalos más cortos o largos, o insertarse en el cursor. Uno estéreo aporta el canal izquierdo/derecho correspondiente. Se convierte el muestreo si hace falta. Los marcadores/capítulos del portapapeles solo se fusionan con Ambos; pegar en un canal conserva los marcadores comunes del destino. **Pegado mezclado** suma desde el inicio de selección/cursor sin desplazar audio posterior y puede superar el final; el otro canal recibe silencio final.

Para grabar en un canal, elige Izquierda/Derecha, **R**, y **Insertar en cursor** o **Reemplazar selección**. Se captura mono al muestreo de la forma. **Primer canal de entrada** elige la entrada física independientemente del destino izquierdo/derecho. Detener aplica una edición, desplaza solo ese canal y completa si hace falta. Nueva forma de onda sigue disponible. La elección queda bloqueada al grabar; un fallo/cancelación del procesamiento final conserva la toma en Recuperar trabajo. Deshacer/Rehacer restaura audio, relleno, metadatos y canales; recuperar conserva el audio estéreo editado.

<a id="ss-topic-editar-muestras-individuales"></a>

### Editar muestras individuales

Amplíe con **+** o **Ctrl+rueda** hasta ver los puntos cuadrados (al menos dos píxeles lógicos entre muestras). El eje horizontal muestra índices desde 0. Arrastre un punto verticalmente para cambiar solo esa muestra de ese canal. Su posición queda fija aunque el puntero cruce otros puntos o canales. El arrastre muestra una vista previa; soltar confirma y **Escape** cancela. **Mayús+arrastrar** sigue seleccionando audio.

Un doble clic o clic derecho abre **Editar muestra**. **Editar → Editar muestra** funciona con cualquier ampliación. Empieza en el cursor y el primer canal elegido; el índice y canal se pueden cambiar. Introduzca un valor normalizado o muéstrelo como 8, 16 o 24 bits con signo. Cero es silencio; −1/+1 son el nivel máximo normal. Por ejemplo, −16384 en la vista de 16 bits equivale a −0,5 normalizado. Cambiar el rango mostrado no modifica audio ni formato. **Aceptar** aplica un valor; **Cancelar** conserva el original.

Cada arrastre terminado o valor confirmado forma un paso Deshacer/Rehacer. Las demás muestras, el otro canal, la duración y los metadatos se conservan. Arrastrar está limitado a −1 … +1; los picos flotantes existentes siguen disponibles numéricamente. La reproducción se detiene al empezar una corrección; la edición queda bloqueada al grabar. Para clips multipista, edite una copia de forma de onda y aplíquela expresamente al clip. Escuche tras cada corrección; para un clic de varias muestras, acerque cada punto a la onda contigua. Un salto brusco a cero puede crear otro clic. WAV float32 conserva los valores internos exactos; guardar como MP3 recomprime todo el archivo con pérdidas.

<a id="ss-topic-dibujar-forma-de-onda"></a>

### Dibujar forma de onda

Activa **Editar → Dibujar forma de onda**, pulsa **D** o usa el lápiz junto a los controles de zoom. Dibuja directamente sobre la forma de onda con el botón izquierdo; no hace falta acertar en un punto individual. La línea dibujada sustituye los valores entre −1 y +1; no desplaza verticalmente la forma de onda original.

El zoom determina el tamaño del grupo: aproximadamente dos píxeles lógicos de audio, redondeados hacia arriba a muestras enteras. De cerca cambia una muestra; al alejar el zoom cambian varias juntas. Cada grupo abarca como máximo un segundo. Un gesto largo puede tocar varios grupos y cambiar más de un segundo en total. Líneas rectas unen las posiciones sucesivas del puntero; volver a dibujar sobre un grupo sustituye su dibujo anterior.

El canal inicial queda fijo aunque el puntero cruce el otro canal. Las demás muestras, el otro canal, la duración y los metadatos se conservan. Los grupos sombreados y la línea nueva muestran la vista previa. Al soltar se confirma todo el gesto en un solo paso de deshacer. **Escape**, perder el foco, cambiar el zoom o desactivar el dibujo cancelan la vista previa. **Mayús+arrastrar** sigue seleccionando audio; pulsa otra vez **D** para volver al funcionamiento normal. Dibujar está bloqueado durante la grabación. Acerca el zoom para reparaciones precisas: al dibujar de lejos también se sustituyen los detalles finos de cada grupo tocado. Escucha después y usa **Ctrl+Z** si hace falta. En multipista, edita una copia de la forma de onda y aplícala al clip.

<a id="ss-topic-7-aplicar-efectos"></a>

## 7. Aplicar efectos

Los efectos de forma de onda de **Efectos** tratan el intervalo y canales elegidos, o toda su duración sin selección temporal. El otro canal queda intacto y se oye en la vista previa estéreo. **Escuchar** reproduce hasta los ocho primeros segundos sin aplicar; vuelve a pulsar, cambia un ajuste o cierra para detener. **Aceptar** aplica un paso de deshacer; **Cancelar** conserva el original. **F2 / Repetir última orden** repite ajustes en la selección/canales actuales. Normalización, tiempo/tono y distorsión de alta calidad analizan toda la selección antes de la vista previa.

<a id="ss-topic-amplitud"></a>

### Amplitud

<a id="ss-topic-amplificar-fundido"></a>

#### Amplificar / fundido

**Amplificar / fundido** ajusta amplificación inicial/final: 100 % sin cambio, 50 % mitad, 200 % doble amplitud. Bloquear izquierda/derecha enlaza canales; igualar inicio/final da ganancia constante, desmarcar permite un fundido. El lineal llega a cero; el logarítmico requiere extremos positivos. Los preajustes incluyen ±6 dB y fundidos. **Fundido de entrada / Fundido de salida** aplican inmediatamente un fundido lineal. Ejemplo: selecciona la introducción, elige entrada gradual, escucha y confirma.

<a id="ss-topic-mezclador-de-canales"></a>

#### Mezclador de canales

**Mezclador de canales** requiere estéreo. Cada salida combina porcentajes de L/R; los negativos invierten la polaridad de entrada y la inversión de salida invierte la suma. Los preajustes intercambian, copian un lado a ambos, promedian a mono (siguen siendo dos canales) o restan. La mezcla puede superar 0 dBFS. Seleccionar un canal cambia solo su salida, aunque utilice ambos originales.

<a id="ss-topic-procesamiento-de-dinamica"></a>

#### Procesamiento de dinámica

**Procesamiento de dinámica** relaciona dB de entrada y salida. Bajo la diagonal atenúa y encima amplifica. Pulsa/arrastra puntos, introduce valores debajo; clic derecho, quitar punto o Supr elimina puntos interiores. Los extremos permanecen fijos. Ataque controla respuesta a picos, liberación la recuperación y ganancia de salida el resultado. Enlazar estéreo mantiene una regulación común. Para voz empieza con 3:1 sobre −18 dB. Compresor reduce partes fuertes, puerta/expansor las débiles y limitador los picos. No hay anticipación: un ataque lento deja pasar transitorios.

<a id="ss-topic-envolvente-de-volumen"></a>

#### Envolvente de volumen

**Envolvente de volumen** dibuja ganancia sobre el 0–100 % del fragmento, con amplitud del 0–200 % (100 % neutro). Arrastra o introduce posiciones/ganancias; elimina puntos interiores. Hay fundidos, fundido en ambos extremos y reducción central. La interpolación logarítmica necesita ganancias positivas. Para bajar una palabra, rodéala de puntos y dibuja una reducción. Esto escribe audio; las curvas de clips siguen editables aparte.

<a id="ss-topic-normalizar"></a>

#### Normalizar

**Normalizar** lleva el pico máximo al objetivo (98 % por defecto) con un factor único. No iguala palabras. Normalizar izquierda/derecha juntas conserva el balance; separarlas da un objetivo por canal. Quitar componente continua centra primero la señal; el silencio sigue igual. Úsalo tras mezclar para dejar margen PCM.

<a id="ss-topic-polaridad-sentido-y-silencio"></a>

#### Polaridad, sentido y silencio

**Invertir polaridad** invierte polaridad, **Invertir sentido** el tiempo y **Silencio** pone a cero sin quitar duración. Se aplican inmediatamente.

<a id="ss-topic-ecualizacion-y-filtros"></a>

### Ecualización y filtros

<a id="ss-topic-ecualizador-grafico"></a>

#### Ecualizador gráfico

En **Filtros**, **Ecualizador gráfico** tiene diez bandas de octava, 31,5 Hz–16 kHz, cada una −24…+24 dB. Se desactivan bandas inutilizables con muestreo bajo. Plano restablece; refuerzo de graves, presencia vocal y sonrisa suave ofrecen puntos de partida. El gráfico combina bandas y ganancia de salida (vista −36…+36 dB). Realzar puede superar 0 dBFS: baja la salida antes de exportar PCM.

<a id="ss-topic-ecualizador-parametrico"></a>

#### Ecualizador paramétrico

**Ecualizador paramétrico** ofrece cinco campanas y estantes grave/agudo activables por separado. Frecuencia elige centro/transición, ganancia −24…+24 dB y Q alto estrecha la campana. Los estantes tienen transiciones suaves fijas sin Q. Para resonancias usa una campana estrecha negativa; para tono general una ancha/estante con poca ganancia. Plano/restablecer pone ganancias a cero; claridad vocal/calidez son puntos de partida.

<a id="ss-topic-filtros"></a>

#### Filtros

**Filtros** ofrece paso alto (retumbo, inicio 80 Hz), paso bajo (suavizar agudos, 8 kHz), paso banda y rechazo. Paso alto/bajo usan Butterworth de 12/24/36/48 dB/oct, unos −3 dB en el corte; más pendiente puede resonar más. Banda/rechazo usan Q. Teléfono es una banda ancha; los rechazos de 50/60 Hz quitan solo la fundamental del zumbido. Restablecer carga retumbo. El estado continúa entre bloques pero empieza vacío en la selección; conserva duración y cambia fase. Una selección corta abrupta puede chasquear; amplíala.

<a id="ss-topic-retardo-eco-y-reverberacion"></a>

### Retardo, eco y reverberación

<a id="ss-topic-efectos-de-retardo-retardo"></a>

#### Efectos de retardo → Retardo

**Efectos de retardo → Retardo** añade una copia tras 1–2000 ms. Izquierda/mono controla el primer retardo; desenlaza para ajustar el derecho. Preajustes: simple 250 ms, slapback 80 ms, duplicación 25 ms y amplitud estéreo.

<a id="ss-topic-eco"></a>

#### Eco

**Eco** repite mediante realimentación (0–95 %); más valor alarga el decaimiento. La amortiguación de agudos oscurece repeticiones realimentadas, no la primera copia. Ping-pong alterna en estéreo. Eco cálido/repeticiones largas son inicios útiles; mucha realimentación puede acumular nivel.

<a id="ss-topic-reverberacion"></a>

#### Reverberación

**Reverberación** ajusta tamaño de sala (separación de reflexiones), decaimiento RT60 aproximado (0,1–10 s), retardo previo (0–250 ms) antes del efecto, amortiguación de agudos y anchura estéreo (0 efecto igual a ambos lados, 100 anchura completa; desactivada en mono). Sala pequeña, estudio, sala grande y ambiente largo varían espacio/decaimiento. Para voz empieza con poco efecto, decaimiento corto y algo de retardo previo. Es reverberación algorítmica, no un modelo exacto de sala.

Señal seca y efecto son porcentajes independientes sumados; ganancia de salida (−24…+24 dB) escala la suma sin limitar automáticamente. Por defecto se conserva duración y se cortan repeticiones tardías. Añadir cola inserta 0,01–60 s, desplazando audio posterior y marcadores. Los últimos 10 ms se desvanecen. Los preajustes desmarcan la cola: ajústala después. Un eco extremo puede superar 60 s; reduce realimentación/retardo. Ejemplo: voz de 2 s + cola de 3 s = 5 s. Una cola en un canal desplaza solo ese canal; los marcadores comunes permanecen.

<a id="ss-topic-reduccion-de-ruido-y-clics"></a>

### Reducción de ruido y clics

Selecciona solo ruido de fondo (normalmente de medio segundo a varios), elige **Capturar perfil de ruido**, selecciona el audio que quieres limpiar y vuelve a abrir **Reducción de ruido**. Capturar desde la ventana también funciona sin cambiar audio. El perfil promedia como máximo los primeros 30 s. La duración mínima depende del muestreo; muestreo/canales deben coincidir. Para un canal estéreo se usa el correspondiente del perfil. Guardar/cargar usa `.ssnoise`, un espectro sin grabación de audio. Reutilízalo solo en una configuración coincidente.

<a id="ss-topic-estimacion-del-ruido-perfil-de-ruido-fijo"></a>

#### Estimación del ruido → Perfil de ruido fijo

**Estimación del ruido → Perfil de ruido fijo** sirve para siseo o ventilación constantes. **Seguimiento adaptativo del ruido** parte del mismo perfil solo de ruido y sigue los cambios de nivel y espectro. Ambos modos necesitan un perfil compatible; uno silencioso no tiene efecto. El procesamiento no cambia el perfil guardado.

**Tiempo de seguimiento**, 0,05–5 segundos, solo se activa en adaptativo. Un tiempo corto reacciona antes, pero puede aprender sonidos sostenidos como ruido; uno largo es más prudente. Empieza en 0,15 s. **Protección de detalles**, 0–100 %, conserva más sonido suave y deja más fondo; valor inicial 50 %. Fijo con 0 % conserva la atenuación anterior. No recupera detalles ausentes de la fuente. Reducción máxima 0–36 dB (empieza con 6–12 dB; 0 conserva exactamente el original), sensibilidad controla qué se considera ruido y suavizado ralentiza una supresión mayor tras sonidos. Enlazar estéreo mantiene el balance; sin enlace los canales se procesan por separado.

Preajustes: **Suave** 6 dB/65 % de protección, **Equilibrado** 12 dB/50 %, **Intenso** 24 dB/15 %, **Fondo cambiante** adaptativo 12 dB/50 % a 0,15 s y **Detalles delicados** fijo 6 dB/90 %. Los tres primeros también son fijos. Para una voz con ventilador creciente, captura solo el ventilador, selecciona la voz y prueba Fondo cambiante. Sube la protección si desaparecen palabras suaves o colas. Aumenta el tiempo o usa Fijo para sonidos sostenidos. **Conservar solo ruido eliminado** permite oír lo quitado: desactívalo antes de confirmar audio limpio.

El seguimiento puede confundir sonido deseado con ruido, especialmente sonidos amplios sostenidos, niveles muy bajos o perfiles con voz/música. No separa voces ni recrea información perdida. Vista previa y procesamiento completo tienen el mismo principio. Duración, marcadores y canal estéreo no elegido permanecen. Deshacer restaura el original; F2 repite modo, tiempo, protección y perfil. Los archivos largos usan memoria de trabajo acotada; cancelar no aplica resultados parciales.

<a id="ss-topic-eliminacion-de-clics"></a>

#### Eliminación de clics

**Eliminación de clics** une muestras intactas alrededor de impulsos breves aislados. Un multiplicador de umbral alto es prudente; menor salto mínimo en dBFS detecta clics suaves. Anchura máxima 0,02–2 ms. Conservador, clics pequeños y anchos son inicios. Escucha con cuidado la percusión: sus ataques pueden parecer daños. Crujidos largos, saturación y muestras dañadas en extremos requieren otro tratamiento.

<a id="ss-topic-tiempo-y-tono"></a>

### Tiempo y tono

<a id="ss-topic-tiempo-tono-estirar-duracion"></a>

#### Tiempo/tono → Estirar duración

**Tiempo/tono → Estirar duración** cambia duración (25–400 %) conservando tono: 200 % duplica, 50 % reduce a la mitad. Los campos de tempo calculan BPM antiguo/nuevo (120→100 da 120 %), sin detección automática. Con Ambos, los marcadores siguen la escala y los posteriores se desplazan. Con Izquierda/Derecha solo se desplaza ese canal; los marcadores comunes permanecen.

<a id="ss-topic-cambio-de-tono"></a>

#### Cambio de tono

**Cambio de tono** varía −24…+24 semitonos sin cambiar duración/marcadores; ±12 es una octava y 0,01 semitono un cent. Preservar formantes ayuda a conservar la voz; compara ambos ajustes en instrumentos.

Fino (predeterminado) y Rápido usan Rubber Band sin tiempo real. El estéreo se procesa conjuntamente; los extremos pueden sonar artificiales. Para un cambio real usa al menos 50 ms y 64 muestras. El ajuste neutro devuelve exactamente el original; la salida se redondea a muestras. La vista previa analiza toda la selección antes de reproducir hasta ocho segundos; archivos largos requieren tiempo y memoria de análisis. Se puede cancelar. Para un clip, edita una copia y aplícala; las curvas escalan, los clips posteriores no se desplazan automáticamente.

<a id="ss-topic-efectos-especiales"></a>

### Efectos especiales

<a id="ss-topic-especial-distorsion"></a>

#### Especial → Distorsión

**Especial → Distorsión** ofrece recorte suave (saturación redondeada), duro (corte brusco), plegado de onda y reducción de bits (2–16). Ganancia de entrada 0–36 dB, techo 10–100 %, mezcla original/procesada, salida −24…+24 dB. El techo solo moldea la parte procesada, no la seca ni la salida total. Calidez suave, crunch, plegado y bits son inicios. Alta calidad sobremuestrea para reducir aliasing (normalmente 4×, adaptado con muestreo alto) y procesa toda la selección incluso para vista previa; estándar es más rápido/áspero. Duración/marcadores fijos y silencio conservado.

<a id="ss-topic-convolucion"></a>

#### Convolución

**Convolución** aplica una respuesta al impulso WAV de filtro, pantalla o espacio acústico. Elígela, ajusta seca/efecto y escucha. Mono funciona por canal; una respuesta estéreo exige entrada estéreo y usa el canal seleccionado correspondiente. Otro muestreo se convierte; respuesta limitada tras conversión a 10 segundos y 524 288 muestras, con archivo de hasta 32 MiB. Se rechazan respuestas vacías o silenciosas. La cola no añade otro fundido. Normalizar energía escala ambos canales juntos; desactívalo para respuestas calibradas. Seca 0 %, efecto 100 % da un filtro puro. Conservar cola completa añade duración de respuesta menos una muestra y desplaza lo posterior. Sin ello mantiene duración. Conserva el archivo intacto para F2; si cambia/falta, elígelo otra vez.

<a id="ss-topic-8-generar-analizar-y-convertir"></a>

## 8. Generar, analizar y convertir

**Generar → Tonos** inserta una senoide en el cursor o reemplaza la selección con duración, frecuencia Hz y amplitud % elegidas. Prueba 440 Hz a nivel moderado. **Generar → Silencio** inserta/reemplaza una duración de silencio; **Efectos → Silencio** conserva la duración existente.

**Analizar → Análisis de frecuencias / Alt+Z** muestra frecuencia frente a dBFS de canales/intervalo elegidos (o grabación entera). En intervalos largos usa una parte central limitada, ventana de Hann y potencia media de canales. Muestra frecuencia/nivel del pico debajo. Selecciona un sonido corto para estudiarlo; no es un espectrómetro continuo. Cerrar no cambia audio.

**Editar → Convertir frecuencia de muestreo** convierte toda la forma de onda a los Hz elegidos, conservando tono/duración con redondeo a tramas (al menos una). Cursor/selección siguen los mismos tiempos. Deshacer restaura audio y muestreo. Esto cambia el documento; la conversión automática de reproducción solo cambia la salida.

<a id="ss-topic-9-multipista-y-automatizacion"></a>

## 9. Multipista y automatización

Crea una sesión con muestreo/número de pistas e importa WAV por menú/botón o arrástralos desde el gestor. Se convierten muestreos y varios archivos ocupan pistas sucesivas. **Ventana → Insertar forma de onda actual en multipista** inserta la forma abierta. Añadir/quitar actúa sobre la pista elegida; deshacer restaura lo eliminado. Los nombres son editables. Silencio apaga y Solo limita a pistas solo; silencio tiene prioridad. Pan −100 izquierda, 0 centro, +100 derecha; en estéreo atenúa un lado sin copiar canales.

En **Mover clips**, arrastra el centro para mover y los bordes para recortar; se conserva el origen para alargar. El espacio vacío selecciona un intervalo de reproducción. **Duplicar clip / Ctrl+D** comparte origen; **Eliminar clip / Supr** quita el clip, no el archivo. Clic derecho abre comandos. **Propiedades del clip** ajusta nombre, límites temporales/origen (segundos), ganancia, pan, fundidos y silencio; los fundidos juntos deben caber. Cancelar no cambia nada.

**Curva de volumen** y **Curva panorámica** dibujan puntos en clips. Pulsa para añadir, arrastra para mover, clic derecho/doble clic abre tramas/valores exactos, quitar/Supr elimina el punto elegido y restablecer vuelve a neutro. Esc cancela el arrastre. Volumen: abajo 0 %, medio 100 %, arriba 200 %, multiplicando ganancias y fundidos. Pan: arriba derecha, medio neutro, abajo izquierda, sumándose a pan de clip/pista. Centra pan normal para un barrido completo. Los puntos siguen al origen al mover/recortar y se guardan. Vuelve a mover clips para desplazarlos.

Doble clic o **Editar copia en forma de onda** abre una copia para efectos sin tiempo real. **Ventana → Aplicar forma de onda al clip** devuelve expresamente el resultado; cambiar de vista no lo aplica. Deshacer en sesión restaura audio/curvas. Se reconvierte muestreo, las curvas siguen la duración y los clips posteriores quedan fijos: comprueba solapamientos. **Mezclar sesión / Mezclar** exporta toda la sesión sin depender de la selección, con silencio/solo, ganancias/pan, curvas, efectos y colas. Guardar sesión conserva el proyecto editable. Estos ajustes cambian durante reproducción; deshacer/cambiar vista la detiene.

<a id="ss-topic-10-efectos-de-pista-plug-ins-y-grabacion"></a>

## 10. Efectos de pista, plug-ins y grabación

Abra **FX** junto a la pista o **Efectos → Efectos de pista**. Añada un efecto, elija ajustes/preajuste y confirme con Aceptar; Aplicar cambia sin cerrar. Editar/doble clic reabre los ajustes. Subir/bajar cambia orden, la marca omite y Quitar elimina. Los cambios tienen Deshacer/Rehacer. Hasta dieciséis efectos actúan tras ganancia/curvas/fundidos del clip y antes de volumen/pan de pista. Mono pasa a estéreo. La cola tras el último clip añade 0–60 segundos. Reproducción y mezcla usan la misma cadena sin cambiar las fuentes.

Se ofrecen amplificación fija, mezclador, dinámica, EQ gráfico/paramétrico, filtros, retardo, eco, reverberación, inversión y plug-ins externos. Aplicar actualiza mientras escucha; el audio ya almacenado conserva los ajustes previos. Reiniciar, buscar y cambiar omisión vacían la memoria del efecto. Normalización, restauración, tiempo/tono, distorsión y convolución siguen siendo ediciones mediante Editar copia en forma de onda. Use la curva de volumen para variar la ganancia del clip.

<a id="ss-topic-vst3-lv2-y-ladspa"></a>

### VST3, LV2 y LADSPA

Instale un **efecto de audio nativo de Linux de 64 bits**. En Efectos de pista elija **Plug-in externo → Añadir**, formato y **Añadir plug-in**. Seleccione un paquete `.vst3`, `.lv2` o biblioteca LADSPA (`.so`). Los efectos del paquete aparecen por separado. Elija el efecto, busque parámetros y cambie su posición normalizada 0–100 %: 50 % no significa necesariamente medio volumen. Los discretos tienen pasos; los de solo lectura quedan fijos. Aplicar permite escuchar en la pista; Aceptar confirma/cierra.

**Abrir ventana del plug-in** abre un editor VST3/LV2 compatible. Sus parámetros y estado guardable se incluyen al confirmar. Las ventanas propias requieren **X11 o XWayland**. Los controles generales siguen disponibles si el editor falta o no es compatible; LADSPA siempre los utiliza. Los editores LV2 que requieren un adaptador GTK/Qt no se integran.

VST3 admite un bus estéreo de entrada/salida con float32. LV2/LADSPA admiten efectos mono/estéreo con igual número de entradas/salidas; los efectos mono usan una instancia por canal estéreo. Instrumentos MIDI, cadenas laterales adicionales, VST2 y plug-ins de Windows no están admitidos. Se indican funciones/puertos LV2 obligatorios no disponibles; no hay procesamiento MIDI/Atom. El estado LV2 que necesita archivos externos no puede guardarse completo y genera un mensaje: elija un efecto con estado autónomo.

Cada plug-in se ejecuta en un proceso aislado. Fallo, tiempo agotado o audio no válido detienen la reproducción conservando lo grabado. Los proyectos guardan parámetros y hasta 1 MiB de estado por efecto. Instale aparte el plug-in y sus bibliotecas/muestras externas. En otro equipo añada la misma versión. Las versiones ausentes/cambiadas se indican; reproducir/exportar requiere el efecto correspondiente o una omisión deliberada.

<a id="ss-topic-compensacion-del-retardo-de-plug-ins"></a>

### Compensación del retardo de plug-ins

El retardo algorítmico declarado se compensa por pista al reproducir y mezclar. Los retardos de la cadena se suman; cambios de ajustes/omisión actualizan el procesamiento. Posiciones y duración de mezcla no cambian. Eco musical, retardo previo y reverberación siguen audibles. La compensación depende de datos correctos del plug-in y admite hasta diez segundos por pista. Un retardo no válido o continuamente cambiante genera un mensaje.

<a id="ss-topic-acompanamiento-y-sincronizacion"></a>

### Acompañamiento y sincronización

Coloque acompañamiento en pistas, elija pista destino y cursor. Pulse **R**, elija entrada y destino nuevo clip y active **Reproducir pistas existentes al grabar**. Las pistas suenan con efectos; la entrada no se envía a altavoces. **P** pausa/reanuda ambos; **Detener/Esc/Espacio/R** conserva la toma como un paso de Deshacer. Descartar elimina solo esta toma. Un fallo de dispositivo/plug-in conserva el audio capturado.

**Sincronización automática** vincula posición al reloj de reproducción y mide la diferencia de relojes de entrada/salida. Una medición larga y fiable corrige suavemente la duración tras Detener. Una medición corta/inestable no estira la toma. Corregir la duración requiere más de diez segundos de mediciones de reloj utilizables. Esto no mide la ruta física de entrada/salida.

Para medirla, use **Opciones → Calibrar grabación** o el botón del diálogo de grabación. Elija los mismos dispositivos, frecuencia, modo mono/estéreo, primer canal y búfer que para grabar. Conecte salida y entrada con un cable de bucle adecuado. Un micrófono cerca de un altavoz incluye el retardo acústico. Empiece a bajo nivel. **Iniciar calibración** reproduce pulsos suaves durante unos seis segundos sin monitorizar la entrada. Solo se guardan resultados fiables; silencio, saturación, ambigüedad o inestabilidad conservan un perfil previo correcto. Compruebe con una toma corta; recalibre si cambia dispositivos/ajustes.

La sincronización automática aplica el perfil correspondiente. Sin perfil funciona la sincronización de reloj, pero puede quedar retardo físico. Como alternativa desactive el automatismo y use **Desplazamiento de posición de grabación**: negativo antes, positivo después; −15 ms corrige una toma que llega 15 ms tarde. La corrección manual y automática se excluyen.

<a id="ss-topic-punch-in-out"></a>

### Punch-in/out

Elija pista destino y un intervalo en la regla multipista o con **Editar → Establecer selección**. Use **Opciones → Punch-in/out** o **Mayús+R**. Configure entrada, sincronización, **Pregrabación** (2 s) y **Fundido cruzado** (5 ms). La selección fija los límites de grabación; el acompañamiento queda activado.

La entrada se prepara antes de reproducir. Durante la pregrabación suena el original. Dentro del intervalo se silencia solo la pista destino mientras se graba el reemplazo; las demás siguen sonando. Tras una breve finalización para sincronizar, se detiene automáticamente. Solo el audio corregido dentro de la selección se añade como nuevo clip.

Los fundidos mezclan antiguo/nuevo dentro de los límites, hasta 100 ms. El audio exterior queda intacto. Los clips originales conservan las fuentes y se cubre la región punch. Ctrl+Z restaura todo en un paso. En el clip antiguo use **Restaurar audio cubierto** para eliminar todas sus regiones cubiertas; borre/silencie la toma nueva para no oír ambas. Detener antes de tiempo conserva solo la parte capturada dentro del intervalo. Antes del intervalo no cambia la sesión; la toma bruta queda en **Archivo → Recuperar trabajo**. Recuperar una toma sin confirmar ofrece el audio bruto, con pregrabación/final, para colocarlo manualmente. Las regiones punch completadas se conservan en el proyecto y la recuperación tras fallo.

**Guardar sesión / Guardar sesión como** conserva audio, clips, curvas, cadenas, estado de plug-ins y regiones punch. Abrir sesión los restaura; la mezcla exporta WAV/MP3 con los mismos efectos. Conserve el proyecto para editar pistas separadas. Los proyectos nuevos guardados requieren SoundSausage **0.19.0 o posterior**; los anteriores siguen legibles. Los plug-ins ausentes no impiden abrir/recuperar las fuentes.

<a id="ss-topic-11-grabar-con-acompanamiento"></a>

## 11. Grabar con acompañamiento

Coloca acompañamiento en pistas, elige otra pista de destino y sitúa el cursor. Pulsa **R**, elige entrada/nuevo clip y activa «Reproducir pistas existentes al grabar». Pistas y efectos parten del cursor; la entrada no va a altavoces. **P** pausa/reanuda ambos; **Detener/Esc/Espacio/R** detiene y conserva la toma como un paso de deshacer. Puede seguir grabando tras terminar el acompañamiento; una duración máxima detiene ambos. Descartar quita solo la nueva toma. Un fallo conserva muestras capturadas. Las ediciones quedan bloqueadas.

El desplazamiento de posición mueve el clip insertado: negativo antes, positivo después. Si llega 15 ms tarde, prueba −15 ms. Graba un clic conocido por tu ruta real de entrada/salida, compara posiciones, introduce la diferencia y comprueba con otra toma. Recalibra tras cambiar dispositivo/búfer. El audio anterior a cero se recorta al insertar. Se recuerda el desplazamiento; calibración física automática, corrección de deriva, compensación de complementos y punch-in/out siguen en desarrollo. Prueba una toma corta antes de una sesión larga.

<a id="ss-topic-12-atajos-favoritos-y-solucion-de-problemas"></a>

## 12. Atajos, favoritos y solución de problemas

**Favoritos** ofrece repetición, normalización y fundidos; aún no hay listas personalizadas. **Ventana** cambia vistas y transfiere formas/clips. Estos son los atajos principales. Al escribir, las teclas pertenecen al campo; pulsa la forma/línea temporal antes de usar transporte/edición.

| Teclas | Acción |
| --- | --- |
| Ctrl+N / Ctrl+O | Nuevo / abrir en vista actual |
| Ctrl+S / Ctrl+Mayús+S | Guardar / como |
| Ctrl+Alt+N / Ctrl+Alt+O / Ctrl+Alt+S | Nueva / abrir / guardar sesión |
| Ctrl+W / Ctrl+Q | Cerrar documento / salir |
| Ctrl+Z / Ctrl+Mayús+Z | Deshacer / rehacer |
| Ctrl+X / Ctrl+C / Ctrl+V | Cortar / copiar / pegar |
| Ctrl+M / Ctrl+T / Supr | Pegar mezclando / recortar / eliminar |
| Ctrl+A / F4 | Toda la duración / cruces por cero |
| Alt+B / Alt+L / Alt+R | Ambos / izquierda / derecha |
| Espacio / P / Esc / R | Reproducir-detener / pausa / detener / grabar |
| Inicio / Fin / + / − | Inicio / fin / ampliar / reducir |
| Ctrl+0 / Ctrl+Mayús+A | Zoom completo / selección |
| Ctrl+D / Tab / F11 | Duplicar clip / vista / pantalla completa |
| F1 / F2 / Alt+Z | Manual / repetir efecto / análisis de frecuencias |

Sin entrada: revisa dispositivo/canal y nivel de micrófono Linux, reconecta y empieza otra toma. Sin salida: comprueba ruta, volumen, silencio/solo y dispositivos. Distorsión/picos rojos: baja ganancia sumada y normaliza antes de PCM; pegar mezclando y clips solapados suman. Pegado rechazado: revisa el número de canales del portapapeles. Efecto desactivado: abre forma/copia; el mezclador necesita estéreo; elige los canales que quieras editar. Puntos en lugar de clips: elige mover clips. Disco lleno: libera espacio sin borrar archivos de trabajo activos. Recuperación dañada: quedan originales; elimina copia solo si ya no hace falta.

En desarrollo: favoritos personalizados y editor de marcadores. Cadenas en tiempo real, Linux VST3 y acompañamiento están disponibles como se describe. Guarda antes de salir. Novedades: [SoundSausage](https://github.com/rene-timmermans/SoundSausage).
