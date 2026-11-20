# SoundSausage-voorbeelden

Maak vanuit de projectmap twee zelfstandige voorbeelden met synthetische audio:

```bash
make demo
./run.sh build/demo-multitrack.celp
./run.sh build/demo-envelopes.celp
```

Gebruik de Python-omgeving met de geïnstalleerde [afhankelijkheden](../docs/INSTALLEREN.md#zelf-bouwen).
De voorbeelden worden lokaal in `build/` aangemaakt; er zijn geen downloads nodig.

- `demo-multitrack.celp` toont overlappende clips, fades en spoorinstellingen.
- `demo-envelopes.celp` demonstreert eerst volumevariatie en daarna een toon die
  van links naar rechts beweegt.

Druk op Spatie om af te spelen. De gegenereerde projecten kun je bewerken en onder
een eigen naam opslaan. Dezelfde opdracht maakt `build/demo.wav` en een WAV-mix
van de volume-/panvoorbeelden voor vergelijking en previewhulpmiddelen.
