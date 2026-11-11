# SoundSausage — manual

Versión 0.17.0. Un editor de audio intuitivo y fácil de usar, con todas las herramientas donde las esperas. Este manual describe las funciones disponibles, los efectos y sus límites prácticos.

## 1. Idioma y ayuda

En **Opciones → Idioma**, elige Nederlands, English, Deutsch, Français o Español. Los menús, ventanas, ayudas y el manual abierto cambian inmediatamente. La elección se conserva para el próximo inicio. Los nombres de archivos, pistas y complementos mantienen su escritura original.

**Ayuda → Manual** o **F1** abre este manual sin conexión junto al editor. **Ctrl+F** activa la búsqueda; **F3** busca la siguiente coincidencia y **Mayús+F3** la anterior, continuando desde el otro extremo. Solo los enlaces web abiertos expresamente necesitan internet. **Acerca de** muestra versión, autor, licencia, sitio web y componentes.

## 2. Inicio rápido y espacio de trabajo

Abre un WAV o MP3 con **Archivo → Abrir**. **Espacio** reproduce o detiene. Selecciona un fragmento, elige **Efectos → Amplitud → Normalizar**, escucha con **Escuchar** y confirma con **Aceptar**. **Ctrl+Z** deshace la edición. Usa **Guardar como** para guardar otro archivo. Para varias grabaciones, crea una **Nueva sesión multipista**, importa WAV o MP3 y termina con **Mezclar**.

**Editar forma de onda** edita una grabación; **Vista multipista** combina clips. Cambia con **Tab**, los botones superiores o **Ver**; ambos documentos siguen disponibles. Las ayudas explican los botones. **Mostrar etiquetas de herramientas** añade texto y **Opciones → Mostrar barra de estado** muestra u oculta la fina línea de información situada abajo del todo, debajo del medidor de nivel. Indica el estado de reproducción y los datos del archivo; la elección se conserva para el próximo inicio. **F11** alterna pantalla completa. El reloj sigue el audio; los campos de selección muestran inicio, fin y duración, y los de vista el intervalo visible. Los picos rojos indican sobrecarga y un asterisco cambios sin guardar.

Las ventanas y las escalas de los gráficos se adaptan al tamaño de letra del escritorio y al idioma elegido. Si un formulario no cabe en la pantalla, desplázate por sus ajustes; los botones para confirmar o cancelar siguen accesibles.

Una fina línea horizontal separa izquierda y derecha en la forma de onda estéreo y en la vista de grabación en directo.

## 3. Archivos, proyectos y recuperación

**Nuevo** crea una forma de onda mono o estéreo con el muestreo elegido. **Abrir** lee WAV y MP3. **Guardar** actualiza el archivo; **Guardar como** elige nombre y codificación; **Guardar selección** guarda solo el tiempo y los canales seleccionados. WAV permite PCM de 8/16/24/32 bits y float32. PCM16 facilita el intercambio; float32 conserva también picos internos superiores a 0 dBFS. Más bits no recuperan detalles perdidos. Los WAV antiguos ambiguos de 32 bits preguntan si son PCM o flotante antiguo; cancelar no cambia el archivo.

Se conservan textos WAV, marcadores y etiquetas. Los marcadores siguen las ediciones, pegados y exportaciones de selección; se mantiene el título de destino. Los campos específicos de grabadoras se conservan literalmente y no se recalculan después de efectos. Los metadatos adicionales tienen un límite de 16 MiB: se rechaza una entrada mayor y se confirman las omisiones al exportar. La mezcla no reúne todos los marcadores de origen. Los WAV grandes usan RF64 cuando hace falta.

**Nueva sesión multipista**, **Abrir sesión**, **Guardar sesión** y **Guardar sesión como** gestionan proyectos editables. Un proyecto SoundSausage (`.celp`) contiene audio, clips, curvas, ajustes de pistas, orden/omisión/colas de efectos y ajustes VST3. Guarda el proyecto además del WAV final para conservar las pistas separadas. Los proyectos SoundSausage anteriores siguen siendo legibles; las cadenas de efectos requieren la aplicación 0.15.0 o posterior. La importación antigua `.ses` es limitada; continúa en un proyecto SoundSausage nuevo.

**Cerrar / Ctrl+W** cierra la forma de onda actual; en multipista se llama **Cerrar sesión**. Elige guardar, descartar o cancelar. La otra vista y el portapapeles siguen disponibles. **Salir / Ctrl+Q** cierra la aplicación y comprueba los cambios sin guardar.

