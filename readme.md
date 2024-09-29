# ClearSpeech

To repozytorium zawiera aplikację webową opartą na FastAPI. Aplikacja jest konteneryzowana przy użyciu Dockera i zarządzana za pomocą Docker Compose, co ułatwia jej konfigurację i wdrażanie.
http://34.118.86.83:3000/
## Funkcje

- Framework webowy FastAPI
- Aplikacja konteneryzowana dla łatwego wdrażania
- Docker Compose do zarządzania wieloma usługami
- Zawiera punkty końcowe API do interakcji webowych

---

## Spis Treści

- [Instalacja](#instalacja)
- [Technologie](#technologie)
- [Koszt miesięczny](#koszt-miesięczny)
- [Dokumentacja API](#dokumentacja-api)

---

## Instalacja

### Wymagania

Przed rozpoczęciem instalacji projektu upewnij się, że masz zainstalowane następujące narzędzia:

- [Docker](https://www.docker.com/get-started) (wersja 20.x lub nowsza)
- [Docker Compose](https://docs.docker.com/compose/install/) (wersja 1.29.x lub nowsza)
- Git (opcjonalnie, jeśli musisz sklonować repozytorium)

### Instalacja krok po kroku

#### 1. Sklonuj repozytorium

```bash
git clone https://github.com/ataj09/clearspeech.git
cd your-repository
run docker-compose up --build
```

## Stak technologiczny
 - Google cloud (VM and Speech-to-text)
 - Hugging face (analiza sentymentu)
 - Luxand Api (wykrycie emocji) 
 - Python 3.11.9
 - Docker and Docker-compose
 - FastApi
 - React.js

## Koszt miesięczny
 - Google cloud ok. 80zł miesięcznie
 - Luxand api ok. 80zł miesięcznie


## Dokumentacja API
http://34.118.86.83:8000/docs