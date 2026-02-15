# Wiki Scraper

Projekt narzędzia CLI do pobierania i analizy danych z wybranej wiki.

## Wymagania
- requirements.txt

## Instalacja
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Uruchomienie
```bash
python3 wiki_scraper.py --help
```

### Summary
```bash
python3 wiki_scraper.py --summary "Team Rocket"
```

### Table (CSV + zliczenia)
```bash
python3 wiki_scraper.py --table "Type" --number 2
python3 wiki_scraper.py --table "Type" --number 2 --first-row-is-header
```

### Count Words (word-counts.json)
```bash
rm -f word-counts.json
python3 wiki_scraper.py --count-words "Team Rocket"
```

### Analyze Relative Word Frequency (+ chart)
```bash
python3 wiki_scraper.py --analyze-relative-word-frequency --mode article --count 30 --language en --chart out.png
```

### Auto Count Words (crawler)
```bash
rm -f word-counts.json
python3 wiki_scraper.py --auto-count-words "Team Rocket" --depth 1 --wait 1
```

## Tryb offline (z pliku HTML)
```bash
python3 wiki_scraper.py --use-local-html --local-html "tests/fixtures/team_rocket_minimal.html" --summary "Team Rocket"
python3 wiki_scraper.py --use-local-html --local-html "tests/fixtures/team_rocket_minimal.html" --table "Team Rocket" --number 2
python3 wiki_scraper.py --use-local-html --local-html "tests/fixtures/team_rocket_minimal.html" --count-words "Team Rocket"
```

## Testy
```bash
python3 -m unittest discover -s tests -p "test_*.py"
python3 wiki_scraper_integration_test.py
```

## Notebook (analiza jezyka)
```bash
python3 -m pip install jupyter
python3 -m jupyter lab
```
`notebooks/language_confidence.ipynb`.