Los archivos largos se procesan por bloques en disco, sin el antiguo límite de 128 MiB. Reserva espacio para copias de origen, resultados y deshacer. Las sesiones se limitan a 24 horas y 32 pistas. Las operaciones largas muestran progreso y cancelación; cancelar conserva audio, selección, historial y el archivo de exportación anterior. Cada efecto aplicado es un paso de deshacer.

Tras un cierre inesperado, recupera, elimina o pospón el último punto guardado. **Archivo → Recuperar trabajo** abre las copias conservadas. Los originales permanecen intactos; vuelven forma de onda, sesión, canales, clips, curvas y cadenas, pero el historial de deshacer se reinicia. Se guardan las ediciones confirmadas y, aproximadamente cada segundo, cursor y selección. Se omiten las instancias activas. Guardar o cerrar normalmente limpia la copia propia. Mantén tus copias de seguridad; un error de disco puede dejar un punto anterior.

### MP3 y WAV

Abre MP3 con **Archivo → Abrir**, impórtalos a multipista o arrástralos a la línea de tiempo. La selección, edición y efectos trabajan con el audio decodificado. **Guardar como**, **Guardar selección** y **Mezclar** ofrecen WAV y MP3; la extensión sigue el formato elegido. Guardar un MP3 existente usa la codificación MP3 elegida; Guardar como permite crear una copia WAV.

MP3 ofrece 128, 192, 256 y 320 kb/s. Una tasa mayor ocupa más espacio y suele conservar más detalle. MP3 tiene pérdida: recomprimir puede perder más detalle. WAV evita otra compresión MP3, pero no recupera información perdida. Usa WAV float32 para seguir editando o PCM16 para intercambiar archivos. MP3 utiliza la frecuencia más cercana entre 32.000, 44.100 y 48.000 Hz y mantiene la duración; el documento conserva su frecuencia. Usa WAV para selecciones de menos de 2 ms.

Se conservan los textos ID3 y las portadas integradas, también al pasar por WAV y proyectos integrados. Se actualiza la duración; las posiciones de capítulos, ReplayGain y otros datos derivados no se recalculan. Los marcadores/datos WAV incompatibles requieren confirmación antes de exportar a MP3. Los metadatos adicionales siguen limitados a 16 MiB; la mezcla no reúne todos los metadatos de las pistas. Las conversiones largas muestran progreso y se pueden cancelar sin reemplazar el destino existente. Reserva espacio para la conversión y la edición.

## 4. Reproducción, zoom y dispositivos

**Espacio** reproduce/detiene, **P** pausa/reanuda y **Esc** detiene. Se reproduce la selección o, sin ella, desde el cursor. **Bucle** repite ese intervalo, con una posible transición breve. **Inicio/Fin** van a los extremos; los botones saltan cinco segundos. Navegar o aplicar una edición detiene la reproducción. **Acercar / Alejar**, **Ctrl+rueda**, rueda y barra horizontal recorren la vista. **Vista completa / Ctrl+0** muestra todo; **Ampliar selección / Ctrl+Mayús+A** encuadra la selección. Sus iconos son distintos. De cerca se unen las muestras; de lejos se conservan mínimos y máximos por columna.

En **Opciones → Dispositivos de audio**, elige una salida o **Predeterminado del sistema**; se recuerda y sirve también para las vistas previas. El búfer predeterminado es de 100 ms: mayor tolera interrupciones y menor responde más rápido. El búfer real puede variar. Cambiarlo detiene reproducción y vistas previas. Si desaparece el dispositivo, reconecta o elige otra salida y reinicia. Comprueba volumen, ruta, silencio y solo. La conversión para la salida no cambia la grabación.

## 5. Grabar

Conecta un micrófono/interfaz, elige la entrada en **Dispositivos de audio** y pulsa **R**. Ajusta entrada, destino, mono/estéreo, primer canal y duración máxima. Una forma nueva graba aparte; insertar en cursor/reemplazar selección modifica una existente; multipista añade un clip en la pista elegida desde el cursor. Una entrada mono puede alimentar ambos canales estéreo. Una forma existente determina muestreo/canales; otro muestreo de entrada se convierte tras detener. **Hasta detener** continúa hasta detener o agotar el disco.

