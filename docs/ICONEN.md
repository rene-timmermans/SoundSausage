# Programma-iconen

SoundSausage gebruikt twee varianten van de aangeleverde staande worst met koptelefoon:

- `src/soundsausage/assets/soundsausage.png`: de paarse afgeronde tegel, met transparante buitenhoeken, voor de taakbalk, launcher en projectpagina.
- `src/soundsausage/assets/soundsausage-mascot.png`: alleen de worst en koptelefoon, met een transparante achtergrond en transparante openingen tussen armen en lichaam, voor gebruik binnen het programma.

Qt krijgt één set venstericonen: de kleine formaten van 16 tot en met 24 pixels gebruiken de losse worst; de grotere formaten vanaf 32 pixels gebruiken de paarse tegel. De schermschaal wordt bij het opbouwen meegenomen, zodat ook de kleine varianten op een scherm met dubbele schaal hun transparante achtergrond houden. De vensterbeheerder kiest uiteindelijk het formaat dat hij voor de titelbalk en taakbalk gebruikt. Het venster **About** gebruikt de losse worst expliciet, ook op groot formaat.

De twee beeldbewerkingen zijn met de ingebouwde imagegen-tool uitgevoerd, op basis van het aangeleverde `SoundSausage-v2.png`. De opdrachten waren: (1) verwijder uitsluitend de achtergrond en vloerschaduw buiten de mascotte en behoud alle karakterdetails; (2) maak uitsluitend de zwarte buitenhoeken van de paarse afgeronde tegel transparant en behoud de tekening en paarse binnenkant. De oorspronkelijke referentie is niet overschreven.

De tests controleren de daadwerkelijke gerenderde achtergrond, de transparante hoeken en armopeningen, de bewaarde paarse koptelefoon, beide schermschalen en het icoon in **About**. De echte desktopdecoratie is niet automatisch gecontroleerd: de geïsoleerde X-server kon in de afgeschermde omgeving geen socket openen.

Qt beschrijft de selectie uit meerdere formaten in [QIcon](https://doc.qt.io/qt-6/qicon.html). Het gedeelde Linux-venstericoon en de keuzevrijheid van de vensterbeheerder staan in de [EWMH-specificatie](https://specifications.freedesktop.org/wm/latest-single/).
