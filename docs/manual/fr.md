# SoundSausage — manuel

Version 0.21.0. Un éditeur audio intuitif et simple à utiliser, avec tous les outils là où vous les attendez. Ce manuel décrit les fonctions disponibles, les effets et leurs limites pratiques.

## 1. Langue et aide

Dans **Options → Langue**, choisissez Nederlands, English, Deutsch, Français ou Español. Menus, fenêtres, conseils et manuel ouvert changent immédiatement. Le choix est mémorisé au prochain démarrage. Les noms de fichiers, pistes et plug-ins conservent leur orthographe.

**Aide → Manuel** ou **F1** ouvre ce manuel hors ligne à côté de l'éditeur. **Ctrl+F** active la recherche ; **F3** trouve l'occurrence suivante et **Maj+F3** la précédente, avec retour au début ou à la fin. Seuls les liens web explicitement ouverts nécessitent Internet. **À propos** indique version, auteur, licence, site et composants.

## 2. Démarrage rapide et espace de travail

L’icône du programme sur fond violet apparaît dans les barres de titre et la barre des tâches. **Aide → À propos** affiche la mascotte détourée à côté des informations du programme.

Ouvrez un WAV ou MP3 par **Fichier → Ouvrir**. **Espace** démarre ou arrête la lecture. Sélectionnez un passage, choisissez **Effets → Amplitude → Normaliser**, écoutez avec **Écouter**, puis validez par **OK**. **Ctrl+Z** annule. **Enregistrer sous** garde un résultat séparé. Pour plusieurs prises, créez une **Nouvelle session multipiste**, importez les WAV ou MP3 puis utilisez **Mixer**.

**Édition la forme d’onde** modifie une prise ; **Vue multipiste** combine des clips. Passez de l'une à l'autre avec **Tab**, les boutons supérieurs ou **Affichage** ; les deux documents restent disponibles. Les infobulles expliquent les boutons. **Afficher le texte des barres d’outils** ajoute leur texte, **Options → Afficher la barre d’état** affiche ou masque la fine ligne d’information tout en bas, sous les indicateurs de niveau. Elle indique l’état de lecture et les détails du fichier ; le choix est conservé au prochain démarrage. **F11** bascule le plein écran. L'horloge suit l'audio ; les champs de sélection indiquent début, fin et durée, ceux de vue l'intervalle visible. Des crêtes rouges signalent une surcharge ; une étoile indique des modifications non enregistrées.

Les fenêtres et les échelles des graphiques s’adaptent à la taille de police du bureau et à la langue choisie. Si un formulaire dépasse l’écran, faites défiler ses réglages ; les boutons de validation et d’annulation restent accessibles.

Deux fines lignes horizontales marquent le bord inférieur du canal gauche et le bord supérieur du canal droit. Elles s’arrêtent aux limites du graphique, également pendant l’enregistrement en direct.

## 3. Fichiers, projets et récupération

**Nouveau** crée une forme d'onde mono ou stéréo à la fréquence choisie. **Ouvrir** lit les WAV et MP3. **Enregistrer** actualise le fichier ; **Enregistrer sous** choisit nom/encodage ; **Enregistrer la sélection** écrit uniquement l'intervalle et les canaux sélectionnés. L'export WAV propose PCM 8/16/24/32 bits et float32. PCM16 facilite l'échange ; float32 conserve aussi les crêtes internes au-delà de 0 dBFS. Augmenter la résolution ne restitue pas les détails perdus. Un ancien WAV 32 bits ambigu demande une interprétation PCM ou flottante historique ; annuler le laisse intact.

Textes WAV, repères et étiquettes sont conservés. Les repères suivent les éditions, collages et exports de sélection ; le titre cible est gardé. Les champs propres aux enregistreurs restent inchangés, sans recalcul après effet. Les métadonnées supplémentaires sont limitées à 16 Mio : une entrée excessive est refusée ; les omissions à l'export demandent confirmation. Le mixage ne fusionne pas les marqueurs des sources. Les gros exports utilisent RF64 si nécessaire.

**Nouvelle session multipiste**, **Ouvrir une session**, **Enregistrer la session** et **Enregistrer la session sous** gèrent les projets éditables. Un projet SoundSausage (`.celp`) contient audio, clips, courbes, réglages de pistes, ordre/contournement/queues d'effets et paramètres VST3. Gardez le projet en plus du WAV final pour retrouver les pistes séparées. Les anciens projets SoundSausage restent lisibles ; les projets nouvellement enregistrés nécessitent l’application 0.19.0 ou ultérieure. L'import historique `.ses` est limité ; poursuivez dans un nouveau projet SoundSausage.

**Fermer / Ctrl+W** ferme la forme d'onde courante ; en multipiste, **Fermer la session** ferme la session. Choisissez enregistrer, abandonner ou annuler. L'autre vue et le presse-papiers restent disponibles. **Quitter / Ctrl+Q** quitte en vérifiant les modifications non enregistrées.

Les fichiers longs sont traités par blocs sur disque, sans l'ancienne limite de 128 Mio. Prévoyez de la place pour sources, résultats et annulations. Les sessions sont limitées à 24 heures et 32 pistes. Les opérations longues affichent progression et annulation ; annuler conserve audio, sélection, historique et ancienne cible d'export. Un effet appliqué constitue une annulation.