**Iniciar grabación** abre el micrófono; antes permanece cerrado. La forma en vivo muestra los últimos 20 segundos, el reloj la duración total y los medidores la entrada. **P** pausa/reanuda sin incluir el tiempo pausado. **Detener**, **Esc**, **Espacio** o **R** conserva la toma. Insertar/reemplazar o añadir un clip es un paso de deshacer; una forma nueva aún necesita guardarse. **Descartar grabación** pide confirmar para eliminar solo esta toma. Cerrar pregunta si conservar, descartar o continuar. Las demás ediciones quedan bloqueadas durante la grabación.

La entrada no se monitoriza por los altavoces. Ajusta la ganancia en la interfaz/micrófono o Linux; bajar después no repara una entrada saturada. Perder el dispositivo detiene y conserva el audio en lugar de cambiar de micrófono. Las tomas se escriben por bloques y se guardan aproximadamente cada segundo. Recuperar abre una forma aparte. Cancelar la conversión tras detener deja la toma en **Recuperar trabajo** y conserva el documento anterior.

**Omitir al inicio** elimina una vez los primeros milisegundos de cada toma para excluir un clic de arranque. El valor inicial es 50 ms, ajustable de 0 a 500 ms y recordado. Con 0 ms se conserva todo el inicio; después de una omisión se aplica una entrada gradual de 5 ms. El audio omitido no se graba. Reloj, vista, niveles y duración máxima siguen el audio conservado. Pausar/reanudar no repite la omisión. Con acompañamiento, la posición del clip tiene en cuenta el tiempo omitido para mantener la sincronización.

## 6. Selección, canales y edición

Pulsa para situar el cursor y arrastra para seleccionar. En estéreo, arrastra dentro de L o R para un canal o por ambos para estéreo. **Canales** o **Editar → Seleccionar canales** cambia canales conservando el intervalo: **Alt+B / Alt+L / Alt+R** eligen ambos/izquierda/derecha. Mayús+clic extiende conservando canales; doble clic selecciona el audio visible del canal pulsado; **Ctrl+A** toma toda la duración de esos canales. Mono tiene uno. **Definir selección** introduce tramas exactas; 44 100 tramas a 44 100 Hz son un segundo. **F4** mueve los bordes hacia dentro hasta cruces por cero (izquierdo si son ambos).

**Cortar / Ctrl+X** elimina y copia; **Copiar / Ctrl+C** copia; **Pegar / Ctrl+V** reemplaza la selección o inserta en el cursor. **Pegar mezclando / Ctrl+M** suma el audio del portapapeles y puede elevar los picos. **Supr** elimina el intervalo; **Recortar / Ctrl+T** conserva solo ese intervalo. **Ctrl+Z / Ctrl+Mayús+Z** deshace/rehace. Pegar convierte el muestreo sin cambiar el portapapeles. Con ambos canales debe coincidir su número. Copiar/exportar izquierda o derecha produce mono; guardar normalmente conserva toda la forma estéreo.

El estéreo comparte una línea temporal: cortar/eliminar/recortar, estirar, insertar o añadir colas requiere ambos canales. Pegar mono en un canal estéreo debe reemplazar exactamente ese intervalo; la mezcla pegada debe quedar dentro de la duración existente. **Silencio** vacía un canal sin desplazar el otro. Cambio de tono, retardo, eco, reverberación y convolución pueden tratar un canal conservando duración. Grabar en una forma estéreo existente también requiere ambos. Deshacer y recuperar conservan la elección de canales.

## 7. Aplicar efectos

Los efectos de forma de onda de **Efectos** tratan el intervalo y canales elegidos, o toda su duración sin selección temporal. El otro canal queda intacto y se oye en la vista previa estéreo. **Escuchar** reproduce hasta los ocho primeros segundos sin aplicar; vuelve a pulsar, cambia un ajuste o cierra para detener. **Aceptar** aplica un paso de deshacer; **Cancelar** conserva el original. **F2 / Repetir última orden** repite ajustes en la selección/canales actuales. Normalización, tiempo/tono y distorsión de alta calidad analizan toda la selección antes de la vista previa.

### Amplitud

**Amplificar / fundido** ajusta amplificación inicial/final: 100 % sin cambio, 50 % mitad, 200 % doble amplitud. Bloquear izquierda/derecha enlaza canales; igualar inicio/final da ganancia constante, desmarcar permite un fundido. El lineal llega a cero; el logarítmico requiere extremos positivos. Los preajustes incluyen ±6 dB y fundidos. **Fundido de entrada / Fundido de salida** aplican inmediatamente un fundido lineal. Ejemplo: selecciona la introducción, elige entrada gradual, escucha y confirma.

