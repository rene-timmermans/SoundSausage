# Referentiesessies maken in de Windows 7-VM

Kopieer `A-mono.wav` en `B-stereo.wav` naar één map in de VM, bijvoorbeeld `C:\CEP-Test\`. Beide zijn standaard 44.100 Hz / 16-bit PCM. A is twee seconden mono; B is drie seconden stereo. Sla de sessies in diezelfde map op en behoud de WAV-bestandsnamen.

Gebruik de huidige geïnstalleerde Cool Edit Pro-versie. Noteer de versie uit Help → About, of maak daarvan een screenshot. Opnieuw installeren is niet nodig.

Als File → New het venster **New Waveform** met Mono/Stereo en Resolution toont, zit je nog in golfvormweergave. Klik Cancel, kies **View → Multitrack View** en daarna **File → New Session…**. Kies 44100 als om de sample rate wordt gevraagd. Dit is 44.100 Hz; er hoeft geen leeg WAV-bestand te worden aangemaakt.

1. Maak een lege multitracksessie met samplerate 44.100 Hz en sla die op als `00-leeg.ses`.
2. Plaats A op spoor 1 vanaf tijd 0 en sla op als `01-een-clip.ses`.
3. Voeg B toe op spoor 2 vanaf tijd 1,000 seconde; behoud A op spoor 1. Sla op als `02-basis.ses`.
4. Verplaats alleen B naar tijd 2,000 seconden en sla op als `03-verplaatst.ses`.
5. Open `02-basis.ses` opnieuw. Zet alleen het volume van spoor 1 op 50% (of −6 dB als de dialoog alleen dB biedt). Noteer de werkelijk ingevoerde waarde. Sla op als `04-volume.ses`.
6. Open `02-basis.ses` opnieuw. Zet alleen de pan van spoor 2 helemaal naar rechts. Sla op als `05-pan.ses`.

Als een exacte tijd handmatig kan worden ingevoerd in Wave Block Info / clipinformatie, gebruik dat. Anders is slepen voldoende; noteer de uiteindelijke tijd die de toepassing toont. Verander per variant verder geen instellingen.

Een screenshot van `02-basis.ses` in multitrackweergave en de gebruikte volume-/pandialoog is nuttig. Zet de `.ses`-bestanden, de twee bron-WAV's en eventuele screenshots terug in deze map, eventueel als ZIP. Ze hoeven niet via chat te worden geüpload als ze hier op de Steam Deck staan.

Optioneel: exporteer van `02-basis.ses` een stereo-mixdown als gewone 16-bit PCM-WAV, bijvoorbeeld `02-basis-mix.wav`. De exacte opdracht heet mogelijk Edit → Mix Down → All Waves. Noteer als de toepassing daarbij extra opties toont. Dit helpt de mixregels te vergelijken, maar is niet nodig voor de eerste bestandsanalyse.