Après une fermeture imprévue, restaurez, supprimez ou reportez la dernière sauvegarde de récupération. **Fichier → Récupérer le travail** ouvre les copies conservées. Les originaux restent intacts ; forme d'onde, session, canaux, clips, courbes et effets reviennent, mais l'historique d'annulation repart à zéro. Les éditions validées sont sauvegardées, curseur/sélection environ chaque seconde. Les instances actives sont ignorées. Enregistrer ou fermer normalement efface la copie propre à l'instance. Gardez vos sauvegardes ; une erreur disque peut laisser un état plus ancien.

### MP3 et WAV

Ouvrez les MP3 par **Fichier → Ouvrir**, importez-les en multipiste ou déposez-les sur la chronologie. Sélection, édition et effets travaillent sur l’audio décodé. **Enregistrer sous**, **Enregistrer la sélection** et **Mixer** proposent WAV et MP3 ; l’extension suit le format choisi. Enregistrer un MP3 existant utilise l’encodage MP3 choisi ; Enregistrer sous permet une copie WAV.

MP3 propose 128, 192, 256 et 320 kb/s. Un débit supérieur occupe plus de place et conserve généralement plus de détails. MP3 est avec perte : recomprimer peut supprimer d’autres détails. WAV évite une compression MP3 supplémentaire sans restaurer les informations perdues. Choisissez WAV float32 pour poursuivre l’édition, PCM16 pour l’échange. L’export MP3 utilise la fréquence la plus proche parmi 32 000, 44 100 et 48 000 Hz, à durée égale ; le document garde sa fréquence. Ces fréquences conviennent aux quatre débits MP3 proposés ; à des fréquences plus basses, l’encodeur peut utiliser un débit inférieur à celui demandé. Le minimum de 2 ms évite que de très courts fragments deviennent plus longs après décodage MP3. Utilisez WAV pour les sélections de moins de 2 ms.

### Métadonnées MP3 après modification

Titre, artiste, album, commentaires et pochettes sont conservés, y compris via WAV et les projets SoundSausage. La durée est actualisée. Les tags ordinaires et identifiants existants restent liés au fichier de destination.

Les **chapitres** suivent automatiquement les modifications. Supprimer avance les chapitres suivants ; insérer les retarde. Rogner et exporter une sélection conserve les chapitres qui la recoupent, avec des temps relatifs au fragment gardé. Les chapitres vides ou entièrement supprimés disparaissent ; la table des matières conserve des références valides. Coller reprend les noms et la hiérarchie des chapitres du fragment tout en conservant les tags généraux de destination. L’étirement temporel adapte les limites ; le changement de fréquence d’échantillonnage conserve les temps en millisecondes. Annuler restaure aussi les métadonnées d’origine.

La précision des chapitres est d’une milliseconde ; un reste arrondi à une durée nulle disparaît. Inverser reflète les chapitres entièrement dans la plage. Un chapitre partiellement inversé qui décrirait des morceaux audio séparés est supprimé ; un chapitre contenant toute la plage inversée reste présent.

Les **mesures** peuvent devenir obsolètes après modification audio. Les valeurs reconnues ReplayGain, R128, MP3Gain et de crête, les empreintes, ajustements de volume relatif et anciennes informations d’encodage sont supprimés. Les informations temporelles non prises en charge, notamment paroles synchronisées, anciens index de recherche et positions de synchronisation, disparaissent aussi. ReplayGain n’est pas recalculé. Un changement de tempo supprime la valeur BPM existante ; un changement de hauteur supprime la tonalité existante. Les autres modifications conservent ces deux valeurs. Les paroles ordinaires sans horodatage et les champs privés inconnus restent inchangés. Réencoder en MP3 supprime également anciennes mesures et positions de fichier, puisque la compression modifie le son et la structure. Les informations d’encodage proviennent du nouveau fichier réel.

**WAV vers MP3 :** les champs INFO pris en charge pour titre, artiste, album, genre, date, numéro de piste, droits d’auteur et commentaires sont transférés. Les valeurs ID3 existantes sont prioritaires. Les champs incompatibles, données INFO mal formées et valeurs contradictoires sont signalés avant export. **Non** annule et préserve une destination existante ; **Oui** continue avec les omissions indiquées. Les tags ID3 supplémentaires d’un WAV sont également signalés avant omission. Les anciennes informations de logiciel sont remplacées par celles du nouvel encodeur. Les marqueurs WAV et autres données incompatibles nécessitent également ce choix.

Les métadonnées supplémentaires restent limitées à 16 Mio. Les données ID3 WAV illisibles restent conservées telles quelles ; l’export MP3 signale une erreur et préserve la destination. Le mixage ne fusionne pas les métadonnées de toutes les pistes. Les longues conversions affichent la progression et sont annulables ; prévoyez de l’espace pour la conversion et l’édition.


## 4. Lecture, zoom et matériel audio

**Espace** démarre/arrête, **P** met en pause/reprend, **Échap** arrête. La sélection définit la lecture ; sinon elle part du curseur. **Boucle** répète, avec une éventuelle courte transition. **Début/Fin** vont aux extrémités ; les boutons sautent de cinq secondes. Naviguer ou appliquer une édition arrête la lecture. **Zoom avant / Zoom arrière**, **Ctrl+molette**, molette et barre horizontale déplacent la vue. **Vue complète / Ctrl+0** montre tout ; **Zoom sur la sélection / Ctrl+Maj+A** cadre la sélection. Leurs icônes diffèrent. De près les échantillons sont reliés ; de loin les crêtes min/max par colonne sont conservées.

