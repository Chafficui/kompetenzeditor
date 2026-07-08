# Kompetenzeditor
This is an early version of my so-called "Kompetenzeditor" (competence editor). It was developed by me as part of a student project during a semester at Fulda University of Applied Sciences.
This software is still at an early stage. I therefore advise against using it in production environments. Currently, I can't work on this project, so don't expect, much development from me here  in the near future.
Overall, it is assumed that the authors have a basic understanding of the formulation and definition of learning objectives and competences.
> The software is currently only available in German and does not support any other language. Therefore, the following information will also be partly written in German.

## What is this exactly?
This is a competence editor. This software supports users in formulating competence descriptions in free text and inserting existing texts in order to check their suitability. The texts are analyzed according to certain criteria and, based on this, passive assistance is offered that the user can implement. A score is also calculated, which shows the user how ‘good’ or how close the text comes to an ‘ideal’ description of competences according to scientific criteria.

Together with my professor at the time, I published a workshop paper on this software, which you can find here. (Unfortunately, this is only available in German).
https://dl.gi.de/items/ed3c8a09-79c0-4799-ba98-f7df219aad8d
```
Erstellung eines NLP-basierten Editors mit Qualitätsindikatoren und Änderungsvorschlägen für Kompetenzbeschreibungen}
Loth, Ludwig; Konert, Johannes
Proceedings of DELFI Workshops 2022
Bonn: Gesellschaft für Informatik e. V. pp. 149–158.
DELFI: Workshop. Karlsruhe. 12.-14. September 2022
DOI: 10.18420/delfi2022-ws-32
```

