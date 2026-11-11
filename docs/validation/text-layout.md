# Tekstuitlijning en vensterindeling — 0.16.1

De tekstindeling gebruikt de werkelijke letterafmetingen. De Y-astitel van de
dynamiek- en volumecurves staat boven de schaal; de onderste Y-waarde en eerste
X-waarde hebben afzonderlijke ruimte. EQ- en spectrumassen, golfvormschalen,
kanaallabels, tijdvelden en multitrackbediening schalen met het lettertype mee.
Te dicht bij elkaar liggende schaalwaarden worden overgeslagen zonder de
bijbehorende rasterlijnen te verliezen. De kanaalletters van de meter krijgen
ruimte voor hun volledige lettercontour.

Formulieren volgen hun minimale inhoudsmaat en de benodigde hoogte van
afgebroken regels. Past de inhoud niet op het scherm, dan komt ze in een
scrollgebied; bevestigingsknoppen blijven daarbuiten bereikbaar. Een taal- of
letterwijziging past bestaande vensters aan zonder effectinstellingen te
vervangen. De minimale hoofdvenstergrootte volgt de bediening.

## Automatische controles

Acht nieuwe regressiecontroles behandelen:

- 24 soorten vensters in vijf talen met letters van 9, 11 en 14 punten: 360 renders.
- Breedte en hoogte van zichtbare labels, schermgrenzen en bereikbare dialoogknoppen.
- Acht overige invoervensters: nieuwe golfvorm/sessie, tijdselectie, samplerate,
  toon, stilte, clipeigenschappen en lijnpunten.
- Open effectvensters na taal- en letterwijzigingen, met behoud van parameters,
  audiosamples en Undo.
- De werkelijk getekende tekstgrenzen van curves, EQ, spectrum en de meter:
  geen afsnijding of onderlinge overlap van schaalwaarden en titels.
- Een groot Duits formulier bij 24 punten, met scrollen en bereikbare knoppen.
- Bestands-, meldings- en voortgangsvensters in alle vijf talen bij 14 punten.
- Hoofdvenstertijden en meter binnen de minimale venstergrenzen.
- Een echte muisklik op de statusbalkoptie, vrijgekomen werkruimte, gewijzigde
  meldingen, taal- en weergavewissels en een nieuwe vensterstart.

De statusbalk is de smalle informatieregel onder de niveaumeter. De optie
verbergt die regel en bewaart de voorkeur in `ui/show_status_bar`.

De rendercontrole gebruikt een virtueel scherm van 800 × 800 logische pixels.
De distributiecontainers installeren DejaVu Sans en Mono voor de expliciete
letterproeven. De grote klok berekent ook bij een breder vervangend lettertype
en tijdwaarden met uren haar benodigde breedte. Alle geneste vensterlayouts
worden na taal- en letterwijzigingen opnieuw gemeten.
Hardwarelijsten en de plug-inindex worden voor de indelingscontrole vervangen
door lege lijsten. Daarvoor worden geen microfoons of externe plug-ins geopend.
De bestaande controle op een ruim golfvormvlak blijft behouden: meer dan 62%
van de vensterhoogte bij 1015 × 609 pixels. Een afzonderlijke proef met 150%
schermvergroting controleert de getekende labels en het aanpassen van open
vensters.

Lokaal slagen alle 384 controles; zes expliciete audiobackendcontroles worden
lokaal overgeslagen en blijven onderdeel van de distributiebouw. De afzonderlijke
proef bij 150% schermvergroting slaagt voor tekstgrenzen, open vensters en
hoofdvenstertijden. De distributiebouw wordt vóór publicatie gecontroleerd.
DSP-ABI 7 en projectformaat 4 blijven ongewijzigd.