Dans **Options → Périphériques audio**, choisissez une sortie ou **Valeur par défaut du système** ; ce choix mémorisé sert aussi à l'aperçu. Le tampon vaut 100 ms par défaut : plus grand, il tolère les interruptions ; plus petit, il répond plus vite. Le tampon réel peut différer. Changer arrête lecture/aperçus. Si le périphérique disparaît, reconnectez-le ou choisissez une sortie puis relancez. Vérifiez volume système, routage, muet et solo. La conversion pour la sortie ne change pas l'enregistrement.

## 5. Enregistrer

Branchez un micro/interface, choisissez l'entrée dans **Périphériques audio**, puis pressez **R**. Réglez entrée, destination, mono/stéréo, premier canal et durée maximale. Une nouvelle forme d'onde reste séparée ; insérer au curseur/remplacer la sélection modifie une forme existante ; le multipiste ajoute un clip sur la piste choisie au curseur. Une entrée mono peut alimenter les deux canaux stéréo. La forme existante détermine fréquence/canaux ; une autre fréquence d'entrée est convertie après arrêt. **Jusqu’à l’arrêt** continue jusqu'à l'arrêt ou épuisement du disque.

**Démarrer l’enregistrement** ouvre alors le microphone, jamais avant. La forme en direct montre les 20 dernières secondes, l'horloge la durée totale et les vumètres l'entrée. **P** pause/reprend sans inclure le temps de pause. **Arrêter**, **Échap**, **Espace** ou **R** conserve la prise. Insertion/remplacement ou nouveau clip forme une annulation ; une nouvelle forme d'onde doit encore être enregistrée. **Abandonner l’enregistrement** confirme la suppression de cette seule prise. Fermer propose conserver, abandonner ou continuer. Les autres éditions sont verrouillées pendant l'enregistrement.

L'entrée n'est pas renvoyée aux haut-parleurs. Réglez le gain sur l'interface/micro ou dans Linux ; baisser ensuite ne répare pas une entrée écrêtée. La perte d'un périphérique arrête et conserve l'audio capturé au lieu de changer de micro. Les prises sont écrites par blocs, avec sauvegarde environ chaque seconde. La récupération ouvre une forme séparée. Annuler la conversion après arrêt garde la prise dans **Récupérer le travail** et laisse l'ancien document intact.

**Début à ignorer** retire une fois les premières millisecondes de chaque prise pour exclure un clic de démarrage. La valeur initiale est 50 ms, réglable de 0 à 500 ms et mémorisée. À 0 ms, le début est conservé ; une coupe est suivie d’un fondu d’entrée de 5 ms. L’audio retiré n’est pas enregistré. Horloge, vue, niveaux et durée maximale suivent l’audio conservé. Pause/reprise ne répète pas la coupe. Avec accompagnement, la position du clip tient compte du temps retiré pour préserver l’alignement.

## 6. Sélection, canaux et édition

Cliquez pour placer le curseur, glissez pour sélectionner. En stéréo, glissez dans L ou R pour un canal, sur les deux pour la stéréo. **Canaux** ou **Édition → Choisir les canaux** change les canaux sans perdre l'intervalle : **Alt+B / Alt+L / Alt+R** pour les deux/gauche/droite. Maj+clic étend en gardant les canaux ; double-clic sélectionne l'audio visible du canal cliqué ; **Ctrl+A** prend toute la durée des canaux choisis. Le mono a un canal. **Définir la sélection** saisit les trames exactes ; 44 100 trames à 44 100 Hz valent une seconde. **F4** rentre les bornes aux passages par zéro (gauche si les deux).

**Couper / Ctrl+X** retire et copie ; **Copier / Ctrl+C** copie ; **Coller / Ctrl+V** remplace la sélection ou insère au curseur. **Collage mixé / Ctrl+M** additionne l'audio du presse-papiers et peut augmenter les crêtes. **Suppr** retire l'intervalle ; **Rogner / Ctrl+T** garde uniquement celui-ci. **Ctrl+Z / Ctrl+Maj+Z** annule/rétablit. Le collage convertit la fréquence sans changer le presse-papiers. Pour les deux canaux, le nombre doit correspondre. Copier/exporter gauche ou droite donne du mono ; l'enregistrement normal garde toute la stéréo.

La stéréo partage une ligne temporelle : couper/supprimer/rogner, étirer, insérer ou ajouter une queue exige les deux canaux. Coller du mono dans un canal stéréo doit remplacer exactement l'intervalle ; le collage mixé doit rester dans la durée existante. **Silence** vide un canal sans déplacer l'autre. Transposition, délai, écho, réverbération et convolution peuvent traiter un canal à durée fixe. Enregistrer dans une stéréo existante exige aussi les deux. Annulation/récupération gardent le choix de canaux.

### Modifier des échantillons individuels

Zoomez avec **+** ou **Ctrl+molette** jusqu’aux points carrés (au moins deux pixels logiques entre échantillons). L’axe horizontal indique alors les indices à partir de 0. Glissez un point verticalement pour modifier uniquement cet échantillon de ce canal. Sa position reste fixe, même si le pointeur traverse d’autres points ou canaux. Le déplacement donne un aperçu ; relâcher valide, **Échap** annule. **Maj+glisser** permet toujours de sélectionner l’audio.

