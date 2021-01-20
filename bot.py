import telegram
from telegram import update
from telegram.ext import Updater, CommandHandler
import logging
import os
import urllib.request as requests
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Per visualizzare il report più aggiornato sui vaccini usa il comando /report")

def convert_number(number):
    new_number = ""
    for d in number:
        if d not in (",", '.'):
            new_number += d
    try:
        return int(new_number)
    except ValueError:
        return 0


def get_data(update, context):
    URL = os.environ.get("REPORT_URL")

    data = json.load(requests.urlopen(URL))['data']

    regioni = {'ABR':'Abruzzo', 'BAS':'Basilicata', 'CAL':'Calabria', 'CAM': 'Campania', 'EMR':'Emilia-Romagna', 'FVG': 'Friuli Venezia Giulia', 'LAZ': 'Lazio', 'LIG':'Liguria', 'LOM': 'Lombardia', 'MOL': 'Molise', 'MAR': 'Marche', 'PAB': 'Provincia di Bolzano', 'PAT': 'Provincia di Trento', 'PIE': 'Piemonte', 'PUG': 'Puglia', 'SAR': 'Sardegna', 'SIC': 'Sicilia', 'TOS': 'Toscana', 'UMB': 'Umbria', 'VDA': "Valle d'Aosta", 'VEN': 'Veneto'}
    
    msg = "*Dati vaccinazioni anti COVID-19 in Italia:*\n"

    totale_dosi_somministrate = 0
    totale_dosi_consegnate = 0
    for regione in data:
        msg += f"*{regioni[regione['area']]}*: {regione['dosi_somministrate']} dosi somministrate di {regione['dosi_consegnate']} dosi consegnate ({regione['percentuale_somministrazione']}%)\n"
        totale_dosi_somministrate += int(regione['dosi_somministrate'])
        totale_dosi_consegnate += int(regione['dosi_consegnate'])
    totale_percentuale_dosi_somministrate = round((totale_dosi_somministrate/totale_dosi_consegnate)*100, 2)

    msg += f"*Totali*: {totale_dosi_somministrate} dosi somministrate di {totale_dosi_consegnate} dosi consegnate ({totale_percentuale_dosi_somministrate}%)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)


def info(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.MARKDOWN,
        text="Questo bot restituisce i dati disponibili sulla [repository Open Data Vaccini](https://github.com/italia/covid19-opendata-vaccini)\n Creato da @Bananaglassata\n [Github](https://github.com/sphoneix22/ReportVacciniBot)")

def main():
    updater = Updater(token=os.environ.get("TELEGRAM_TOKEN"), use_context=True) 

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('report', get_data))
    dispatcher.add_handler(CommandHandler('info', info))

    if os.getenv("HEROKU", False):
        updater.start_webhook(listen="0.0.0.0", port=os.getenv("PORT"), url_path=os.getenv("TELEGRAM_TOKEN"))
        updater.bot.setWebhook(os.getenv("HEROKU_LINK")+os.getenv("TELEGRAM_TOKEN"))
    else:
        updater.start_polling()

if __name__ == '__main__':
    main()