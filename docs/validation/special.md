# Vervorming en convolutie — 0.13.0

Veertien nieuwe controles toetsen vier overdrachtsfuncties, stille invoer,
bitgelijke Preview-prefixen, blokgroottes, FFT-convolutie tegen een directe
lineaire referentie, kanaalafzondering, energienormalisatie, IR-resampling,
uitklank, Undo/F2, opslag/herstel zonder extern IR-bestand, foutafhandeling en
annuleren. Grote effectresultaten worden als memmap gecontroleerd. De volledige
suite telt 322 controles; distributie- en pakketverificatie volgen bij de release.

Een 5 kHz-sinus bij 48 kHz, hard clip en 18 dB Drive levert in de lokale proef
een 13 kHz-alias op ongeveer −17,5 dB ten opzichte van de grondtoon zonder
oversampling en ongeveer −67 dB met oversampling. De test vereist minstens
20 dB verbetering. Dit is een specifieke proef, geen universele aliasinggrens.
Oversampling gebruikt de bestaande stateful libsamplerate-converter, met
schijfopslag voor grote tussenresultaten. Preview gebruikt dezelfde volledige
conversie, zodat het uitvoerprefix overeenkomt.

Convolutie gebruikt uniforme FFT-partities met hops van 2048 samples voor korte
responsen en 8192 voor langere. Kernel en invoerhistorie zijn begrensd door de
IR-grens van 524.288 uitvoersamples. Per partitie wordt één kleine scratchbuffer
gebruikt; er ontstaat geen tijdelijke kopie van de hele spectrummatrix. Het
resultaat volgt lineaire convolutie, met eventueel de volledige FIR-uitklank.
Mono-IR wordt per kanaal toegepast; stereo-IR is kanaalgewijs, geen matrixconvolutie.

Een gekozen respons wordt op regelmatige bestandsvorm, bytegrootte, audiolengte
en inhoud gecontroleerd. De inhoudshash wordt vóór en na openen gecontroleerd.
Herhalen vereist dezelfde hash; ontbrekende of gewijzigde bestanden veranderen
het document niet. Het gerenderde geluid blijft zelfstandig in projecten en
herstelkopieën bewaard. Geen extra native ABI of afhankelijkheden zijn toegevoegd;
DSP-ABI blijft 7. Native Time/Pitch-toestand wordt pas na de Python-werkbuffers
aangemaakt, zodat ook een mislukte werkbufferallocatie geen native toestand lekt.