Un double-clic ou clic droit sur un point ouvre **Modifier un échantillon**. **Édition → Modifier un échantillon** fonctionne à tout niveau de zoom. La position initiale est celle du curseur dans le premier canal sélectionné ; indice et canal sont modifiables. Affichez une valeur normalisée ou en 8, 16 ou 24 bits signés. Zéro est le silence ; −1/+1 représentent le niveau maximal normal. Par exemple, −16384 en affichage 16 bits correspond à −0,5 normalisé. Changer la plage d’affichage ne change ni l’audio ni l’encodage. **OK** applique une valeur ; **Annuler** préserve l’original.

Chaque déplacement terminé ou valeur confirmée forme une étape Annuler/Rétablir. Tous les autres échantillons, l’autre canal, la durée et les métadonnées restent inchangés. Le glissement est limité à −1 … +1 ; les crêtes flottantes existantes restent accessibles numériquement. La lecture s’arrête au début d’une correction ; l’édition est bloquée pendant l’enregistrement. Pour une région multipiste, modifiez sa copie en forme d’onde puis appliquez-la explicitement à la région. Écoutez après chaque correction ; pour un clic de plusieurs échantillons, rapprochez chaque point du tracé voisin. Une transition brutale vers zéro peut créer un clic. WAV float32 conserve exactement les valeurs internes ; enregistrer en MP3 recompresse tout le fichier avec pertes.

### Dessiner la forme d’onde

Activez **Édition → Dessiner la forme d’onde**, appuyez sur **D** ou utilisez le crayon près des boutons de zoom. Dessinez directement sur la forme d’onde avec le bouton gauche ; inutile de viser un point individuel. La ligne dessinée remplace les valeurs entre −1 et +1 ; elle ne déplace pas verticalement la forme d’onde d’origine.

Le zoom détermine la taille du groupe : environ deux pixels logiques d’audio, arrondis au nombre entier supérieur d’échantillons. À fort zoom, un échantillon change ; en dézoomant, plusieurs changent ensemble. Chaque groupe couvre au plus une seconde. Un geste plus long peut toucher plusieurs groupes et modifier plus d’une seconde au total. Des lignes droites relient les positions successives du pointeur ; repasser sur un groupe remplace son dessin précédent.

Le canal de départ reste fixe même si le pointeur traverse l’autre canal. Les autres échantillons, l’autre canal, la durée et les métadonnées sont conservés. Les groupes colorés et la nouvelle ligne montrent l’aperçu. Relâcher valide tout le geste en une seule annulation. **Échap**, la perte du focus, un changement de zoom ou la désactivation du dessin annulent l’aperçu. **Maj+glisser** sélectionne toujours l’audio ; appuyez à nouveau sur **D** pour revenir au fonctionnement normal. Le dessin est bloqué pendant l’enregistrement. Zoomez pour les corrections précises : dézoomer remplace aussi les petits détails des groupes touchés. Écoutez ensuite et utilisez **Ctrl+Z** au besoin. En multipiste, modifiez une copie de la forme d’onde puis appliquez-la au clip.

## 7. Appliquer des effets

Les effets de forme d'onde sous **Effets** traitent l'intervalle/canaux choisis, ou toute leur durée sans sélection temporelle. L'autre canal reste intact et audible dans l'aperçu stéréo. **Écouter** lit au maximum les huit premières secondes sans appliquer ; recliquer, changer un réglage ou fermer arrête. **OK** applique une annulation ; **Annuler** conserve l'original. **F2 / Répéter la dernière commande** répète les réglages sur la sélection/canaux actuels. Normalisation, temps/hauteur et distorsion haute qualité analysent toute la sélection avant l'aperçu.

### Amplitude

**Amplifier / fondre** règle amplification initiale/finale : 100 % inchangé, 50 % moitié, 200 % double amplitude. Verrouiller gauche/droite lie les canaux ; égaliser début/fin donne un gain constant, sinon un fondu. Le linéaire peut atteindre zéro, le logarithmique exige des extrémités positives. Les préréglages proposent ±6 dB et fondus. **Fondu d’entrée / Fondu de sortie** appliquent immédiatement un fondu linéaire. Exemple : sélectionner l'introduction, choisir un fondu d'entrée, écouter puis valider.

**Mélangeur de canaux** exige la stéréo. Chaque sortie combine des pourcentages L/R ; les négatifs inversent la polarité d'entrée, l'inversion de sortie celle de la somme. Les préréglages échangent, copient un côté, moyennent en mono (toujours deux canaux) ou soustraient. Le mélange peut dépasser 0 dBFS. Une sélection d'un canal change seulement sa sortie, même si les deux originaux l'alimentent.

**Traitement de la dynamique** associe dB d'entrée et de sortie. Sous la diagonale atténue, au-dessus amplifie. Cliquez/glissez les points, saisissez les valeurs dessous ; clic droit, retirer un point ou Suppr efface un point intérieur. Les extrémités restent fixes. Attaque règle la réponse aux crêtes, relâchement le retour, gain de sortie le résultat. Lier la stéréo garde une correction commune. Pour la parole, commencez à 3:1 au-dessus de −18 dB. Compresseur réduit les passages forts, gate/expanseur les faibles, limiteur les crêtes. Sans anticipation, une attaque lente laisse passer les transitoires.

**Enveloppe de volume** dessine le gain sur 0–100 % du fragment, avec amplitude de 0–200 % (100 % neutre). Glissez ou saisissez positions/gains ; retirez les points intérieurs. Les préréglages donnent fondus, fondu aux deux bouts et creux central. L'interpolation logarithmique exige des gains positifs. Pour baisser un mot, encadrez-le de points et dessinez un creux. Ceci écrit l'audio ; les courbes de clips restent éditables séparément.