**Mezclador de canales** requiere estéreo. Cada salida combina porcentajes de L/R; los negativos invierten la polaridad de entrada y la inversión de salida invierte la suma. Los preajustes intercambian, copian un lado a ambos, promedian a mono (siguen siendo dos canales) o restan. La mezcla puede superar 0 dBFS. Seleccionar un canal cambia solo su salida, aunque utilice ambos originales.

**Procesamiento de dinámica** relaciona dB de entrada y salida. Bajo la diagonal atenúa y encima amplifica. Pulsa/arrastra puntos, introduce valores debajo; clic derecho, quitar punto o Supr elimina puntos interiores. Los extremos permanecen fijos. Ataque controla respuesta a picos, liberación la recuperación y ganancia de salida el resultado. Enlazar estéreo mantiene una regulación común. Para voz empieza con 3:1 sobre −18 dB. Compresor reduce partes fuertes, puerta/expansor las débiles y limitador los picos. No hay anticipación: un ataque lento deja pasar transitorios.

**Envolvente de volumen** dibuja ganancia sobre el 0–100 % del fragmento, con amplitud del 0–200 % (100 % neutro). Arrastra o introduce posiciones/ganancias; elimina puntos interiores. Hay fundidos, fundido en ambos extremos y reducción central. La interpolación logarítmica necesita ganancias positivas. Para bajar una palabra, rodéala de puntos y dibuja una reducción. Esto escribe audio; las curvas de clips siguen editables aparte.

**Normalizar** lleva el pico máximo al objetivo (98 % por defecto) con un factor único. No iguala palabras. Normalizar izquierda/derecha juntas conserva el balance; separarlas da un objetivo por canal. Quitar componente continua centra primero la señal; el silencio sigue igual. Úsalo tras mezclar para dejar margen PCM. **Invertir polaridad** invierte polaridad, **Invertir sentido** el tiempo y **Silencio** pone a cero sin quitar duración. Se aplican inmediatamente.

### Ecualización y filtros

En **Filtros**, **Ecualizador gráfico** tiene diez bandas de octava, 31,5 Hz–16 kHz, cada una −24…+24 dB. Se desactivan bandas inutilizables con muestreo bajo. Plano restablece; refuerzo de graves, presencia vocal y sonrisa suave ofrecen puntos de partida. El gráfico combina bandas y ganancia de salida (vista −36…+36 dB). Realzar puede superar 0 dBFS: baja la salida antes de exportar PCM.

**Ecualizador paramétrico** ofrece cinco campanas y estantes grave/agudo activables por separado. Frecuencia elige centro/transición, ganancia −24…+24 dB y Q alto estrecha la campana. Los estantes tienen transiciones suaves fijas sin Q. Para resonancias usa una campana estrecha negativa; para tono general una ancha/estante con poca ganancia. Plano/restablecer pone ganancias a cero; claridad vocal/calidez son puntos de partida.

**Filtros** ofrece paso alto (retumbo, inicio 80 Hz), paso bajo (suavizar agudos, 8 kHz), paso banda y rechazo. Paso alto/bajo usan Butterworth de 12/24/36/48 dB/oct, unos −3 dB en el corte; más pendiente puede resonar más. Banda/rechazo usan Q. Teléfono es una banda ancha; los rechazos de 50/60 Hz quitan solo la fundamental del zumbido. Restablecer carga retumbo. El estado continúa entre bloques pero empieza vacío en la selección; conserva duración y cambia fase. Una selección corta abrupta puede chasquear; amplíala.

### Retardo, eco y reverberación

**Efectos de retardo → Retardo** añade una copia tras 1–2000 ms. Izquierda/mono controla el primer retardo; desenlaza para ajustar el derecho. Preajustes: simple 250 ms, slapback 80 ms, duplicación 25 ms y amplitud estéreo. **Eco** repite mediante realimentación (0–95 %); más valor alarga el decaimiento. La amortiguación de agudos oscurece repeticiones realimentadas, no la primera copia. Ping-pong alterna en estéreo. Eco cálido/repeticiones largas son inicios útiles; mucha realimentación puede acumular nivel.

