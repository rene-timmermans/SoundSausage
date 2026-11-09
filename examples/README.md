# SoundSausage-voorbeelden

De twee zelfstandige projecten bevatten synthetische audio en kunnen direct worden geopend, vanuit de projectmap:

```bash
./run.sh examples/demo-multitrack.celp
./run.sh examples/demo-envelopes.celp
```

`demo-multitrack.celp` toont overlappende clips, fades en spoorinstellingen. `demo-envelopes.celp` demonstreert eerst volumevariatie en daarna een toon die van links naar rechts beweegt. Druk op Spatie om af te spelen.

Opnieuw genereren kan met `make demo` en `PYTHONPATH=src python3 tools/make_envelope_demo.py`. Die opdrachten schrijven nieuwe voorbeelden naar `build/`.