**Normaliser** amène la plus haute crête à la cible (98 % par défaut) par un gain unique. Les mots ne deviennent pas égaux. Lier gauche/droite garde la balance ; délier cible chaque canal. Retirer la composante continue recentre d'abord ; le silence reste silencieux. Utile après mélange pour garder de la marge PCM. **Inverser la polarité** inverse la polarité, **Inverser le sens** le temps, **Silence** met à zéro sans retirer de durée. Ils s'appliquent immédiatement.

### Égalisation et filtres

Sous **Filtres**, **Égaliseur graphique** comporte dix bandes d'octave, 31,5 Hz–16 kHz, chacune −24…+24 dB. Les bandes inutilisables à basse fréquence d'échantillonnage sont désactivées. Plat remet à zéro ; renfort des basses, présence vocale et sourire léger offrent des départs. Le graphe combine bandes et gain de sortie (affichage −36…+36 dB). Les hausses peuvent dépasser 0 dBFS : baissez la sortie avant export PCM.

**Égaliseur paramétrique** propose cinq bandes en cloche et deux plateaux grave/aigu, activables séparément. Fréquence choisit centre/transition, gain −24…+24 dB, un Q élevé resserre la cloche. Les plateaux ont une transition douce fixe sans Q. Traitez une résonance par une cloche étroite négative, la couleur générale par une cloche large/un plateau et peu de gain. Plat/réinitialiser remet les gains à zéro ; clarté vocale/chaleur sont des départs.

**Filtres** propose passe-haut (grondement, départ 80 Hz), passe-bas (adoucir les aigus, 8 kHz), passe-bande et réjecteur. Passe-haut/bas utilisent Butterworth 12/24/36/48 dB/oct, environ −3 dB à la coupure ; une pente raide peut résonner davantage. Passe-bande/réjecteur utilisent Q. Téléphone est un passe-bande large ; les réjecteurs 50/60 Hz n'enlèvent pas les harmoniques du ronflement. Réinitialiser restaure le grondement. L'état suit les blocs mais démarre vide à la sélection ; durée conservée, phase modifiée. Une sélection courte abrupte peut cliquer ; élargissez-la.

### Délai, écho et réverbération

**Effets de retard → Retard** ajoute une copie après 1–2 000 ms. Gauche/mono règle le premier délai ; déliez pour un temps droit distinct. Préréglages : simple 250 ms, slapback 80 ms, doublage 25 ms, élargissement stéréo. **Écho** répète par réinjection (0–95 %) ; plus elle est haute, plus le déclin dure. L'amortissement aigu assombrit les répétitions réinjectées, pas la première copie. Ping-pong alterne en stéréo. Écho chaud/longues répétitions sont des départs ; une forte réinjection peut accumuler les niveaux.

**Réverbération** règle taille de pièce (espacement des réflexions), déclin RT60 approximatif (0,1–10 s), prédélai (0–250 ms) avant l'effet, amortissement aigu et largeur stéréo (0 même effet des deux côtés, 100 pleine largeur ; désactivée en mono). Petite pièce, studio, grande salle et ambiance longue varient espace/déclin. Pour la parole, commencez avec peu d'effet, déclin court et un peu de prédélai. Réverbération algorithmique, sans modèle exact de salle.

Son direct et effet sont des pourcentages indépendants additionnés ; le gain de sortie (−24…+24 dB) règle la somme sans limitation automatique. La durée reste fixe par défaut, coupant les répétitions tardives. Ajouter une queue insère 0,01–60 s et décale l'audio suivant et ses repères. Les 10 dernières ms s'estompent. Les préréglages décochent la queue ; réglez-la ensuite. Un écho extrême peut dépasser 60 s : réduisez réinjection/délai. Exemple : voix 2 s + queue 3 s = 5 s. Un seul canal stéréo ne peut ajouter du temps.

### Réduction du bruit et déclics

Sélectionnez du bruit seul (demi-seconde à plusieurs secondes), choisissez **Capturer le profil de bruit**, puis sélectionnez l'audio à nettoyer et rouvrez **Réduction du bruit**. La capture dans la fenêtre fonctionne aussi sans changer l'audio. Le profil moyenne au maximum les 30 premières secondes. Durée minimale selon l'échantillonnage ; fréquence/canaux doivent correspondre. Pour un canal stéréo, le canal de profil correspondant est utilisé. Enregistrer/charger un profil utilise `.ssnoise`, un spectre sans prise audio. Réutilisez avec une installation correspondante.

Réduction maximale 0–36 dB ; commencez à 6–12 dB. La sensibilité traite plus de fond ; le lissage adoucit les variations mais peut laisser du bruit après les sons. Lier la stéréo garde la balance. « Garder uniquement le bruit retiré » permet d'écouter les pertes : désactivez avant de nettoyer. Doux/Équilibré sont des départs. Convient au souffle/ventilation constants ; ne sépare pas les voix ni ne restaure les détails. Trop de réduction ou un profil musical abîme le son. Durée/repères fixes ; traitement hors ligne.

**Suppression des clics** relie les échantillons intacts autour d'impulsions courtes isolées. Un multiplicateur de seuil élevé est prudent ; un saut minimal dBFS bas trouve des clics faibles. Largeur maximale 0,02–2 ms. Prudent, petits clics et clics larges sont des départs. Écoutez les percussions : leurs attaques ressemblent aux défauts. Longs craquements, écrêtage et bords endommagés nécessitent un autre traitement.

