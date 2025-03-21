# Patchwerk Multitrack Ear Training

In dieser App können Songs gehört und einzelne Instrumente an- und ausgestellt werden. Zunächst als Übung und dann als Test schult dies das musikalische Hören. Schüler können durch das eigene Erfahren schnell einzelne Instrumente aus komplexen Songs heraushören und typische Besetzungen identifizieren.

## 🚀 Demo
![Demo GIF](readme_content/multitrack_test_example.gif)

## 📦 Features
- Freies anhören und ausprobieren
- Tests in drei Schwierigkeitsstufen
- Ausprobieren von E-Gitarren-Effekten


## 🛠️ Setup

Es muss ein .tar Image auf den Server geladen und mit einem compose-file gestartet werden. Dafür .tar und compose.yaml in einen Ordner auf dem Server ablegen und die CLI in diesem Ordner öffnen:

```bash
sudo docker load -i multitrack.tar
sudo docker compose up -d
```

### Image 
- Repo klonen und Docker-Image (**multitrack.tar**) erstellen und auf den Server laden
- .tar-Datei aus dem Release herunterladen


### Docker Compose:
```bash

services:
  multitrack:
   image: multitrack
    restart: unless-stopped
    ports:
      - "44222:8000"
```

## 📄 Lizenzen
Das Audiomaterial wurden von "Cambridge Music Technology" veröffentlicht und sind für nicht-kommerzielle Zwecke frei zu nutzen.
https://www.cambridge-mt.com/ms/mtk/