**Reverberación** ajusta tamaño de sala (separación de reflexiones), decaimiento RT60 aproximado (0,1–10 s), retardo previo (0–250 ms) antes del efecto, amortiguación de agudos y anchura estéreo (0 efecto igual a ambos lados, 100 anchura completa; desactivada en mono). Sala pequeña, estudio, sala grande y ambiente largo varían espacio/decaimiento. Para voz empieza con poco efecto, decaimiento corto y algo de retardo previo. Es reverberación algorítmica, no un modelo exacto de sala.

Señal seca y efecto son porcentajes independientes sumados; ganancia de salida (−24…+24 dB) escala la suma sin limitar automáticamente. Por defecto se conserva duración y se cortan repeticiones tardías. Añadir cola inserta 0,01–60 s, desplazando audio posterior y marcadores. Los últimos 10 ms se desvanecen. Los preajustes desmarcan la cola: ajústala después. Un eco extremo puede superar 60 s; reduce realimentación/retardo. Ejemplo: voz de 2 s + cola de 3 s = 5 s. Un canal estéreo solo no puede añadir tiempo.

### Reducción de ruido y clics

Selecciona solo ruido de fondo (normalmente de medio segundo a varios), elige **Capturar perfil de ruido**, selecciona el audio que quieres limpiar y vuelve a abrir **Reducción de ruido**. Capturar desde la ventana también funciona sin cambiar audio. El perfil promedia como máximo los primeros 30 s. La duración mínima depende del muestreo; muestreo/canales deben coincidir. Para un canal estéreo se usa el correspondiente del perfil. Guardar/cargar usa `.ssnoise`, un espectro sin grabación de audio. Reutilízalo solo en una configuración coincidente.

Reducción máxima 0–36 dB; empieza con 6–12 dB. Sensibilidad trata más fondo como ruido; suavizado calma cambios pero puede dejar ruido tras sonidos. Enlazar estéreo mantiene el balance. «Conservar solo ruido eliminado» permite oír lo quitado: desactívalo antes de limpiar. Suave/Equilibrado son inicios útiles. Mejor para siseo/ventilación constantes; no separa voces ni recupera detalles. Demasiada reducción o un perfil musical puede dañar el sonido. Duración/marcadores fijos; procesamiento sin tiempo real.

**Eliminación de clics** une muestras intactas alrededor de impulsos breves aislados. Un multiplicador de umbral alto es prudente; menor salto mínimo en dBFS detecta clics suaves. Anchura máxima 0,02–2 ms. Conservador, clics pequeños y anchos son inicios. Escucha con cuidado la percusión: sus ataques pueden parecer daños. Crujidos largos, saturación y muestras dañadas en extremos requieren otro tratamiento.

### Tiempo y tono

**Tiempo/tono → Estirar duración** cambia duración (25–400 %) conservando tono: 200 % duplica, 50 % reduce a la mitad. Los campos de tempo calculan BPM antiguo/nuevo (120→100 da 120 %), sin detección automática. Los marcadores internos siguen la escala; audio/marcadores posteriores se desplazan. El estéreo necesita ambos canales. **Cambio de tono** varía −24…+24 semitonos sin cambiar duración/marcadores; ±12 es una octava y 0,01 semitono un cent. Preservar formantes ayuda a conservar la voz; compara ambos ajustes en instrumentos.

Fino (predeterminado) y Rápido usan Rubber Band sin tiempo real. El estéreo se procesa conjuntamente; los extremos pueden sonar artificiales. Para un cambio real usa al menos 50 ms y 64 muestras. El ajuste neutro devuelve exactamente el original; la salida se redondea a muestras. La vista previa analiza toda la selección antes de reproducir hasta ocho segundos; archivos largos requieren tiempo y memoria de análisis. Se puede cancelar. Para un clip, edita una copia y aplícala; las curvas escalan, los clips posteriores no se desplazan automáticamente.

### Efectos especiales

**Especial → Distorsión** ofrece recorte suave (saturación redondeada), duro (corte brusco), plegado de onda y reducción de bits (2–16). Ganancia de entrada 0–36 dB, techo 10–100 %, mezcla original/procesada, salida −24…+24 dB. El techo solo moldea la parte procesada, no la seca ni la salida total. Calidez suave, crunch, plegado y bits son inicios. Alta calidad sobremuestrea para reducir aliasing (normalmente 4×, adaptado con muestreo alto) y procesa toda la selección incluso para vista previa; estándar es más rápido/áspero. Duración/marcadores fijos y silencio conservado.