### Temps et hauteur

**Durée/hauteur → Étirement temporel** change la durée (25–400 %) sans changer la hauteur : 200 % double, 50 % divise par deux. Les champs de tempo calculent ancien/nouveau BPM (120→100 donne 120 %), sans détection automatique. Les repères internes suivent l'échelle ; audio/repères suivants se décalent. La stéréo exige les deux canaux. **Transposition** varie −24…+24 demi-tons sans changer durée/repères ; ±12 vaut une octave, 0,01 demi-ton un cent. Préserver les formants aide la voix ; comparez sur les instruments.

Fin (défaut) et Rapide utilisent Rubber Band hors ligne. La stéréo est traitée ensemble ; les extrêmes peuvent sembler artificiels. Pour une vraie modification, utilisez au moins 50 ms et 64 échantillons. Le neutre rend exactement l'original, la sortie s'arrondit aux échantillons. L'aperçu analyse toute la sélection avant huit secondes maximum ; les fichiers longs demandent temps et mémoire d'analyse. La progression est annulable. Pour un clip, modifiez une copie puis réappliquez ; les courbes se redimensionnent, les clips suivants ne bougent pas automatiquement.

### Effets spéciaux

**Spécial → Distorsion** offre écrêtage doux (saturation arrondie), dur (coupure nette), repliement des crêtes et réduction de bits (2–16 bits). Préamplification 0–36 dB, plafond 10–100 %, mélange original/traité, sortie −24…+24 dB. Le plafond ne limite que la partie traitée, pas le direct ni la sortie totale. Chaleur douce, crunch, repliement et bits sont des départs. Haute qualité suréchantillonne contre le repliement spectral (souvent 4×, adapté aux hautes fréquences) et traite tout même pour l'aperçu ; standard est plus rapide/rude. Durée/repères fixes, silence conservé.

**Convolution** applique une réponse impulsionnelle WAV de filtre, enceinte ou espace acoustique. Choisissez-la, réglez direct/effet et écoutez. Mono fonctionne par canal ; une réponse stéréo exige une entrée stéréo et utilise le canal sélectionné correspondant. Une autre fréquence est convertie ; réponse limitée après conversion à 10 secondes et 524 288 échantillons, fichier à 32 Mio. Les réponses vides ou silencieuses sont refusées. Aucun fondu supplémentaire de queue. Normaliser l'énergie met à l'échelle les deux canaux ensemble ; désactivez pour une réponse calibrée. Direct 0 %, effet 100 % donne un filtre pur. Garder la queue complète ajoute la durée de réponse moins un échantillon et décale la suite. Sinon durée fixe. Gardez le fichier intact pour F2 ; s'il change/manque, sélectionnez-le de nouveau.

## 8. Générer, analyser et convertir

**Générer → Tonalités** insère une sinusoïde au curseur ou remplace la sélection avec durée, fréquence Hz et amplitude % choisies. Essayez 440 Hz à faible niveau. **Générer → Silence** insère/remplace une durée de silence ; **Effets → Silence** conserve la durée existante.

**Analyser → Analyse fréquentielle / Alt+Z** affiche fréquences et dBFS des canaux/intervalle choisis (sinon toute la prise). Pour les longs passages, une partie centrale limitée est utilisée, avec fenêtre de Hann et puissance moyenne des canaux. Fréquence/niveau de crête sont indiqués dessous. Sélectionnez un son court pour l'étudier ; ce n'est pas un spectromètre continu. Fermer ne change rien.

**Édition → Convertir la fréquence d’échantillonnage** convertit toute la forme d'onde en Hz choisis, conservant hauteur/durée avec arrondi aux trames (au moins une). Curseur/sélection suivent les mêmes instants. Annuler restaure audio et fréquence. Ceci change le document ; la conversion automatique de lecture change seulement le flux de sortie.

## 9. Multipiste et automation

Créez une session avec fréquence/nombre de pistes, importez des WAV par menu/bouton ou déposez-les depuis le gestionnaire. Les fréquences sont converties ; plusieurs fichiers occupent des pistes successives. **Fenêtre → Insérer la forme d’onde dans le multipiste** insère la forme ouverte. Ajouter/retirer agit sur la piste choisie ; annuler récupère le contenu supprimé. Les noms sont éditables. Muet coupe, solo limite aux pistes solo ; muet reste prioritaire. Pan −100 gauche, 0 centre, +100 droite ; en stéréo il atténue un côté sans copier les canaux.

En **Déplacer les clips**, glissez le centre pour déplacer, les bords pour rogner ; la source est conservée pour rallonger. Le vide de la ligne du temps sélectionne un intervalle de lecture. **Dupliquer le clip / Ctrl+D** partage la source ; **Supprimer le clip / Suppr** retire le clip, pas son fichier source. Clic droit ouvre les commandes. **Propriétés du clip** règle nom, bornes temporelles/source (secondes), gain, pan, fondus et muet ; les fondus doivent tenir ensemble dans le clip. Annuler le garde intact.

**Courbe de volume** et **Courbe de panoramique** dessinent dans les clips. Cliquez pour ajouter, glissez pour déplacer, clic droit/double-clic ouvre trames/valeurs exactes, retirer/Suppr enlève le point choisi, réinitialiser remet au neutre. Échap annule le glissement. Volume : bas 0 %, milieu 100 %, haut 200 %, multipliant gains et fondus. Pan : haut droite, milieu neutre, bas gauche, ajouté au pan clip/piste. Centrez le pan ordinaire pour une traversée complète. Les points suivent la source lors de déplacements/rognages et sont sauvegardés. Revenez au déplacement de clips ensuite.