![Screenshot of a the Software in action](https://raw.githubusercontent.com/ludwig-loth/kompetenzeditor/main/screenshot.png)


## Tech Stack
- Docker
- spaCy (NLP Software)
- Vue.js
- Nuxt.js
- Vuetify
- Dexie.js


## know bugs and downsides
- it currently only supports german
   - the whole UI is written in german as well
- `kennen` und `erkennen` im gleichen Test führen zu unerwartetem Verhalten
  - `kennen` wird dann icht mehr als gutes Verb erkannt
- das einfügen von Text mit Listenelementen und anderem funktioniert nicht wie erwartet
- die Response Time ist im Allgemeinen etwas langsam


## Setup instructions
  
### **spaCy Server**

> Das Backend ist besteht aus einer bereits etablierten Software und ist nicht von mir entwickelt worden.

Dies ist ein vorgefertigter Dockercontainer mit einer in Python geschriebenen REST-API. Dies bietet alle nötigen Möglichkeiten für das abfragen der NLP-gestützen Analyse von Texten 
hier zu finden: https://github.com/bbieniek/spacy-api-docker

Die REST API Dokumentation ist hier zu finden: https://hub.docker.com/r/bbieniek/spacyapi/

- Laden Sie sich unter https://docs.docker.com/get-docker/ die für ihr Betriebssystem geeignete und neuste Version von Docker herunter.
- Nun müssen Sie den entsprechenden Dockercontainer von spaCy mit deutschem Core  installieren, dazu öffnen Sie ein Terminal und tippen diesen Befehl ein `docker pull bbieniek/spacyapi:de_v3`
- Tippen Sie diesen Befehl ein um den Container zu starten `docker run -p "127.0.0.1:8080:80" bbieniek/spacyapi:de_v3`
- Nachdem der obige Befehl das erste Mal gegeben worden ist. Lässt sich der Container auch aus Docker Desktop heraus starten und beenden. Starten Sie Docker Desktop und starten Sie den Container dieser wird unter einem zufälligem Namen und der Bezeichnung **bbieniek/spacyapi** aufgeführt.
- der Container ist nun gestartet und die REST-API von spaCy ist nun auf ihrer lokalen Maschine unter http://127.0.0.1:8080/ bzw. http://localhost/ erreichbar.
- das UI zum testen von der NLP-Software erreichen Sie nun unter http://127.0.0.1:8080/ui/
- Die Installation des Backendes ist hiermit abgeschlossen.


### **Frontend: Kompetenzeditor Beta**

- Falls Sie Node.js niocht bereits installiert haben dann laden Sie Node.js inklusive des Paketmanagers NPM von dieser Seite herunter https://nodejs.org/en/ und installieren Sie dies anschließend in dem Sie den Anweisungen des Installers folgen
- entpacken Sie den angehängten Ordner **kompetenzeditor.zip** in ein Verzeichnis Ihrer Wahl
- Öffnen Sie ein Terminalfenster und navigieren Sie in der Verzeichnis **kompetenzeditor**
- Geben Sie folgenden Befehl ein um die entsprechenden Pakete zu installieren 'npm install'
- Generieren Sie zunächst die Dateien damit Nuxt.js diese zuordnen kann. Tippen Sie dazu folgendes in das Terminalfenster ein `npm run build`
- Sobald der Build-Prozess abgeschlossen ist tippen Sie folgendes ein um den Editor endgültig zu starten `npm run start`
- der Kompetenzeditor ist nun einsatzbereit und unter http://localhost:3000/ zu finden
  
> **WICHTIG**
> Der Kompetenzeditor funktioniert nur in Verbindung mit dem Backend von spaCy. Deshalb müssen beide gestartet sein um die Software nutzen zu können.

#### Zusammenfassung 
##### **Lokale Möglichkeit:**

- Docker installieren
- Docker Container runterladen in der deutschen Version
- dazu in die Konsole eintippen:
  - `docker pull bbieniek/spacyapi:de_v3`
- in diesem Projekt wird standardmäßig der PORT `8080` genutzt
- Docker starten auf `http://127.0.0.1:8080/`:
  - `docker run -p "127.0.0.1:8080:80" bbieniek/spacyapi:de_v3`

##### **Digital Ocean:**

- App erstellen mit DockerHub direkt
- Repository: `bbieniek/spacyapi`
- Tag: `bbieniek/spacyapi:de_v3` für deutsches Model
- getestet mit `$5.00/mo – Basic 512 MB RAM | 1 vCPU  x  1`
- Problem ist, dass die UI nicht funktioniert hier

An dem `/ui` Endpoint wird eine UI zur Kontrolle erstellt.
http://127.0.0.1:8080/ui/

-----------------------------------------------------


## NLP 

### **Liste der Tags/Abkuerzungen/POS**
Die ist hilfreich um zu verstehen, welche Verarbeitungen spaCy macht und um diese in dem UI unter dem Endpoint `/ui` entsprechend lesen zu können.

| Tag | Description | Example |
|---|---|---|
| ADJA | attributive adjective (including participles used adjectivally) | das **große** Haus die **versunkene** Glocke |
| ADJD | predicate adjective; adjective used adverbially | der Vogel ist **blau** er fährt **schnell** |
| ADV | adverb (never used as attributive adjective) | sie kommt **bald** |
| APPR | preposition left hand part of double preposition | **auf** dem Tisch an der Straße entlang |
| APPRART | preposition with fused article | **am** Tag |
| APPO | postposition | meiner Meinung **nach** |
| APZR | right hand part of double preposition | an der Straße **entlang** |
| ART | article (definite or indefinite) | **die** Tante; **eine** Tante |
| CARD | cardinal number (words or figures); also declined | **zwei; 526; dreier** |
| FM | foreign words (actual part of speech in original language may be appended, e.g. FMADV/ FM-NN) | **semper fidem** |
| ITJ | interjection | **Ach**! |
| KON | co-ordinating conjunction | **oder** ich bezahle nicht |
| KOKOM | comparative conjunction or particle | er arbeitet **als** Straßenfeger, so gut **wie** du |
| KOUI | preposition used to introduce infinitive clause | **um** den König zu töten |
| KOUS | subordinating conjunction | **weil** er sie gesehen hat |
| NA | adjective used as noun | der **Gesandte** |
| NE | names and other proper nouns | **Fulda** |
| NN | noun (but not adjectives used as nouns) | der **Abend** |
| PAV [PROAV] | pronominal adverb | sie spielt **damit** |
| PAVREL | pronominal adverb used as relative | die Puppe, **damit** sie spielt |
| PDAT | demonstrative determiner | **dieser** Mann war schlecht |
| PDS | demonstrative pronoun | **dieser** war schlecht |
| PIAT | indefinite determiner (whether occurring on its own or in conjunction with another determiner) | **einige** Wochen, **viele solche** Bemerkungen |
| PIS | indefinite pronoun | sie hat **viele** gesehen |
| PPER | personal pronoun | **sie** liebt **mich** |
| PRF | reflexive pronoun | ich wasche **mich**, sie wäscht **sich** |
| PPOSS | possessive pronoun | das ist **meins** |
| PPOSAT | possessive determiner | **mein** Buch, das ist der **meine/meinige** |
| PRELAT | relative depending on a noun | der Mann, **dessen** Lied ich singe […], **welchen** Begriff ich nicht verstehe |
| PRELS | relative pronoun (i.e. forms of der or welcher) | der Herr, **der** gerade kommt; der Herr, **welcher** nun kommt |
| PTKA | particle with adjective or adverb | **am** besten, **zu** schnell, **aufs** herzlichste |
| PTKANT | answer particle | **ja, nein** |
| PTKNEG | negative particle | **nicht** |
| PTKREL | indeclinable relative particle | **so** |
| PTKVZ | separable prefix | sie kommt **an** |
| PTKZU | infinitive particle | **zu** |
| PWS | interrogative pronoun | **wer** kommt? |
| PWAT | interrogative determiner | **welche** Farbe? |
| PWAV | interrogative adverb | **wann** kommst du? |
| PWAVREL | interrogative adverb used as relative | der Zaun, **worüber** sie springt |
| PWREL | interrogative pronoun used as relative | etwas, **was** er sieht |
| TRUNC | truncated form of compound | **Vor-** und Nachteile |
| VAFIN | finite auxiliary verb | sie **ist** gekommen |
| VAIMP | imperative of auxiliary | **sei** still! |
| VAINF | infinitive of auxiliary | er wird es gesehen **haben** |
| VAPP | past participle of auxiliary | sie ist es **gewesen** |
| VMFIN | finite modal verb | sie **will** kommen |
| VMINF | infinitive of modal | er hat es sehen **müssen** |
| VMPP | past participle of auxiliary | sie hat es **gekonnt** |
| VVFIN | finite full verb | sie **ist** gekommen |
| VVIMP | imperative of full verb | **bleibt** da! |
| VVINF | infinitive of full verb | er wird es **sehen** |
| VVIZU | infinitive with incorporated zu | sie versprach **aufzuhören** |
| VVPP | past participle of full verb | sie ist **gekommen** |

*Tabelle-Quelle: https://www.sketchengine.eu/german-stts-part-of-speech-tagset/*


-----------------------------------------------------------

## License
- this Project is licensed under [MIT License](https://github.com/ludwig-loth/kompetenzeditor/blob/main/LICENSE.txt)