**Convolución** aplica una respuesta al impulso WAV de filtro, pantalla o espacio acústico. Elígela, ajusta seca/efecto y escucha. Mono funciona por canal; una respuesta estéreo exige entrada estéreo y usa el canal seleccionado correspondiente. Otro muestreo se convierte; respuesta limitada tras conversión a 10 segundos y 524 288 muestras, con archivo de hasta 32 MiB. Se rechazan respuestas vacías o silenciosas. La cola no añade otro fundido. Normalizar energía escala ambos canales juntos; desactívalo para respuestas calibradas. Seca 0 %, efecto 100 % da un filtro puro. Conservar cola completa añade duración de respuesta menos una muestra y desplaza lo posterior. Sin ello mantiene duración. Conserva el archivo intacto para F2; si cambia/falta, elígelo otra vez.

## 8. Generar, analizar y convertir

**Generar → Tonos** inserta una senoide en el cursor o reemplaza la selección con duración, frecuencia Hz y amplitud % elegidas. Prueba 440 Hz a nivel moderado. **Generar → Silencio** inserta/reemplaza una duración de silencio; **Efectos → Silencio** conserva la duración existente.

**Analizar → Análisis de frecuencias / Alt+Z** muestra frecuencia frente a dBFS de canales/intervalo elegidos (o grabación entera). En intervalos largos usa una parte central limitada, ventana de Hann y potencia media de canales. Muestra frecuencia/nivel del pico debajo. Selecciona un sonido corto para estudiarlo; no es un espectrómetro continuo. Cerrar no cambia audio.

**Editar → Convertir frecuencia de muestreo** convierte toda la forma de onda a los Hz elegidos, conservando tono/duración con redondeo a tramas (al menos una). Cursor/selección siguen los mismos tiempos. Deshacer restaura audio y muestreo. Esto cambia el documento; la conversión automática de reproducción solo cambia la salida.

## 9. Multipista y automatización

Crea una sesión con muestreo/número de pistas e importa WAV por menú/botón o arrástralos desde el gestor. Se convierten muestreos y varios archivos ocupan pistas sucesivas. **Ventana → Insertar forma de onda actual en multipista** inserta la forma abierta. Añadir/quitar actúa sobre la pista elegida; deshacer restaura lo eliminado. Los nombres son editables. Silencio apaga y Solo limita a pistas solo; silencio tiene prioridad. Pan −100 izquierda, 0 centro, +100 derecha; en estéreo atenúa un lado sin copiar canales.

En **Mover clips**, arrastra el centro para mover y los bordes para recortar; se conserva el origen para alargar. El espacio vacío selecciona un intervalo de reproducción. **Duplicar clip / Ctrl+D** comparte origen; **Eliminar clip / Supr** quita el clip, no el archivo. Clic derecho abre comandos. **Propiedades del clip** ajusta nombre, límites temporales/origen (segundos), ganancia, pan, fundidos y silencio; los fundidos juntos deben caber. Cancelar no cambia nada.

**Curva de volumen** y **Curva panorámica** dibujan puntos en clips. Pulsa para añadir, arrastra para mover, clic derecho/doble clic abre tramas/valores exactos, quitar/Supr elimina el punto elegido y restablecer vuelve a neutro. Esc cancela el arrastre. Volumen: abajo 0 %, medio 100 %, arriba 200 %, multiplicando ganancias y fundidos. Pan: arriba derecha, medio neutro, abajo izquierda, sumándose a pan de clip/pista. Centra pan normal para un barrido completo. Los puntos siguen al origen al mover/recortar y se guardan. Vuelve a mover clips para desplazarlos.

Doble clic o **Editar copia en forma de onda** abre una copia para efectos sin tiempo real. **Ventana → Aplicar forma de onda al clip** devuelve expresamente el resultado; cambiar de vista no lo aplica. Deshacer en sesión restaura audio/curvas. Se reconvierte muestreo, las curvas siguen la duración y los clips posteriores quedan fijos: comprueba solapamientos. **Mezclar sesión / Mezclar** exporta toda la sesión sin depender de la selección, con silencio/solo, ganancias/pan, curvas, efectos y colas. Guardar sesión conserva el proyecto editable. Estos ajustes cambian durante reproducción; deshacer/cambiar vista la detiene.

## 10. Efectos de pista en tiempo real y VST3