Double-clic ou **Édition une copie en forme d’onde** ouvre une copie pour effets hors ligne. **Fenêtre → Appliquer la forme d’onde au clip** réapplique explicitement ; changer de vue seul ne suffit pas. Annuler dans la session restaure audio/courbes. La fréquence est reconvertie, les courbes suivent la nouvelle durée, les clips suivants restent fixes : vérifiez les chevauchements. **Mixer la session / Mixer** exporte toute la session, indépendamment de la sélection, avec muet/solo, gains/pan, courbes, effets et queues. Enregistrer la session garde le projet éditable. Ces réglages changent pendant la lecture ; annuler/changer de vue l'arrête.

## 10. Effets de piste, plug-ins et enregistrement

Ouvrez **FX** près d’une piste ou **Effets → Effets de piste**. Ajoutez un effet, choisissez réglages/préréglage et confirmez avec OK ; Appliquer modifie sans fermer. Modifier/double-clic rouvre les réglages. Monter/descendre change l’ordre, la coche contourne, Supprimer retire. Les changements ont Annuler/Rétablir. Au plus seize effets agissent après gain/courbes/fondus du clip, avant volume/pan de piste. Le mono devient stéréo. La queue après dernier clip ajoute 0–60 secondes. Lecture et mixage utilisent la même chaîne sans modifier les sources.

Les chaînes proposent amplification fixe, mélangeur, dynamique, EQ graphique/paramétrique, filtres, délai, écho, réverbération, inversion et plug-ins externes. Appliquer actualise à l’écoute ; l’audio déjà tamponné garde les anciens réglages. Redémarrage, recherche et changement de contournement vident la mémoire d’effet. Normalisation, restauration, temps/hauteur, distorsion et convolution restent des modifications via Modifier une copie en forme d’onde. Utilisez la courbe de volume pour varier le gain du clip.

### VST3, LV2 et LADSPA

Installez un **effet audio Linux natif 64 bits**. Dans Effets de piste, choisissez **Plug-in externe → Ajouter**, le format, puis **Ajouter un plug-in**. Sélectionnez un ensemble `.vst3`, `.lv2` ou une bibliothèque LADSPA (`.so`). Les effets d’un ensemble apparaissent séparément. Choisissez l’effet, cherchez un paramètre et changez sa position normalisée 0–100 % : 50 % ne signifie pas forcément demi-volume. Les paramètres discrets ont des pas ; ceux en lecture seule restent fixes. Appliquer permet l’écoute sur la piste ; OK confirme/ferme.

**Ouvrir la fenêtre du plug-in** ouvre un éditeur VST3/LV2 compatible. Ses paramètres et son état enregistrable sont repris à la confirmation. Les fenêtres propres nécessitent **X11 ou XWayland**. Les commandes générales restent disponibles si l’éditeur manque ou n’est pas compatible ; LADSPA les utilise toujours. Les éditeurs LV2 nécessitant un adaptateur GTK/Qt ne sont pas intégrés.

VST3 accepte un bus stéréo d’entrée/sortie en float32. LV2/LADSPA acceptent les effets mono/stéréo avec autant d’entrées que de sorties ; les effets mono ont une instance par canal stéréo. Instruments MIDI, sidechains supplémentaires, VST2 et plug-ins Windows ne sont pas pris en charge. Les fonctions/ports LV2 requis mais indisponibles sont signalés ; le traitement MIDI/Atom est absent. Un état LV2 nécessitant des fichiers externes ne peut pas être sauvegardé complètement et déclenche un message : choisissez un effet dont l’état est autonome.

Chaque plug-in tourne dans un processus isolé. Plantage, délai dépassé ou audio invalide arrêtent la lecture en préservant l’audio enregistré. Les projets gardent paramètres et au plus 1 Mio d’état par effet. Installez séparément le plug-in, ses bibliothèques/échantillons externes. Sur une autre machine, ajoutez la même version. Les versions absentes/modifiées sont signalées ; lecture/export nécessitent l’effet correspondant ou un contournement volontaire.

### Compensation du retard des plug-ins

Le retard de traitement algorithmique déclaré est compensé par piste en lecture et mixage. Les retards d’une chaîne s’additionnent ; les changements de réglage/contournement actualisent le traitement. Positions et durée du mix restent identiques. Écho musical, prédélai et réverbération restent audibles. La compensation dépend d’une déclaration correcte et est limitée à dix secondes par piste. Un retard invalide ou changeant continuellement déclenche un message.

### Accompagnement et synchronisation

Placez l’accompagnement sur des pistes, choisissez piste cible et curseur. Appuyez sur **R**, choisissez entrée et destination nouveau clip, puis **Lire les pistes existantes pendant l’enregistrement**. Les pistes jouent avec leurs effets ; l’entrée n’est pas renvoyée aux haut-parleurs. **P** suspend/reprend les deux ; **Arrêter/Échap/Espace/R** conserve la prise en une étape d’annulation. Rejeter supprime seulement cette prise. Une panne d’appareil/plug-in conserve l’audio capturé.

**Synchronisation automatique** relie le placement à l’horloge de lecture et mesure l’écart entre horloges d’entrée/sortie. Une mesure assez longue et fiable corrige légèrement la durée après Arrêter. Une mesure courte/instable n’étire pas la prise. La correction de durée nécessite plus de dix secondes de mesures d’horloge utilisables. Elle ne mesure pas le trajet physique entrée/sortie.

