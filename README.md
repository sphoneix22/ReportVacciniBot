# Come funziona il bot
Tramite Selenium effettua uno scraping sulla pagina del report vaccini anti COVID-19.
Al momento il link alla pagina è [questo](https://app.powerbi.com/view?r=eyJrIjoiMzg4YmI5NDQtZDM5ZC00ZTIyLTgxN2MtOTBkMWM4MTUyYTg0IiwidCI6ImFmZDBhNzVjLTg2NzEtNGNjZS05MDYxLTJjYTBkOTJlNDIyZiIsImMiOjh9).

### Dati dalle regioni
Alcune regioni pubblicano i dati sui vaccinati prima che vengano inseriti sul report nazionale.
Al momento il bot è in grado di recupare i dati della Regione [Toscana](https://vaccinazioni.sanita.toscana.it), [Emilia-Romagna](https://reportvaccinianticovid19er.lepida.it/), [Lazio](https://app.powerbi.com/view?r=eyJrIjoiYTg3MmEwN2QtOTQ2Zi00MzcyLWJmNTctYjkzY2E3MmE0N2RjIiwidCI6IjY0ZTY0YTY0LWZjNzMtNGIzYy05Mjc4LWFmN2I2OGQ2NjU0NCIsImMiOjl9), [Piemonte](https://www.regione.piemonte.it/web/pinforma/notizie/22203-persone-finora-vaccinate-contro-covid?fbclid=IwAR08RnwxdI-_tt-p1Ex9jO2HsSjAT-AIIwqK2YKDMsOFEooE2tt6SYegQhY).

# Come utilizzare il bot
Il bot è utilizzabile col tag `@reportvaccinibot` su Telegram.

Per avviarlo in locale, dopo aver installato i prerequisiti e inserito le seguenti variabili d'ambiente è sufficiente avviare il file `bot.py`
```
"TELEGRAM_TOKEN"
"REPORT_URL"
"PORT":"25565"
"CHROME_EXECUTABLE_PATH"
"URL_LAZIO"
"URL_PIEMONTE"
"URL_EMILIAROMAGNA"
"URL_TOSCANA"
```