Abre **FX** junto a la pista o **Efectos → Efectos de pista**. Añade efecto, elige ajustes/preajuste; Aceptar añade y Aplicar cambia sin cerrar. Subir/bajar cambia orden, marca omite, editar/doble clic modifica y quitar elimina. Hasta 16 efectos se ejecutan de arriba abajo tras ganancia/curvas/fundidos del clip y antes de volumen/pan de pista. Mono pasa a estéreo. Cola tras último clip añade 0–60 s. Las cadenas sirven en reproducción, mezcla, proyecto y recuperación. Reiniciar/buscar/omitir vacía memoria; editar efectos internos puede reiniciar cola, los parámetros VST3 conservan instancia.

Las cadenas en tiempo real admiten amplificación fija, mezclador, dinámica, EQ gráfico/paramétrico, filtros, retardo, eco, reverberación, inversión y VST3. Para variar ganancia usa la curva de volumen. Normalización, ruido/clics, tiempo/tono, distorsión y convolución siguen sin tiempo real. Aplicar actualiza mientras escuchas; el audio ya almacenado usa ajustes anteriores. Los orígenes no cambian.

Instala un **efecto VST3 nativo de Linux de 64 bits**, elige complemento VST3, **Añadir paquete VST3** y su carpeta `.vst3`. Varios efectos aparecen por separado. Busca parámetros y cambia su posición normalizada 0–100 % (50 % no significa necesariamente medio volumen). Los discretos tienen pasos y los de solo lectura no cambian. Aplicar permite escuchar en pista; Aceptar confirma/cierra. No se integra su editor propio. Se admite un bus estéreo de entrada/salida y procesamiento float32. Sin VST2, VST Windows, instrumentos MIDI, cadenas laterales ni otros formatos. Las funciones no admitidas se notifican sin cambiar el proyecto.

Se muestra el retardo del complemento sin compensarlo entre pistas. Cada uno usa un proceso auxiliar: fallo, tiempo agotado o audio inválido detiene reproducción y conserva la toma. El proyecto guarda parámetros y hasta 1 MiB de estado por efecto, no código ni bibliotecas/muestras externas. En otro equipo instala/añade el paquete coincidente. Versiones ausentes/cambiadas conservan ajustes pero exigen el efecto adecuado o una omisión deliberada; no se eliminan silenciosamente.

## 11. Grabar con acompañamiento

Coloca acompañamiento en pistas, elige otra pista de destino y sitúa el cursor. Pulsa **R**, elige entrada/nuevo clip y activa «Reproducir pistas existentes al grabar». Pistas y efectos parten del cursor; la entrada no va a altavoces. **P** pausa/reanuda ambos; **Detener/Esc/Espacio/R** detiene y conserva la toma como un paso de deshacer. Puede seguir grabando tras terminar el acompañamiento; una duración máxima detiene ambos. Descartar quita solo la nueva toma. Un fallo conserva muestras capturadas. Las ediciones quedan bloqueadas.

El desplazamiento de posición mueve el clip insertado: negativo antes, positivo después. Si llega 15 ms tarde, prueba −15 ms. Graba un clic conocido por tu ruta real de entrada/salida, compara posiciones, introduce la diferencia y comprueba con otra toma. Recalibra tras cambiar dispositivo/búfer. El audio anterior a cero se recorta al insertar. Se recuerda el desplazamiento; calibración física automática, corrección de deriva, compensación de complementos y punch-in/out siguen en desarrollo. Prueba una toma corta antes de una sesión larga.

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

Sin entrada: revisa dispositivo/canal y nivel de micrófono Linux, reconecta y empieza otra toma. Sin salida: comprueba ruta, volumen, silencio/solo y dispositivos. Distorsión/picos rojos: baja ganancia sumada y normaliza antes de PCM; pegar mezclando y clips solapados suman. Pegado rechazado: revisa canales o duración exacta del reemplazo mono. Efecto desactivado: abre forma/copia; mezclador necesita estéreo y cambios temporales ambos canales. Puntos en lugar de clips: elige mover clips. Disco lleno: libera espacio sin borrar archivos de trabajo activos. Recuperación dañada: quedan originales; elimina copia solo si ya no hace falta.

En desarrollo: editores propios de complementos, más formatos, compensación automática de latencia/deriva, punch-in/out, favoritos personalizados y editor de marcadores. Cadenas en tiempo real, Linux VST3 y acompañamiento están disponibles como se describe. Guarda antes de salir. Novedades: [SoundSausage](https://github.com/rene-timmermans/SoundSausage).