Pour ce trajet, choisissez **Options → Étalonner l’enregistrement**, ou le bouton d’étalonnage du dialogue. Choisissez les mêmes appareils, fréquence, mode mono/stéréo, premier canal d’entrée et tampon que pour enregistrer. Reliez sortie et entrée avec un câble de bouclage adapté. Un microphone près d’un haut-parleur inclut aussi le délai acoustique. Commencez à faible niveau. **Démarrer l’étalonnage** joue des impulsions faibles pendant environ six secondes, sans retour de l’entrée. Seul un résultat fiable est enregistré ; silence, saturation, ambiguïté ou instabilité conservent un ancien bon profil. Vérifiez avec une courte prise ; refaites l’étalonnage après changement d’appareils/réglages.

La synchronisation automatique utilise le profil correspondant. Sans profil, la synchronisation d’horloge fonctionne, mais un retard physique peut rester. Sinon, désactivez l’automatisme et utilisez **Décalage de position d’enregistrement** : négatif avance, positif retarde ; −15 ms corrige une prise en retard de 15 ms. Les corrections automatique et manuelle s’excluent.

### Punch-in/out

Choisissez une piste cible et une plage sur la règle multipiste ou via **Édition → Définir la sélection**. Choisissez **Options → Punch-in/out** ou **Maj+R**. Réglez entrée, synchronisation, **Prélecture** (2 s) et **Fondu enchaîné** (5 ms). La sélection fixe les limites d’enregistrement ; l’accompagnement est activé.

L’entrée est préparée avant la lecture. L’original joue pendant la prélecture. Dans l’intervalle choisi, seule la piste cible est coupée pendant la capture de remplacement ; les autres continuent. Après une courte finalisation de synchronisation, l’enregistrement s’arrête automatiquement. Seul l’audio corrigé dans la sélection devient un nouveau clip.

Les fondus mélangent ancien/nouveau dans les limites, au plus 100 ms. L’audio extérieur reste intact. Les clips originaux gardent leurs sources, la zone punch étant recouverte. Ctrl+Z restaure tout en une étape. Sur l’ancien clip, **Restaurer l’audio recouvert** retire toutes ses zones de recouvrement ; supprimez/coupez la nouvelle prise pour éviter d’entendre les deux. Un arrêt anticipé garde seulement la partie capturée dans l’intervalle. Avant l’intervalle, il ne modifie pas la session ; la prise brute reste dans **Fichier → Récupérer le travail**. La récupération d’une prise non confirmée propose l’audio brut, avec prélecture/fin, à placer manuellement. Les zones punch terminées sont sauvegardées dans le projet et la récupération après plantage.

**Enregistrer la session / Enregistrer la session sous** garde audio, clips, courbes, chaînes, état des plug-ins et zones punch. Ouvrir une session les restaure ; le mixage exporte WAV/MP3 avec les mêmes effets. Gardez le projet pour les pistes séparées. Les projets nouvellement enregistrés nécessitent SoundSausage **0.19.0 ou ultérieur** ; les anciennes versions de projet restent lisibles. Un plug-in absent n’empêche pas l’ouverture/récupération des sources.

## 11. Enregistrer avec accompagnement

Placez l'accompagnement sur des pistes, choisissez une autre piste cible et le curseur. Pressez **R**, choisissez entrée/nouveau clip et activez « Lire les pistes existantes pendant l'enregistrement ». Pistes et effets partent du curseur ; l'entrée n'est pas renvoyée aux haut-parleurs. **P** pause/reprend les deux ; **Arrêter/Échap/Espace/R** arrête et conserve la prise en une annulation. L'enregistrement peut continuer après l'accompagnement ; une durée maximale arrête les deux. Abandonner retire seulement la nouvelle prise. Une panne conserve les échantillons capturés. Les éditions sont verrouillées.

Le décalage de position déplace le clip inséré : négatif plus tôt, positif plus tard. Pour une prise retardée de 15 ms, essayez −15 ms. Enregistrez un clic connu via le trajet entrée/sortie réel, comparez les positions, saisissez la différence et vérifiez une seconde prise. Recalibrez après changement de périphérique/tampon. L'audio avant zéro est rogné à l'insertion. Le décalage est mémorisé ; calibration physique automatique, dérive d'horloges, compensation des plug-ins et punch-in/out restent en développement. Testez brièvement avant une longue session.

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

Pas d'entrée : vérifiez périphérique/canal et niveau micro Linux, reconnectez puis recommencez. Pas de sortie : routage, volume, muet/solo et matériel audio. Distorsion/crêtes rouges : baissez le gain cumulé, normalisez avant PCM ; collage mixé et clips superposés s'additionnent. Collage refusé : vérifiez canaux ou durée exacte de remplacement mono. Effet désactivé : ouvrez une forme/copie ; mélangeur exige stéréo, changements de durée les deux canaux. Points au lieu des clips : choisissez déplacer les clips. Disque plein : libérez de la place sans effacer de fichiers de travail actifs. Récupération endommagée : les originaux restent ; supprimez la copie seulement si inutile.

En développement : favoris personnalisés et éditeur de marqueurs. Chaînes temps réel, Linux VST3 et accompagnement sont disponibles comme décrit. Enregistrez avant de quitter. Actualités : [SoundSausage](https://github.com/rene-timmermans/SoundSausage).
