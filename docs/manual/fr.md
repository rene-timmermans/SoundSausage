# SoundSausage — manuel

Version 0.27.0. Un éditeur audio intuitif et simple à utiliser, avec tous les outils là où vous les attendez. Ce manuel décrit les fonctions disponibles, les effets et leurs limites pratiques.

<!-- soundsausage-contents:start -->
<a id="ss-contents"></a>

## Sommaire

Cliquez sur un sujet pour y accéder. Sommaire revient ici ; Précédent et Suivant changent de sujet. F3 et Maj+F3 suivent les résultats de recherche.

- [1. Langue et aide](#ss-topic-1-langue-et-aide)
- [2. Démarrage rapide et espace de travail](#ss-topic-2-demarrage-rapide-et-espace-de-travail)
- [3. Fichiers, projets et récupération](#ss-topic-3-fichiers-projets-et-recuperation)
  - [MP3 et WAV](#ss-topic-mp3-et-wav)
  - [Métadonnées MP3 après modification](#ss-topic-metadonnees-mp3-apres-modification)
- [4. Lecture, zoom et matériel audio](#ss-topic-4-lecture-zoom-et-materiel-audio)
- [5. Enregistrer](#ss-topic-5-enregistrer)
  - [Enregistrer l’audio système (ce que vous entendez)](#ss-topic-enregistrer-laudio-systeme-ce-que-vous-entendez)
- [6. Sélection, canaux et édition](#ss-topic-6-selection-canaux-et-edition)
  - [Modifier des échantillons individuels](#ss-topic-modifier-des-echantillons-individuels)
  - [Dessiner la forme d’onde](#ss-topic-dessiner-la-forme-donde)
- [6a. Repères](#ss-topic-6a-reperes)
- [7. Appliquer des effets](#ss-topic-7-appliquer-des-effets)
  - [Remaster](#ss-topic-remaster)
    - [Choisir un préréglage Remaster](#ss-topic-choisir-un-prereglage-remaster)
    - [Ce que Remaster change dans le son](#ss-topic-ce-que-remaster-change-dans-le-son)
    - [Effet des réglages Remaster](#ss-topic-effet-des-reglages-remaster)
    - [Comparer et appliquer Remaster](#ss-topic-comparer-et-appliquer-remaster)
    - [Résultats attendus de Remaster](#ss-topic-resultats-attendus-de-remaster)
  - [Amplitude](#ss-topic-amplitude)
    - [Amplifier / fondre](#ss-topic-amplifier-fondre)
    - [Mélangeur de canaux](#ss-topic-melangeur-de-canaux)
    - [Traitement de la dynamique](#ss-topic-traitement-de-la-dynamique)
    - [Enveloppe de volume](#ss-topic-enveloppe-de-volume)
    - [Normaliser](#ss-topic-normaliser)
    - [Inversion de polarité, sens et silence](#ss-topic-inversion-de-polarite-sens-et-silence)
  - [Égalisation et filtres](#ss-topic-egalisation-et-filtres)
    - [Égaliseur graphique](#ss-topic-egaliseur-graphique)
    - [Égaliseur paramétrique](#ss-topic-egaliseur-parametrique)
    - [Filtres](#ss-topic-filtres)
  - [Délai, écho et réverbération](#ss-topic-delai-echo-et-reverberation)
    - [Effets de retard → Retard](#ss-topic-effets-de-retard-retard)
    - [Écho](#ss-topic-echo)
    - [Réverbération](#ss-topic-reverberation)
  - [Réduction du bruit et déclics](#ss-topic-reduction-du-bruit-et-declics)
    - [Estimation du bruit → Profil de bruit fixe](#ss-topic-estimation-du-bruit-profil-de-bruit-fixe)
    - [Suppression des clics](#ss-topic-suppression-des-clics)
  - [Temps et hauteur](#ss-topic-temps-et-hauteur)
    - [Durée/hauteur → Étirement temporel](#ss-topic-duree-hauteur-etirement-temporel)
    - [Transposition](#ss-topic-transposition)
  - [Effets spéciaux](#ss-topic-effets-speciaux)
    - [Spécial → Distorsion](#ss-topic-special-distorsion)
    - [Convolution](#ss-topic-convolution)
- [8. Générer, analyser et convertir](#ss-topic-8-generer-analyser-et-convertir)
- [9. Multipiste et automation](#ss-topic-9-multipiste-et-automation)
- [10. Effets de piste, plug-ins et enregistrement](#ss-topic-10-effets-de-piste-plug-ins-et-enregistrement)
  - [VST3, LV2 et LADSPA](#ss-topic-vst3-lv2-et-ladspa)
  - [Compensation du retard des plug-ins](#ss-topic-compensation-du-retard-des-plug-ins)
  - [Accompagnement et synchronisation](#ss-topic-accompagnement-et-synchronisation)
  - [Punch-in/out](#ss-topic-punch-in-out)
- [11. Enregistrer avec accompagnement](#ss-topic-11-enregistrer-avec-accompagnement)
- [12. Raccourcis, favoris et dépannage](#ss-topic-12-raccourcis-favoris-et-depannage)

<!-- soundsausage-contents:end -->

<a id="ss-topic-1-langue-et-aide"></a>

## 1. Langue et aide

Dans **Options → Langue**, choisissez Nederlands, English, Deutsch, Français ou Español. Menus, fenêtres, conseils et manuel ouvert changent immédiatement. Le choix est mémorisé au prochain démarrage. Les noms de fichiers, pistes et plug-ins conservent leur orthographe.

**Aide → Manuel** ou **F1** ouvre ce manuel hors ligne à côté de l'éditeur. **Ctrl+F** active la recherche ; **F3** trouve l'occurrence suivante et **Maj+F3** la précédente, avec retour au début ou à la fin. Précédent et Suivant changent de sujet sans recherche et se désactivent aux limites. Seuls les liens web explicitement ouverts nécessitent Internet. **À propos** indique version, auteur, licence, site et composants.

<a id="ss-topic-2-demarrage-rapide-et-espace-de-travail"></a>

## 2. Démarrage rapide et espace de travail

Les boutons de barre et de transport ont un fond neutre et des icônes de la couleur d’accent ; un cadre fin marque le choix actif.

L’icône du programme sur fond violet apparaît dans les barres de titre et la barre des tâches. **Aide → À propos** affiche la mascotte détourée à côté des informations du programme.

Ouvrez un WAV ou MP3 par **Fichier → Ouvrir**. **Espace** démarre ou arrête la lecture. Sélectionnez un passage, choisissez **Effets → Amplitude → Normaliser**, écoutez avec **Écouter**, puis validez par **OK**. **Ctrl+Z** annule. **Enregistrer sous** garde un résultat séparé. Pour plusieurs prises, créez une **Nouvelle session multipiste**, importez les WAV ou MP3 puis utilisez **Mixer**.

**Édition la forme d’onde** modifie une prise ; **Vue multipiste** combine des clips. Passez de l'une à l'autre avec **Tab**, les boutons supérieurs ou **Affichage** ; les deux documents restent disponibles. Les infobulles expliquent les boutons. **Afficher le texte des barres d’outils** ajoute leur texte, **Options → Afficher la barre d’état** affiche ou masque la fine ligne d’information tout en bas, sous les indicateurs de niveau. Elle indique l’état de lecture et les détails du fichier ; le choix est conservé au prochain démarrage. **F11** bascule le plein écran. La taille, la position et l’état plein écran ou agrandi de la fenêtre sont restaurés au prochain démarrage. Si un écran n’est plus disponible, la fenêtre revient sur un écran disponible. Pendant la lecture, le curseur suit l’horloge audio. L’image de la forme d’onde est réutilisée ; après un zoom ou un redimensionnement, les nouvelles crêtes sont préparées en arrière-plan. L’aperçu précédent peut rester brièvement visible. L'horloge suit l'audio ; les champs de sélection indiquent début, fin et durée, ceux de vue l'intervalle visible. Des crêtes rouges signalent une surcharge ; une étoile indique des modifications non enregistrées.

Les fenêtres et les échelles des graphiques s’adaptent à la taille de police du bureau et à la langue choisie. Si un formulaire dépasse l’écran, faites défiler ses réglages ; les boutons de validation et d’annulation restent accessibles.

Deux fines lignes horizontales marquent le bord inférieur du canal gauche et le bord supérieur du canal droit. Elles s’arrêtent aux limites du graphique, également pendant l’enregistrement en direct.

<a id="ss-topic-3-fichiers-projets-et-recuperation"></a>

## 3. Fichiers, projets et récupération

**Nouveau** crée une forme d'onde mono ou stéréo à la fréquence choisie. **Ouvrir** lit les WAV et MP3. **Enregistrer** actualise le fichier ; **Enregistrer sous** choisit nom/encodage ; **Enregistrer la sélection** écrit uniquement l'intervalle et les canaux sélectionnés. L'export WAV propose PCM 8/16/24/32 bits et float32. PCM16 facilite l'échange ; float32 conserve aussi les crêtes internes au-delà de 0 dBFS. Augmenter la résolution ne restitue pas les détails perdus. Un ancien WAV 32 bits ambigu demande une interprétation PCM ou flottante historique ; annuler le laisse intact.

Textes WAV, repères et étiquettes sont conservés. Les repères suivent les éditions, collages et exports de sélection ; le titre cible est gardé. Les champs propres aux enregistreurs restent inchangés, sans recalcul après effet. Les métadonnées supplémentaires sont limitées à 16 Mio : une entrée excessive est refusée ; les omissions à l'export demandent confirmation. Le mixage ne fusionne pas les marqueurs des sources. Les gros exports utilisent RF64 si nécessaire.

**Nouvelle session multipiste**, **Ouvrir une session**, **Enregistrer la session** et **Enregistrer la session sous** gèrent les projets éditables. Un projet SoundSausage (`.celp`) contient audio, clips, courbes, réglages de pistes, ordre/contournement/queues d'effets et paramètres VST3. Gardez le projet en plus du WAV final pour retrouver les pistes séparées. Les anciens projets SoundSausage restent lisibles ; les projets nouvellement enregistrés nécessitent l’application 0.26.0 ou ultérieure. L'import historique `.ses` est limité ; poursuivez dans un nouveau projet SoundSausage.

**Fermer / Ctrl+W** ferme la forme d'onde courante ; en multipiste, **Fermer la session** ferme la session. Choisissez enregistrer, abandonner ou annuler. L'autre vue et le presse-papiers restent disponibles. **Quitter / Ctrl+Q** quitte en vérifiant les modifications non enregistrées.

Les fichiers longs sont traités par blocs sur disque, sans l'ancienne limite de 128 Mio. Prévoyez de la place pour sources, résultats et annulations. Les sessions sont limitées à 24 heures et 32 pistes. Les opérations longues affichent progression et annulation ; annuler conserve audio, sélection, historique et ancienne cible d'export. Un effet appliqué constitue une annulation.

Après une fermeture imprévue, restaurez, supprimez ou reportez la dernière sauvegarde de récupération. **Fichier → Récupérer le travail** ouvre les copies conservées. Les originaux restent intacts ; forme d'onde, session, canaux, clips, courbes et effets reviennent, mais l'historique d'annulation repart à zéro. Les éditions validées sont sauvegardées, curseur/sélection environ chaque seconde. Les instances actives sont ignorées. Enregistrer ou fermer normalement efface la copie propre à l'instance. Gardez vos sauvegardes ; une erreur disque peut laisser un état plus ancien.

<a id="ss-topic-mp3-et-wav"></a>

### MP3 et WAV

Ouvrez les MP3 par **Fichier → Ouvrir**, importez-les en multipiste ou déposez-les sur la chronologie. Sélection, édition et effets travaillent sur l’audio décodé. **Enregistrer sous**, **Enregistrer la sélection** et **Mixer** proposent WAV et MP3 ; l’extension suit le format choisi. Enregistrer un MP3 existant utilise l’encodage MP3 choisi ; Enregistrer sous permet une copie WAV.

MP3 propose 128, 192, 256 et 320 kb/s. Un débit supérieur occupe plus de place et conserve généralement plus de détails. MP3 est avec perte : recomprimer peut supprimer d’autres détails. WAV évite une compression MP3 supplémentaire sans restaurer les informations perdues. Choisissez WAV float32 pour poursuivre l’édition, PCM16 pour l’échange. L’export MP3 utilise la fréquence la plus proche parmi 32 000, 44 100 et 48 000 Hz, à durée égale ; le document garde sa fréquence. Ces fréquences conviennent aux quatre débits MP3 proposés ; à des fréquences plus basses, l’encodeur peut utiliser un débit inférieur à celui demandé. Le minimum de 2 ms évite que de très courts fragments deviennent plus longs après décodage MP3. Utilisez WAV pour les sélections de moins de 2 ms.

<a id="ss-topic-metadonnees-mp3-apres-modification"></a>

### Métadonnées MP3 après modification

Titre, artiste, album, commentaires et pochettes sont conservés, y compris via WAV et les projets SoundSausage. La durée est actualisée. Les tags ordinaires et identifiants existants restent liés au fichier de destination.

Les **chapitres** suivent automatiquement les modifications. Supprimer avance les chapitres suivants ; insérer les retarde. Rogner et exporter une sélection conserve les chapitres qui la recoupent, avec des temps relatifs au fragment gardé. Les chapitres vides ou entièrement supprimés disparaissent ; la table des matières conserve des références valides. Coller reprend les noms et la hiérarchie des chapitres du fragment tout en conservant les tags généraux de destination. L’étirement temporel adapte les limites ; le changement de fréquence d’échantillonnage conserve les temps en millisecondes. Annuler restaure aussi les métadonnées d’origine.

La précision des chapitres est d’une milliseconde ; un reste arrondi à une durée nulle disparaît. Inverser reflète les chapitres entièrement dans la plage. Un chapitre partiellement inversé qui décrirait des morceaux audio séparés est supprimé ; un chapitre contenant toute la plage inversée reste présent.

Les **mesures** peuvent devenir obsolètes après modification audio. Les valeurs reconnues ReplayGain, R128, MP3Gain et de crête, les empreintes, ajustements de volume relatif et anciennes informations d’encodage sont supprimés. Les informations temporelles non prises en charge, notamment paroles synchronisées, anciens index de recherche et positions de synchronisation, disparaissent aussi. ReplayGain n’est pas recalculé. Un changement de tempo supprime la valeur BPM existante ; un changement de hauteur supprime la tonalité existante. Les autres modifications conservent ces deux valeurs. Les paroles ordinaires sans horodatage et les champs privés inconnus restent inchangés. Réencoder en MP3 supprime également anciennes mesures et positions de fichier, puisque la compression modifie le son et la structure. Les informations d’encodage proviennent du nouveau fichier réel.

**WAV vers MP3 :** les champs INFO pris en charge pour titre, artiste, album, genre, date, numéro de piste, droits d’auteur et commentaires sont transférés. Les valeurs ID3 existantes sont prioritaires. Les champs incompatibles, données INFO mal formées et valeurs contradictoires sont signalés avant export. **Non** annule et préserve une destination existante ; **Oui** continue avec les omissions indiquées. Les tags ID3 supplémentaires d’un WAV sont également signalés avant omission. Les anciennes informations de logiciel sont remplacées par celles du nouvel encodeur. Les repères WAV pris en charge deviennent des chapitres MP3 ; les autres données incompatibles nécessitent ce choix.

Les métadonnées supplémentaires restent limitées à 16 Mio. Les données ID3 WAV illisibles restent conservées telles quelles ; l’export MP3 signale une erreur et préserve la destination. Le mixage ne fusionne pas les métadonnées de toutes les pistes. Les longues conversions affichent la progression et sont annulables ; prévoyez de l’espace pour la conversion et l’édition.


<a id="ss-topic-4-lecture-zoom-et-materiel-audio"></a>

## 4. Lecture, zoom et matériel audio

**Espace** démarre/arrête, **P** met en pause/reprend, **Échap** arrête. La sélection définit la lecture ; sinon elle part du curseur. **Boucle** répète, avec une éventuelle courte transition. **Début/Fin** vont aux extrémités ; les boutons sautent de cinq secondes. Naviguer ou appliquer une édition arrête la lecture. **Zoom avant / Zoom arrière**, **Ctrl+molette**, molette et barre horizontale déplacent la vue. **Vue complète / Ctrl+0** montre tout ; **Zoom sur la sélection / Ctrl+Maj+A** cadre la sélection. Leurs icônes diffèrent. De près les échantillons sont reliés ; de loin les crêtes min/max par colonne sont conservées.

Dans **Options → Périphériques audio**, choisissez une sortie ou **Valeur par défaut du système** ; ce choix mémorisé sert aussi à l'aperçu. Le tampon vaut 100 ms par défaut : plus grand, il tolère les interruptions ; plus petit, il répond plus vite. Le tampon réel peut différer. Changer arrête lecture/aperçus. Si le périphérique disparaît, reconnectez-le ou choisissez une sortie puis relancez. Vérifiez volume système, routage, muet et solo. La conversion pour la sortie ne change pas l'enregistrement.

<a id="ss-topic-5-enregistrer"></a>

## 5. Enregistrer

Branchez un micro/interface, choisissez l'entrée dans **Périphériques audio**, puis pressez **R**. Réglez entrée, destination, mono/stéréo, premier canal et durée maximale. Une nouvelle forme d'onde reste séparée ; insérer au curseur/remplacer la sélection modifie une forme existante ; le multipiste ajoute un clip sur la piste choisie au curseur. Une entrée mono peut alimenter les deux canaux stéréo. La forme existante détermine fréquence/canaux ; une autre fréquence d'entrée est convertie après arrêt. **Jusqu’à l’arrêt** continue jusqu'à l'arrêt ou épuisement du disque.

**Démarrer l’enregistrement** ouvre alors le microphone, jamais avant. La forme en direct montre les 20 dernières secondes, l'horloge la durée totale et les vumètres l'entrée. **P** pause/reprend sans inclure le temps de pause. **Arrêter**, **Échap**, **Espace** ou **R** conserve la prise. Insertion/remplacement ou nouveau clip forme une annulation ; une nouvelle forme d'onde doit encore être enregistrée. **Abandonner l’enregistrement** confirme la suppression de cette seule prise. Fermer propose conserver, abandonner ou continuer. Les autres éditions sont verrouillées pendant l'enregistrement.

L'entrée n'est pas renvoyée aux haut-parleurs. Réglez le gain sur l'interface/micro ou dans Linux ; baisser ensuite ne répare pas une entrée écrêtée. La perte d'un périphérique arrête et conserve l'audio capturé au lieu de changer de micro. Les prises sont écrites par blocs, avec sauvegarde environ chaque seconde. La récupération ouvre une forme séparée. Annuler la conversion après arrêt garde la prise dans **Récupérer le travail** et laisse l'ancien document intact.

**Début à ignorer** retire une fois les premières millisecondes de chaque prise pour exclure un clic de démarrage. La valeur initiale est 50 ms, réglable de 0 à 500 ms et mémorisée. À 0 ms, le début est conservé ; une coupe est suivie d’un fondu d’entrée de 5 ms. L’audio retiré n’est pas enregistré. Horloge, vue, niveaux et durée maximale suivent l’audio conservé. Pause/reprise ne répète pas la coupe. Avec accompagnement, la position du clip tient compte du temps retiré pour préserver l’alignement.

<a id="ss-topic-enregistrer-laudio-systeme-ce-que-vous-entendez"></a>

### Enregistrer l’audio système (ce que vous entendez)

Choisissez **Options → Périphériques audio → Périphérique d’enregistrement → Audio
système (ce que vous entendez)**, également disponible dans la fenêtre d’enregistrement.
La source, mémorisée, enregistre la sortie Linux par défaut sans microphone.
Choisissez cette sortie dans les réglages audio du système, lancez l’autre application,
puis appuyez sur **R** et démarrez. **Stéréo** conserve les deux canaux ; Mono utilise
le premier canal d’entrée 1 (gauche) ou 2 (droite). **P** met en pause/reprend sans
inclure la pause. Stop conserve la prise ; modifiez et enregistrez en WAV/MP3.

Chaque nouvelle prise détermine la sortie système par défaut actuelle, qui peut
différer du périphérique de lecture choisi séparément dans SoundSausage. Seul le
son envoyé à cette sortie est inclus, y compris les accompagnements SoundSausage
qui y jouent. Les niveaux suivent le mixeur audio et peuvent différer du volume
physique des haut-parleurs. L’entrée n’est pas rejouée dans les haut-parleurs.

Nécessite PulseAudio ou la compatibilité PulseAudio de PipeWire ; les paquets
incluent les outils clients. Une sortie, un serveur ou un outil manquant produit
un message, sans jamais sélectionner le microphone à sa place. Changez la sortie
entre les prises. Un changement ou une perte de sortie signalé arrête et conserve
la prise ; corrigez le routage et recommencez. **Valeur par défaut du système** reste
l’entrée microphone par défaut, distincte de **Audio système**.

<a id="ss-topic-6-selection-canaux-et-edition"></a>

## 6. Sélection, canaux et édition

Cliquez pour placer le curseur, glissez pour sélectionner. En stéréo, glissez dans L ou R pour un canal, sur les deux pour la stéréo. **Canaux** ou **Édition → Choisir les canaux** change les canaux sans perdre l'intervalle : **Alt+B / Alt+L / Alt+R** pour les deux/gauche/droite. Maj+clic étend en gardant les canaux ; double-clic sélectionne l'audio visible du canal cliqué ; **Ctrl+A** prend toute la durée des canaux choisis. Le mono a un canal. **Définir la sélection** saisit les trames exactes ; 44 100 trames à 44 100 Hz valent une seconde. **F4** rentre les bornes aux passages par zéro (gauche si les deux).

**Couper / Ctrl+X** retire et copie ; **Copier / Ctrl+C** copie ; **Coller / Ctrl+V** remplace la sélection ou insère au curseur. **Collage mixé / Ctrl+M** additionne l'audio du presse-papiers et peut augmenter les crêtes. **Suppr** retire l'intervalle ; **Rogner / Ctrl+T** garde uniquement celui-ci. **Ctrl+Z / Ctrl+Maj+Z** annule/rétablit. Le collage convertit la fréquence sans changer le presse-papiers. Pour les deux canaux, le nombre doit correspondre. Copier/exporter gauche ou droite donne du mono ; l'enregistrement normal garde toute la stéréo.

La stéréo garde une ligne temporelle commune. Avec **Gauche** ou **Droite**, couper/supprimer, insérer, coller une durée différente, étirer, générer des sons/silences et ajouter une queue décale uniquement le canal choisi. L’autre garde ses échantillons à leurs positions d’origine. Le canal plus court est complété par du silence à la fin. **Les deux** décale les deux canaux et leurs repères communs ; **Effets → Silence** efface sans décaler.

Exemple : supprimer les secondes 2–3 à gauche avance la suite gauche d’une seconde et ajoute une seconde de silence final ; droite reste en place. **Rogner** place uniquement le fragment choisi du canal choisi à l’instant zéro et complète le reste par du silence. Ce silence fait partie de l’audio, reste après enregistrement/réouverture et suit les insertions ultérieures. Supprimez le silence final indésirable avec Les deux. Les repères et chapitres MP3 communs gardent leurs positions lors d’une modification d’un seul canal ; vérifiez leur signification après un décalage.

Le presse-papiers mono peut remplacer un intervalle plus court ou plus long, ou s’insérer au curseur. Un presse-papiers stéréo fournit le canal gauche/droit correspondant. La fréquence est convertie si nécessaire. Les repères/chapitres du presse-papiers ne sont fusionnés qu’avec Les deux ; le collage sur un canal garde les repères communs de destination. **Collage mixé** additionne depuis le début de sélection/curseur sans décaler la suite et peut dépasser la fin ; l’autre canal reçoit du silence final.

Pour enregistrer dans un canal, choisissez Gauche/Droite, **R**, puis **Insérer au curseur** ou **Remplacer la sélection**. La capture est mono, à la fréquence de la forme d’onde. **Premier canal d’entrée** choisit l’entrée matérielle indépendamment de la destination gauche/droite. Arrêter applique une modification, décale ce seul canal et complète si nécessaire. Nouvelle forme d’onde reste disponible. Le choix de canal est verrouillé pendant la capture ; un échec/annulation du traitement final conserve la prise sous Récupérer le travail. Annuler/Rétablir restaure audio, remplissage, métadonnées et canaux ; la récupération conserve l’audio stéréo modifié.

<a id="ss-topic-modifier-des-echantillons-individuels"></a>

### Modifier des échantillons individuels

Zoomez avec **+** ou **Ctrl+molette** jusqu’aux points carrés (au moins deux pixels logiques entre échantillons). L’axe horizontal indique alors les indices à partir de 0. Glissez un point verticalement pour modifier uniquement cet échantillon de ce canal. Sa position reste fixe, même si le pointeur traverse d’autres points ou canaux. Le déplacement donne un aperçu ; relâcher valide, **Échap** annule. **Maj+glisser** permet toujours de sélectionner l’audio.

Un double-clic ou clic droit sur un point ouvre **Modifier un échantillon**. **Édition → Modifier un échantillon** fonctionne à tout niveau de zoom. La position initiale est celle du curseur dans le premier canal sélectionné ; indice et canal sont modifiables. Affichez une valeur normalisée ou en 8, 16 ou 24 bits signés. Zéro est le silence ; −1/+1 représentent le niveau maximal normal. Par exemple, −16384 en affichage 16 bits correspond à −0,5 normalisé. Changer la plage d’affichage ne change ni l’audio ni l’encodage. **OK** applique une valeur ; **Annuler** préserve l’original.

Chaque déplacement terminé ou valeur confirmée forme une étape Annuler/Rétablir. Tous les autres échantillons, l’autre canal, la durée et les métadonnées restent inchangés. Le glissement est limité à −1 … +1 ; les crêtes flottantes existantes restent accessibles numériquement. La lecture s’arrête au début d’une correction ; l’édition est bloquée pendant l’enregistrement. Pour une région multipiste, modifiez sa copie en forme d’onde puis appliquez-la explicitement à la région. Écoutez après chaque correction ; pour un clic de plusieurs échantillons, rapprochez chaque point du tracé voisin. Une transition brutale vers zéro peut créer un clic. WAV float32 conserve exactement les valeurs internes ; enregistrer en MP3 recompresse tout le fichier avec pertes.

<a id="ss-topic-dessiner-la-forme-donde"></a>

### Dessiner la forme d’onde

Activez **Édition → Dessiner la forme d’onde**, appuyez sur **D** ou utilisez le crayon près des boutons de zoom. Dessinez directement sur la forme d’onde avec le bouton gauche ; inutile de viser un point individuel. La ligne dessinée remplace les valeurs entre −1 et +1 ; elle ne déplace pas verticalement la forme d’onde d’origine.

Le zoom détermine la taille du groupe : environ deux pixels logiques d’audio, arrondis au nombre entier supérieur d’échantillons. À fort zoom, un échantillon change ; en dézoomant, plusieurs changent ensemble. Chaque groupe couvre au plus une seconde. Un geste plus long peut toucher plusieurs groupes et modifier plus d’une seconde au total. Des lignes droites relient les positions successives du pointeur ; repasser sur un groupe remplace son dessin précédent.

Le canal de départ reste fixe même si le pointeur traverse l’autre canal. Les autres échantillons, l’autre canal, la durée et les métadonnées sont conservés. Les groupes colorés et la nouvelle ligne montrent l’aperçu. Relâcher valide tout le geste en une seule annulation. **Échap**, la perte du focus, un changement de zoom ou la désactivation du dessin annulent l’aperçu. **Maj+glisser** sélectionne toujours l’audio ; appuyez à nouveau sur **D** pour revenir au fonctionnement normal. Le dessin est bloqué pendant l’enregistrement. Zoomez pour les corrections précises : dézoomer remplace aussi les petits détails des groupes touchés. Écoutez ensuite et utilisez **Ctrl+Z** au besoin. En multipiste, modifiez une copie de la forme d’onde puis appliquez-la au clip.

<a id="ss-topic-6a-reperes"></a>

## 6a. Repères

**M** ajoute un repère au curseur. **Édition → Liste des repères** (**Ctrl+Maj+M**) permet de nommer, déplacer, supprimer ou **Aller à** un repère. **Alt+Gauche/Droite** passe au précédent/suivant. Double-cliquez sur un drapeau au-dessus de la forme d’onde pour ses propriétés. Faites-le glisser pour déplacer ; **Échap** annule, relâcher crée une étape Annuler.

Les propriétés proposent des secondes et une trame exacte. Les nouveaux noms acceptent 256 caractères au maximum, sans caractères de contrôle. Un chapitre MP3 existant peut avoir une fin, après son début et dans l’audio. Un nouveau repère est un point, pas une nouvelle plage de chapitre.

Les repères sont communs aux deux canaux. Les modifications temporelles avec **Les deux** les déplacent ensemble ; sur un seul canal, leurs positions communes restent fixes. Nommer ou déplacer ne change aucun échantillon. En multipiste, les repères de session gardent leurs positions absolues quand les clips bougent. Ils peuvent dépasser le dernier clip sans prolonger le mixage. Les repères sources restent avec leur source ; le mixage exporte uniquement ceux de la session dans sa durée audio. Aucune fusion automatique des repères sources.

WAV conserve les points cue et leurs noms. L’export MP3 les convertit en chapitres à positions millisecondes ; WAV garde la précision d’une trame. Projet et récupération conservent les repères de session ; Annuler/Rétablir fonctionne pendant l’édition. Les nouveaux projets nécessitent **0.26.0 ou ultérieur** ; les anciens restent lisibles. Jusqu’à 4096 repères sont modifiables. Les données cue inhabituelles restent conservées, mais une modification risquée est refusée. Le jeu de caractères WAV existant peut limiter les noms.

<a id="ss-topic-7-appliquer-des-effets"></a>

## 7. Appliquer des effets

Les effets de forme d'onde sous **Effets** traitent l'intervalle/canaux choisis, ou toute leur durée sans sélection temporelle. L'autre canal reste intact et audible dans l'aperçu stéréo. **Écouter** lit au maximum les huit premières secondes sans appliquer ; recliquer, changer un réglage ou fermer arrête. **OK** applique une annulation ; **Annuler** conserve l'original. **F2 / Répéter la dernière commande** répète les réglages sur la sélection/canaux actuels. Normalisation, temps/hauteur et distorsion haute qualité analysent toute la sélection avant l'aperçu.

<a id="ss-topic-remaster"></a>

### Remaster

Ouvrez **Effets → Remaster…** lorsque des voix ou instruments s’effacent brièvement derrière la batterie, ou qu’un mixage comporte de courtes coupures de volume. Remaster détecte les creux appropriés et relève localement les détails encore présents. Il traite la sélection, ou toute la forme d’onde sans sélection.

<a id="ss-topic-choisir-un-prereglage-remaster"></a>

#### Choisir un préréglage Remaster

| Préréglage | Réduction du pompage / Récupération maximale | Seuil de percussion / Temps de récupération | Correction des baisses brèves |
| --- | --- | --- | --- |
| Récupération douce | 35% / 2 dB | 4 dB / 160 ms | 0 dB : désactivée |
| Récupération équilibrée | 60% / 4 dB | 3 dB / 180 ms | 0 dB : désactivée |
| Récupération forte | 90% / 6 dB | 2 dB / 240 ms | 0 dB : désactivée |
| Baisses de volume brèves | 90% / 6 dB | 2 dB / 240 ms | 12 dB |

Commencez par **Récupération équilibrée** pour un pompage léger. **Récupération douce** modifie moins. **Récupération forte** autorise davantage de hausse et réagit à des attaques plus faibles. **Baisses de volume brèves** reprend les réglages ordinaires du mode fort et active en plus la correction rapide des creux courts et profonds. Augmenter seulement l’intensité n’active pas cette correction supplémentaire.

Un préréglage ne change que les cinq valeurs du tableau. Plafond de sortie, position d’écoute et égalisation du volume gardent leurs valeurs. Le plafond commence à −1 dBFS. **Personnalisé** conserve les valeurs courantes. Modifier un réglage de récupération ou le plafond sélectionne cet état ; la position d’écoute et l’égalisation de volume ne le font pas.

<a id="ss-topic-ce-que-remaster-change-dans-le-son"></a>

#### Ce que Remaster change dans le son

La récupération ordinaire estime les sons soutenus médiums/aigus, par exemple voix, guitare ou synthétiseur. Elle compare leur niveau à l’environnement et recherche de brefs déficits près des attaques de graves/percussions détectées. Seul le déficit reçoit une hausse limitée ; aucune piste voix ou instrument séparée n’est créée.

La correction des baisses brèves mesure les médiums/aigus sur environ **4 ms**, avec une mise à jour toutes les **1 ms** environ. Elle compare les **20–80 ms avant et après** un creux possible ; les deux côtés doivent soutenir le niveau manquant. Elle recherche des baisses d’environ **6–120 ms** et d’au moins **4 dB**, liées à la détection de percussion. Les longues pauses, passages très faibles et fondus progressifs sont ainsi évités autant que possible.

Sur un creux adapté, la correction rapide remplace localement la récupération ordinaire. Les deux gains ne sont pas additionnés. Une transition douce et un retour rapide limitent les dépassements lorsque le niveau d’origine revient. Cette voie possède ses propres temps rapides ; le **Temps de récupération** du dialogue règle la durée de maintien de la détection de percussion.

Les graves sous environ **180 Hz** ne sont pas relevés ; la transition va jusqu’à environ **600 Hz**. **Les deux** lie les canaux gauche/droit ; **Gauche/Droite** ne traite que le canal choisi. Durée, fréquence d’échantillonnage et positions des repères restent fixes.

<a id="ss-topic-effet-des-reglages-remaster"></a>

#### Effet des réglages Remaster

| Réglage | Action et résultat attendu |
| --- | --- |
| Réduction du pompage | 0–100% ; règle l’intensité des deux voies. Ce pourcentage ne promet pas de reconstruire cette proportion du mixage original. À 0%, les deux récupérations sont désactivées ; le plafond de sortie reste actif. |
| Récupération maximale | 0–9 dB ; limite la voie ordinaire avant intensité et lissage. 0 dB ne désactive que cette voie. |
| Correction des baisses brèves | 0–18 dB ; limite séparée des creux brefs avant intensité. 0 dB désactive la voie supplémentaire. Commencez à 12 dB pour les creux profonds et ajustez par petits pas. |
| Seuil de percussion | 0–12 dB ; plus bas accepte davantage d’attaques, plus haut seulement les plus fortes. Cela conditionne aussi l’intervention de la correction brève. |
| Temps de récupération | 50–500 ms ; plus long maintient la détection après une attaque. Les fenêtres rapides fixes de la voie supplémentaire ne changent pas. |
| Plafond de sortie | −12 à 0 dBFS ; défaut −1 dBFS. Si nécessaire, une atténuation constante réduit toute la plage pour respecter les crêtes d’échantillons. Les passages faibles ne sont pas automatiquement remontés au plafond. Ce n’est pas un limiteur true peak. |
| Écouter à partir de | Position en secondes dans la plage traitée ; la déplacer ne change que l’extrait écouté. |

**Une réserve de récupération de 12 dB n’est pas une hausse fixe de 12 dB.** À l’intensité de 90% du préréglage, la limite nominale rapide vaut 10,8 dB. Détection, déficit mesuré, fréquences et transitions douces peuvent réduire la correction réelle. L’atténuation finale constante affecte aussi le niveau enregistré.

<a id="ss-topic-comparer-et-appliquer-remaster"></a>

#### Comparer et appliquer Remaster

1. Ouvrez l’original. Préférez toute la forme d’onde pour garder un niveau de sortie commun. Pour une sélection, gardez environ une seconde de contexte de chaque côté et vérifiez les transitions après application.
2. Placez le curseur près d’un défaut, ouvrez Remaster et choisissez un préréglage. Utilisez **Baisses de volume brèves** si le mode fort laisse des coupures rapides.
3. Comparez **Original** et **Aperçu** avec **Égaliser le volume d’écoute de l’original et de l’aperçu** activé. Ils jouent jusqu’à huit secondes depuis la position choisie. L’égalisation utilise le niveau moyen (RMS) de l’extrait sans modifier le traitement enregistré.
4. Écoutez aussi un passage calme et la fin. Réduisez intensité ou réserve si les instruments deviennent trop brillants, si le bruit ressort ou si les accents naturels disparaissent.
5. **OK** applique ; **Annuler** laisse la forme intacte. **Ctrl+Z** restaure l’original. Comparez les modes depuis cet original : appliquer de nouveau ou **F2** retraite le son courant. Utilisez **Enregistrer sous** pour un WAV séparé.

La première écoute analyse toute la plage avec progression et annulation. Changer seulement la position ou l’égalisation de volume réutilise le calcul. L’enregistrement peut devenir globalement plus faible pour garder une réserve de crête, tandis que les baisses brèves s’entendent moins.

<a id="ss-topic-resultats-attendus-de-remaster"></a>

#### Résultats attendus de Remaster

Un passage adapté peut sembler plus régulier, avec moins d’effacement des voix et instruments derrière la batterie. Un mixage propre peut changer peu. Tous les creux ne répondent pas aux critères ; des baisses fortes ou longues peuvent rester. Des coupures musicales intentionnelles peuvent être adoucies inutilement.

Un réglage fort peut changer timbre, équilibre et dynamique naturelle, ou révéler du bruit/de la distorsion existants. Remaster ne reconstruit pas un instrument totalement absent, ne supprime pas l’écrêtage et ne restaure pas les détails MP3 perdus. Il ne remplit ni silence ni fondu avec de la musique nouvelle. Comparez à niveau moyen égal et jugez aussi le résultat musical.

| Traitement | But et différence |
| --- | --- |
| Amplifier / fondre | Applique un gain ou fondu choisi ; ne recherche pas de creux locaux. |
| Normaliser | Ajuste toute la plage par un facteur jusqu’à une crête choisie ; les écarts brefs relatifs restent présents. |
| Traitement de la dynamique | Règle le niveau selon sa courbe et ses temps de détection ; n’utilise pas les environs d’un creux bref comme référence de réparation. |
| Remaster | Repère des déficits temporaires médiums/aigus appropriés et tente une récupération locale. |

Remaster modifie la forme d’onde hors ligne et ne figure pas dans la chaîne de piste en temps réel.

<a id="ss-topic-amplitude"></a>

### Amplitude

<a id="ss-topic-amplifier-fondre"></a>

#### Amplifier / fondre

**Amplifier / fondre** règle amplification initiale/finale : 100 % inchangé, 50 % moitié, 200 % double amplitude. Verrouiller gauche/droite lie les canaux ; égaliser début/fin donne un gain constant, sinon un fondu. Le linéaire peut atteindre zéro, le logarithmique exige des extrémités positives. Les préréglages proposent ±6 dB et fondus. **Fondu d’entrée / Fondu de sortie** appliquent immédiatement un fondu linéaire. Exemple : sélectionner l'introduction, choisir un fondu d'entrée, écouter puis valider.

<a id="ss-topic-melangeur-de-canaux"></a>

#### Mélangeur de canaux

**Mélangeur de canaux** exige la stéréo. Chaque sortie combine des pourcentages L/R ; les négatifs inversent la polarité d'entrée, l'inversion de sortie celle de la somme. Les préréglages échangent, copient un côté, moyennent en mono (toujours deux canaux) ou soustraient. Le mélange peut dépasser 0 dBFS. Une sélection d'un canal change seulement sa sortie, même si les deux originaux l'alimentent.

<a id="ss-topic-traitement-de-la-dynamique"></a>

#### Traitement de la dynamique

**Traitement de la dynamique** associe dB d'entrée et de sortie. Sous la diagonale atténue, au-dessus amplifie. Cliquez/glissez les points, saisissez les valeurs dessous ; clic droit, retirer un point ou Suppr efface un point intérieur. Les extrémités restent fixes. Attaque règle la réponse aux crêtes, relâchement le retour, gain de sortie le résultat. Lier la stéréo garde une correction commune. Pour la parole, commencez à 3:1 au-dessus de −18 dB. Compresseur réduit les passages forts, gate/expanseur les faibles, limiteur les crêtes. Sans anticipation, une attaque lente laisse passer les transitoires.

<a id="ss-topic-enveloppe-de-volume"></a>

#### Enveloppe de volume

**Enveloppe de volume** dessine le gain sur 0–100 % du fragment, avec amplitude de 0–200 % (100 % neutre). Glissez ou saisissez positions/gains ; retirez les points intérieurs. Les préréglages donnent fondus, fondu aux deux bouts et creux central. L'interpolation logarithmique exige des gains positifs. Pour baisser un mot, encadrez-le de points et dessinez un creux. Ceci écrit l'audio ; les courbes de clips restent éditables séparément.

<a id="ss-topic-normaliser"></a>

#### Normaliser

**Normaliser** amène la plus haute crête à la cible (98 % par défaut) par un gain unique. Les mots ne deviennent pas égaux. Lier gauche/droite garde la balance ; délier cible chaque canal. Retirer la composante continue recentre d'abord ; le silence reste silencieux. Utile après mélange pour garder de la marge PCM.

<a id="ss-topic-inversion-de-polarite-sens-et-silence"></a>

#### Inversion de polarité, sens et silence

**Inverser la polarité** inverse la polarité, **Inverser le sens** le temps, **Silence** met à zéro sans retirer de durée. Ils s'appliquent immédiatement.

<a id="ss-topic-egalisation-et-filtres"></a>

### Égalisation et filtres

<a id="ss-topic-egaliseur-graphique"></a>

#### Égaliseur graphique

Sous **Filtres**, **Égaliseur graphique** comporte dix bandes d'octave, 31,5 Hz–16 kHz, chacune −24…+24 dB. Les bandes inutilisables à basse fréquence d'échantillonnage sont désactivées. Plat remet à zéro ; renfort des basses, présence vocale et sourire léger offrent des départs. Le graphe combine bandes et gain de sortie (affichage −36…+36 dB). Les hausses peuvent dépasser 0 dBFS : baissez la sortie avant export PCM.

<a id="ss-topic-egaliseur-parametrique"></a>

#### Égaliseur paramétrique

**Égaliseur paramétrique** propose cinq bandes en cloche et deux plateaux grave/aigu, activables séparément. Fréquence choisit centre/transition, gain −24…+24 dB, un Q élevé resserre la cloche. Les plateaux ont une transition douce fixe sans Q. Traitez une résonance par une cloche étroite négative, la couleur générale par une cloche large/un plateau et peu de gain. Plat/réinitialiser remet les gains à zéro ; clarté vocale/chaleur sont des départs.

<a id="ss-topic-filtres"></a>

#### Filtres

**Filtres** propose passe-haut (grondement, départ 80 Hz), passe-bas (adoucir les aigus, 8 kHz), passe-bande et réjecteur. Passe-haut/bas utilisent Butterworth 12/24/36/48 dB/oct, environ −3 dB à la coupure ; une pente raide peut résonner davantage. Passe-bande/réjecteur utilisent Q. Téléphone est un passe-bande large ; les réjecteurs 50/60 Hz n'enlèvent pas les harmoniques du ronflement. Réinitialiser restaure le grondement. Les filtres gardent la durée et leur phase causale naturelle.

**Transition de sélection**, initialement 5 ms, réglable 0–100 ms, mélange à l’intérieur des limites d’une sélection partielle. Échantillons aux bords et audio extérieur restent exacts. Une sélection très courte peut être entièrement transition. L’audio précédent prépare l’état par blocs, selon les pôles jusqu’à 60 s. Avec 0 ms, ancien traitement direct depuis un état vide. Un fichier entier garde le filtre continu ordinaire. La courbe montre le gain stationnaire ; le mélange aux bords est distinct. Ce n’est pas une EQ à phase linéaire/nulle : les fréquences peuvent réagir à des instants différents. Un filtre très étroit et grave peut atteindre la limite de contexte ; sélectionnez plus ou le fichier entier. Les inserts temps réel gardent leur état sans transition de sélection.

<a id="ss-topic-delai-echo-et-reverberation"></a>

### Délai, écho et réverbération

<a id="ss-topic-effets-de-retard-retard"></a>

#### Effets de retard → Retard

**Effets de retard → Retard** ajoute une copie après 1–2 000 ms. Gauche/mono règle le premier délai ; déliez pour un temps droit distinct. Préréglages : simple 250 ms, slapback 80 ms, doublage 25 ms, élargissement stéréo.

<a id="ss-topic-echo"></a>

#### Écho

**Écho** répète par réinjection (0–95 %) ; plus elle est haute, plus le déclin dure. L'amortissement aigu assombrit les répétitions réinjectées, pas la première copie. Ping-pong alterne en stéréo. Écho chaud/longues répétitions sont des départs ; une forte réinjection peut accumuler les niveaux.

<a id="ss-topic-reverberation"></a>

#### Réverbération

**Réverbération** règle taille de pièce (espacement des réflexions), déclin RT60 approximatif (0,1–60 s), prédélai (0–250 ms) avant l'effet, amortissement aigu et largeur stéréo (0 même effet des deux côtés, 100 pleine largeur ; désactivée en mono). Petite pièce, studio, grande salle et ambiance longue varient espace/déclin. Pour la parole, commencez avec peu d'effet, déclin court et un peu de prédélai. Réverbération algorithmique, sans modèle exact de salle.

Son direct et effet s’additionnent ; gain de sortie (−24…+24 dB) donne de la marge sans limitation automatique. La durée reste fixe par défaut. Activez **Ajouter une queue après la sélection** et **Durée de queue automatique** pour suivre le son restant. Décochez Automatique pour une durée manuelle de 0,01–600 s. Le déclin de réverbération (RT60 approximatif) va de 0,1–60 s. Les préréglages désactivent l’ajout ; réglez-le ensuite.

L’automatique vérifie l’état mémorisé de l’effet et garde les échos tardifs malgré un intervalle silencieux. Vérification par pas de 100 ms, fin calme puis fondu des dernières 10 ms. Seuil environ 90 dB sous la crête de référence, plancher −140 dBFS ; choisissez manuel pour garder une queue extrêmement faible. Silence ou 0% effet n’ajoute pas de durée vide. État encore audible à 600 s : message et conservation de l’original/annulation ; baissez réinjection/déclin ou choisissez manuel.

Seuls les canaux choisis se décalent. Les deux décale les repères communs suivants ; Gauche/Droite les garde et complète l’autre canal si besoin. Un aperçu dans la queue peut d’abord en déterminer la fin, tout en restant le début exact du traitement complet. Les gros résultats grandissent sur disque sans réserver 600 s ; annuler n’applique aucun résultat partiel. La queue des pistes en temps réel garde sa limite distincte de 60 s.

<a id="ss-topic-reduction-du-bruit-et-declics"></a>

### Réduction du bruit et déclics

Sélectionnez du bruit seul (demi-seconde à plusieurs secondes), choisissez **Capturer le profil de bruit**, puis sélectionnez l'audio à nettoyer et rouvrez **Réduction du bruit**. La capture dans la fenêtre fonctionne aussi sans changer l'audio. Le profil moyenne au maximum les 30 premières secondes. Durée minimale selon l'échantillonnage ; fréquence/canaux doivent correspondre. Pour un canal stéréo, le canal de profil correspondant est utilisé. Enregistrer/charger un profil utilise `.ssnoise`, un spectre sans prise audio. Réutilisez avec une installation correspondante.

<a id="ss-topic-estimation-du-bruit-profil-de-bruit-fixe"></a>

#### Estimation du bruit → Profil de bruit fixe

**Estimation du bruit → Profil de bruit fixe** convient au souffle ou à une ventilation stable. **Suivi adaptatif du bruit** part du même profil de bruit seul et suit les variations du niveau et du spectre. Les deux modes exigent un profil compatible ; un profil silencieux n’a aucun effet. Le profil enregistré reste inchangé.

**Temps de suivi du bruit**, 0,05–5 secondes, est actif seulement en adaptatif. Un temps court réagit plus vite mais peut apprendre des sons tenus comme du bruit ; un temps long est plus prudent. Commencez à 0,15 s. **Protection des détails**, 0–100 %, garde plus de sons faibles et laisse davantage de fond ; valeur initiale 50 %. Fixe avec 0 % reprend l’atténuation précédente. Les détails absents de la source ne sont pas recréés. Réduction maximale 0–36 dB (commencez à 6–12 dB ; 0 conserve exactement l’original), sensibilité règle ce qui est considéré comme bruit et lissage ralentit une suppression plus forte après les sons. Lier la stéréo garde la balance ; sinon les canaux sont traités séparément.

Préréglages : **Doux** 6 dB/65 % de protection, **Équilibré** 12 dB/50 %, **Fort** 24 dB/15 %, **Bruit de fond variable** adaptatif 12 dB/50 % à 0,15 s et **Détails délicats** fixe 6 dB/90 %. Les trois premiers sont également fixes. Pour une voix devant un ventilateur devenant plus fort, capturez le ventilateur seul, sélectionnez la voix et essayez Bruit de fond variable. Augmentez la protection si des mots faibles ou des fins disparaissent. Allongez le temps ou choisissez Fixe pour les sons tenus. **Garder uniquement le bruit retiré** permet d’écouter les pertes ; désactivez avant de confirmer un résultat nettoyé.

Le suivi peut confondre un son utile avec le bruit, surtout un son large et tenu, un niveau très faible ou un profil contenant parole/musique. Il ne sépare pas les voix et ne recrée pas d’informations perdues. Aperçu et traitement complet ont le même début. Durée, repères et canal stéréo non choisi restent fixes. Annuler restaure l’original ; F2 répète mode, temps, protection et profil. Les gros fichiers utilisent une mémoire de travail bornée ; une annulation n’applique aucun résultat partiel.

<a id="ss-topic-suppression-des-clics"></a>

#### Suppression des clics

**Suppression des clics** relie les échantillons intacts autour d'impulsions courtes isolées. Un multiplicateur de seuil élevé est prudent ; un saut minimal dBFS bas trouve des clics faibles. Largeur maximale 0,02–2 ms. Prudent, petits clics et clics larges sont des départs. Écoutez les percussions : leurs attaques ressemblent aux défauts. Longs craquements, écrêtage et bords endommagés nécessitent un autre traitement.

<a id="ss-topic-temps-et-hauteur"></a>

### Temps et hauteur

<a id="ss-topic-duree-hauteur-etirement-temporel"></a>

#### Durée/hauteur → Étirement temporel

**Durée/hauteur → Étirement temporel** change la durée (25–400 %) sans changer la hauteur : 200 % double, 50 % divise par deux. Les champs de tempo calculent ancien/nouveau BPM (120→100 donne 120 %), sans détection automatique. Avec Les deux, les repères suivent l’échelle et la suite se décale. Avec Gauche/Droite, seul ce canal se décale ; les repères communs restent en place.

<a id="ss-topic-transposition"></a>

#### Transposition

**Transposition** varie −24…+24 demi-tons sans changer durée/repères ; ±12 vaut une octave, 0,01 demi-ton un cent. Préserver les formants aide la voix ; comparez sur les instruments.

Fin (défaut) et Rapide utilisent Rubber Band hors ligne. La stéréo est traitée ensemble ; les extrêmes peuvent sembler artificiels. Pour une vraie modification, utilisez au moins 50 ms et 64 échantillons. Le neutre rend exactement l'original, la sortie s'arrondit aux échantillons. L'aperçu analyse toute la sélection avant huit secondes maximum ; les fichiers longs demandent temps et mémoire d'analyse. La progression est annulable. Pour un clip, modifiez une copie puis réappliquez ; les courbes se redimensionnent, les clips suivants ne bougent pas automatiquement.

<a id="ss-topic-effets-speciaux"></a>

### Effets spéciaux

<a id="ss-topic-special-distorsion"></a>

#### Spécial → Distorsion

**Spécial → Distorsion** offre écrêtage doux (saturation arrondie), dur (coupure nette), repliement des crêtes et réduction de bits (2–16 bits). Préamplification 0–36 dB, plafond 10–100 %, mélange original/traité, sortie −24…+24 dB. Le plafond ne limite que la partie traitée, pas le direct ni la sortie totale. Chaleur douce, crunch, repliement et bits sont des départs. Haute qualité suréchantillonne contre le repliement spectral (souvent 4×, adapté aux hautes fréquences) et traite tout même pour l'aperçu ; standard est plus rapide/rude. Durée/repères fixes, silence conservé.

<a id="ss-topic-convolution"></a>

#### Convolution

**Convolution** applique une réponse impulsionnelle WAV de filtre, enceinte ou espace acoustique. Choisissez-la, réglez direct/effet et écoutez. Mono fonctionne par canal ; une réponse stéréo exige une entrée stéréo et utilise le canal sélectionné correspondant. Une autre fréquence est convertie ; réponse limitée après conversion à 10 secondes et 524 288 échantillons, fichier à 32 Mio. Les réponses vides ou silencieuses sont refusées. Aucun fondu supplémentaire de queue. Normaliser l'énergie met à l'échelle les deux canaux ensemble ; désactivez pour une réponse calibrée. Direct 0 %, effet 100 % donne un filtre pur. Garder la queue complète ajoute la durée de réponse moins un échantillon et décale la suite. Sinon durée fixe. Gardez le fichier intact pour F2 ; s'il change/manque, sélectionnez-le de nouveau.

<a id="ss-topic-8-generer-analyser-et-convertir"></a>

## 8. Générer, analyser et convertir

**Générer → Tonalités** insère une sinusoïde au curseur ou remplace la sélection avec durée, fréquence Hz et amplitude % choisies. Essayez 440 Hz à faible niveau. **Générer → Silence** insère/remplace une durée de silence ; **Effets → Silence** conserve la durée existante.

**Analyser → Analyse fréquentielle / Alt+Z** affiche fréquences et dBFS des canaux/intervalle choisis (sinon toute la prise). Pour les longs passages, une partie centrale limitée est utilisée, avec fenêtre de Hann et puissance moyenne des canaux. Fréquence/niveau de crête sont indiqués dessous. Sélectionnez un son court pour l'étudier ; ce n'est pas un spectromètre continu. Fermer ne change rien.

**Édition → Convertir la fréquence d’échantillonnage** convertit toute la forme d'onde en Hz choisis, conservant hauteur/durée avec arrondi aux trames (au moins une). Curseur/sélection suivent les mêmes instants. Annuler restaure audio et fréquence. Ceci change le document ; la conversion automatique de lecture change seulement le flux de sortie.

<a id="ss-topic-9-multipiste-et-automation"></a>

## 9. Multipiste et automation

Créez une session avec fréquence/nombre de pistes, importez des WAV par menu/bouton ou déposez-les depuis le gestionnaire. Les fréquences sont converties ; plusieurs fichiers occupent des pistes successives. **Fenêtre → Insérer la forme d’onde dans le multipiste** insère la forme ouverte. Ajouter/retirer agit sur la piste choisie ; annuler récupère le contenu supprimé. Les noms sont éditables. Muet coupe, solo limite aux pistes solo ; muet reste prioritaire. Pan −100 gauche, 0 centre, +100 droite ; en stéréo il atténue un côté sans copier les canaux.

En **Déplacer les clips**, glissez le centre pour déplacer, les bords pour rogner ; la source est conservée pour rallonger. Le vide de la ligne du temps sélectionne un intervalle de lecture. **Dupliquer le clip / Ctrl+D** partage la source ; **Supprimer le clip / Suppr** retire le clip, pas son fichier source. Clic droit ouvre les commandes. **Propriétés du clip** règle nom, bornes temporelles/source (secondes), gain, pan, fondus et muet ; les fondus doivent tenir ensemble dans le clip. Annuler le garde intact.

**Courbe de volume** et **Courbe de panoramique** dessinent dans les clips. Cliquez pour ajouter, glissez pour déplacer, clic droit/double-clic ouvre trames/valeurs exactes, retirer/Suppr enlève le point choisi, réinitialiser remet au neutre. Échap annule le glissement. Volume : bas 0 %, milieu 100 %, haut 200 %, multipliant gains et fondus. Pan : haut droite, milieu neutre, bas gauche, ajouté au pan clip/piste. Centrez le pan ordinaire pour une traversée complète. Les points suivent la source lors de déplacements/rognages et sont sauvegardés. Revenez au déplacement de clips ensuite.

Double-clic ou **Édition une copie en forme d’onde** ouvre une copie pour effets hors ligne. **Fenêtre → Appliquer la forme d’onde au clip** réapplique explicitement ; changer de vue seul ne suffit pas. Annuler dans la session restaure audio/courbes. La fréquence est reconvertie, les courbes suivent la nouvelle durée, les clips suivants restent fixes : vérifiez les chevauchements. **Mixer la session / Mixer** exporte toute la session, indépendamment de la sélection, avec muet/solo, gains/pan, courbes, effets et queues. Enregistrer la session garde le projet éditable. Ces réglages changent pendant la lecture ; annuler/changer de vue l'arrête.

<a id="ss-topic-10-effets-de-piste-plug-ins-et-enregistrement"></a>

## 10. Effets de piste, plug-ins et enregistrement

Ouvrez **FX** près d’une piste ou **Effets → Effets de piste**. Ajoutez un effet, choisissez réglages/préréglage et confirmez avec OK ; Appliquer modifie sans fermer. Modifier/double-clic rouvre les réglages. Monter/descendre change l’ordre, la coche contourne, Supprimer retire. Les changements ont Annuler/Rétablir. Au plus seize effets agissent après gain/courbes/fondus du clip, avant volume/pan de piste. Le mono devient stéréo. La queue après dernier clip ajoute 0–60 secondes. Lecture et mixage utilisent la même chaîne sans modifier les sources.

Les chaînes proposent amplification fixe, mélangeur, dynamique, EQ graphique/paramétrique, filtres, délai, écho, réverbération, inversion et plug-ins externes. Appliquer actualise à l’écoute ; l’audio déjà tamponné garde les anciens réglages. Redémarrage, recherche et changement de contournement vident la mémoire d’effet. Normalisation, restauration, temps/hauteur, distorsion et convolution restent des modifications via Modifier une copie en forme d’onde. Utilisez la courbe de volume pour varier le gain du clip.

<a id="ss-topic-vst3-lv2-et-ladspa"></a>

### VST3, LV2 et LADSPA

Installez un **effet audio Linux natif 64 bits**. Dans Effets de piste, choisissez **Plug-in externe → Ajouter**, le format, puis **Ajouter un plug-in**. Sélectionnez un ensemble `.vst3`, `.lv2` ou une bibliothèque LADSPA (`.so`). Les effets d’un ensemble apparaissent séparément. Choisissez l’effet, cherchez un paramètre et changez sa position normalisée 0–100 % : 50 % ne signifie pas forcément demi-volume. Les paramètres discrets ont des pas ; ceux en lecture seule restent fixes. Appliquer permet l’écoute sur la piste ; OK confirme/ferme.

**Ouvrir la fenêtre du plug-in** ouvre un éditeur VST3/LV2 compatible. Ses paramètres et son état enregistrable sont repris à la confirmation. Les fenêtres propres nécessitent **X11 ou XWayland**. Les commandes générales restent disponibles si l’éditeur manque ou n’est pas compatible ; LADSPA les utilise toujours. Les éditeurs LV2 nécessitant un adaptateur GTK/Qt ne sont pas intégrés.

VST3 accepte un bus stéréo d’entrée/sortie en float32. LV2/LADSPA acceptent les effets mono/stéréo avec autant d’entrées que de sorties ; les effets mono ont une instance par canal stéréo. Instruments MIDI, sidechains supplémentaires, VST2 et plug-ins Windows ne sont pas pris en charge. Les fonctions/ports LV2 requis mais indisponibles sont signalés ; le traitement MIDI/Atom est absent. Un état LV2 nécessitant des fichiers externes ne peut pas être sauvegardé complètement et déclenche un message : choisissez un effet dont l’état est autonome.

Chaque plug-in tourne dans un processus isolé. Plantage, délai dépassé ou audio invalide arrêtent la lecture en préservant l’audio enregistré. Les projets gardent paramètres et au plus 1 Mio d’état par effet. Installez séparément le plug-in, ses bibliothèques/échantillons externes. Sur une autre machine, ajoutez la même version. Les versions absentes/modifiées sont signalées ; lecture/export nécessitent l’effet correspondant ou un contournement volontaire.

<a id="ss-topic-compensation-du-retard-des-plug-ins"></a>

### Compensation du retard des plug-ins

Le retard de traitement algorithmique déclaré est compensé par piste en lecture et mixage. Les retards d’une chaîne s’additionnent ; les changements de réglage/contournement actualisent le traitement. Positions et durée du mix restent identiques. Écho musical, prédélai et réverbération restent audibles. La compensation dépend d’une déclaration correcte et est limitée à dix secondes par piste. Un retard invalide ou changeant continuellement déclenche un message.

<a id="ss-topic-accompagnement-et-synchronisation"></a>

### Accompagnement et synchronisation

Placez l’accompagnement sur des pistes, choisissez piste cible et curseur. Appuyez sur **R**, choisissez entrée et destination nouveau clip, puis **Lire les pistes existantes pendant l’enregistrement**. Les pistes jouent avec leurs effets ; l’entrée n’est pas renvoyée aux haut-parleurs. **P** suspend/reprend les deux ; **Arrêter/Échap/Espace/R** conserve la prise en une étape d’annulation. Rejeter supprime seulement cette prise. Une panne d’appareil/plug-in conserve l’audio capturé.

**Synchronisation automatique** relie le placement à l’horloge de lecture et mesure l’écart entre horloges d’entrée/sortie. Une mesure assez longue et fiable corrige légèrement la durée après Arrêter. Une mesure courte/instable n’étire pas la prise. La correction de durée nécessite plus de dix secondes de mesures d’horloge utilisables. Elle ne mesure pas le trajet physique entrée/sortie.

Pour ce trajet, choisissez **Options → Étalonner l’enregistrement**, ou le bouton d’étalonnage du dialogue. Choisissez les mêmes appareils, fréquence, mode mono/stéréo, premier canal d’entrée et tampon que pour enregistrer. Reliez sortie et entrée avec un câble de bouclage adapté. Un microphone près d’un haut-parleur inclut aussi le délai acoustique. Commencez à faible niveau. **Démarrer l’étalonnage** joue des impulsions faibles pendant environ six secondes, sans retour de l’entrée. Seul un résultat fiable est enregistré ; silence, saturation, ambiguïté ou instabilité conservent un ancien bon profil. Vérifiez avec une courte prise ; refaites l’étalonnage après changement d’appareils/réglages.

La synchronisation automatique utilise le profil correspondant. Sans profil, la synchronisation d’horloge fonctionne, mais un retard physique peut rester. Sinon, désactivez l’automatisme et utilisez **Décalage de position d’enregistrement** : négatif avance, positif retarde ; −15 ms corrige une prise en retard de 15 ms. Les corrections automatique et manuelle s’excluent.

<a id="ss-topic-punch-in-out"></a>

### Punch-in/out

Choisissez une piste cible et une plage sur la règle multipiste ou via **Édition → Définir la sélection**. Choisissez **Options → Punch-in/out** ou **Maj+R**. Réglez entrée, synchronisation, **Prélecture** (2 s) et **Fondu enchaîné** (5 ms). La sélection fixe les limites d’enregistrement ; l’accompagnement est activé.

L’entrée est préparée avant la lecture. L’original joue pendant la prélecture. Dans l’intervalle choisi, seule la piste cible est coupée pendant la capture de remplacement ; les autres continuent. Après une courte finalisation de synchronisation, l’enregistrement s’arrête automatiquement. Seul l’audio corrigé dans la sélection devient un nouveau clip.

Les fondus mélangent ancien/nouveau dans les limites, au plus 100 ms. L’audio extérieur reste intact. Les clips originaux gardent leurs sources, la zone punch étant recouverte. Ctrl+Z restaure tout en une étape. Sur l’ancien clip, **Restaurer l’audio recouvert** retire toutes ses zones de recouvrement ; supprimez/coupez la nouvelle prise pour éviter d’entendre les deux. Un arrêt anticipé garde seulement la partie capturée dans l’intervalle. Avant l’intervalle, il ne modifie pas la session ; la prise brute reste dans **Fichier → Récupérer le travail**. La récupération d’une prise non confirmée propose l’audio brut, avec prélecture/fin, à placer manuellement. Les zones punch terminées sont sauvegardées dans le projet et la récupération après plantage.

**Enregistrer la session / Enregistrer la session sous** garde audio, clips, courbes, chaînes, état des plug-ins et zones punch. Ouvrir une session les restaure ; le mixage exporte WAV/MP3 avec les mêmes effets. Gardez le projet pour les pistes séparées. Les projets nouvellement enregistrés nécessitent SoundSausage **0.26.0 ou ultérieur** ; les anciennes versions de projet restent lisibles. Un plug-in absent n’empêche pas l’ouverture/récupération des sources.

<a id="ss-topic-11-enregistrer-avec-accompagnement"></a>

## 11. Enregistrer avec accompagnement

Placez l'accompagnement sur des pistes, choisissez une autre piste cible et le curseur. Pressez **R**, choisissez entrée/nouveau clip et activez « Lire les pistes existantes pendant l'enregistrement ». Pistes et effets partent du curseur ; l'entrée n'est pas renvoyée aux haut-parleurs. **P** pause/reprend les deux ; **Arrêter/Échap/Espace/R** arrête et conserve la prise en une annulation. L'enregistrement peut continuer après l'accompagnement ; une durée maximale arrête les deux. Abandonner retire seulement la nouvelle prise. Une panne conserve les échantillons capturés. Les éditions sont verrouillées.

Le décalage de position déplace le clip inséré : négatif plus tôt, positif plus tard. Pour une prise retardée de 15 ms, essayez −15 ms. Enregistrez un clic connu via le trajet entrée/sortie réel, comparez les positions, saisissez la différence et vérifiez une seconde prise. Recalibrez après changement de périphérique/tampon. L'audio avant zéro est rogné à l'insertion. Le décalage est mémorisé ; la calibration automatique, la correction de dérive, la compensation des plug-ins et le punch-in/out sont décrits au chapitre précédent. Testez brièvement avant une longue session.

<a id="ss-topic-12-raccourcis-favoris-et-depannage"></a>

## 12. Raccourcis, favoris et dépannage

**Favoris** propose répétition, normalisation et fondus ; les listes personnalisées ne sont pas disponibles. **Fenêtre** change de vue et transfère formes/clips. Voici les principaux raccourcis. Pendant la saisie, les touches appartiennent au champ ; cliquez sur la forme/ligne du temps avant les commandes de transport/édition.

| Touches | Action |
| --- | --- |
| Ctrl+N / Ctrl+O | Nouveau / ouvrir dans la vue active |
| Ctrl+S / Ctrl+Maj+S | Enregistrer / sous |
| Ctrl+Alt+N / Ctrl+Alt+O / Ctrl+Alt+S | Nouvelle / ouvrir / enregistrer session |
| Ctrl+W / Ctrl+Q | Fermer document / quitter |
| Ctrl+Z / Ctrl+Maj+Z | Annuler / rétablir |
| Ctrl+X / Ctrl+C / Ctrl+V | Couper / copier / coller |
| Ctrl+M / Ctrl+T / Suppr | Coller en mixant / rogner / retirer |
| Ctrl+A / F4 | Toute la durée / passages par zéro |
| Alt+B / Alt+L / Alt+R | Deux canaux / gauche / droite |
| Espace / P / Échap / R | Lecture-arrêt / pause / arrêt / enregistrer |
| Début / Fin / + / − | Début / fin / zoom avant / arrière |
| Ctrl+0 / Ctrl+Maj+A | Zoom total / sélection |
| Ctrl+D / Tab / F11 | Dupliquer clip / vue / plein écran |
| F1 / F2 / Alt+Z | Manuel / répéter effet / analyse fréquentielle 

Pas d'entrée : vérifiez périphérique/canal et niveau micro Linux, reconnectez puis recommencez. Pas de sortie : routage, volume, muet/solo et matériel audio. Distorsion/crêtes rouges : baissez le gain cumulé, normalisez avant PCM ; collage mixé et clips superposés s'additionnent. Collage refusé : vérifiez le nombre de canaux du presse-papiers. Effet désactivé : ouvrez une forme/copie ; le mélangeur exige la stéréo ; choisissez les canaux à modifier. Points au lieu des clips : choisissez déplacer les clips. Disque plein : libérez de la place sans effacer de fichiers de travail actifs. Récupération endommagée : les originaux restent ; supprimez la copie seulement si inutile.

En développement : favoris personnalisés. Chaînes temps réel, Linux VST3 et accompagnement sont disponibles comme décrit. Enregistrez avant de quitter. Actualités : [SoundSausage](https://github.com/rene-timmermans/SoundSausage).
