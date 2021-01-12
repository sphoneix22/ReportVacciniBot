import telegram
from telegram import update
from telegram.ext import Updater, CommandHandler
import logging
import os
import datetime
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Per visualizzare il report più aggiornato sui vaccini usa il comando /report")

def convert_number(number):
    new_number = ""
    for d in number:
        if d not in (",", '.'):
            new_number += d
    return int(new_number)


def get_data(update, context):
    last_usage = context.user_data.get('LastUse')
    if last_usage is None or last_usage + 180 <= time.time():
        context.user_data['LastUse'] = time.time()
    else:
        return context.bot.send_message(chat_id=update.effective_chat.id, text="Per favore attendi, puoi usare il comando solo ogni 3 minuti.")

    context.bot.send_message(chat_id=update.effective_chat.id, text="Sto cercando i dati. Questo può richiedere fino a qualche minuto...", parse_mode=telegram.ParseMode.MARKDOWN)
    URL = os.environ.get("REPORT_URL")

    option = webdriver.ChromeOptions()
    if os.getenv("HEROKU", False):
        option.binary_location = os.getenv("GOOGLE_CHROME_BIN")
    option.add_argument("--headless")
    option.add_argument('--disable-gpu')
    option.add_argument('--no-sandbox')
    option.add_argument("--proxy-server='direct://'")
    option.add_argument("--proxy-bypass-list=*")

    driver = webdriver.Chrome(executable_path=os.getenv("CHROME_EXECUTABLE_PATH"), options=option)

    driver.get(URL)
    try:
        #wait load page
        d = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "title"))
        )
        
        data = driver.find_elements_by_css_selector('.pivotTableCellWrap')
        
        #1/5/2021 5:45:18 PM
        data_update = datetime.datetime.strptime(d.text, '%d/%m/%Y %I:%M:%S %p')

        regioni = {}

        # Da Abruzzo a Valle d'Aosta i dati sono tutti in fila, per qualche motivo quelli del Veneto sono in fondo
        for row in range(4, 24):
            regioni[data[row].text] = {'somministrate': data[row+21].text, 'consegnate': data[row+41].text, 'percentuale_somministrate': data[row+61].text}
        regioni['Veneto'] = {'somministrate': data[85].text, 'consegnate': data[86].text, 'percentuale_somministrate': data[87].text} 

        totale = {'somministrate': data[89].text, 'consegnate': data[90].text, 'percentuale_somministrate': data[91].text}

        msg = '*Report ufficiale vaccinazioni anti COVID-19:\n'

        for regione in regioni:
            msg += f"*{regione}*: {regioni[regione]['somministrate']} dosi somministrate di {regioni[regione]['consegnate']} consegnate ({regioni[regione]['percentuale_somministrate']})\n"
        msg += f"*Totali*: {totale['somministrate']} dosi somministrate di {totale['consegnate']} consegnate ({totale['percentuale_somministrate']})\n\n"

        msg += f"Aggiornamento delle {data_update}"

        context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)
    
        URL_LAZIO = os.environ.get("URL_LAZIO")
        URL_PIEMONTE = os.environ.get("URL_PIEMONTE")
        URL_EMILIAROMAGNA = os.environ.get("URL_EMILIAROMAGNA")
        URL_TOSCANA = os.environ.get("URL_TOSCANA")

        # Lazio scraping
        driver.get(URL_LAZIO)
        data_lazio = convert_number(driver.find_element_by_xpath("//b").text)
        if data_lazio > convert_number(regioni['Lazio']['somministrate']):
            additional_lazio = data_lazio - convert_number(regioni['Lazio']['somministrate'])
        else:
            additional_lazio = 0

        # Piemonte scraping
        driver.get(URL_PIEMONTE)
        raw_data_piemonte = driver.find_element_by_class_name("field--name-title").text
        data_piemonte = ""
        for l in raw_data_piemonte:
            if l not in (" "):
                data_piemonte += l
            else:
                break

        data_piemonte = convert_number(data_piemonte)

        if data_piemonte > convert_number(regioni['Piemonte']['somministrate']):
            additional_piemonte = data_piemonte - convert_number(regioni['Piemonte']['somministrate'])
        else:
            additional_piemonte = 0

        # ER scraping
        driver.get(URL_EMILIAROMAGNA)
        data_emiliaromagna = convert_number(driver.find_element_by_class_name("valore").text)
        if data_emiliaromagna > convert_number(regioni['Emilia-Romagna']['somministrate']):
            additional_emiliaromagna = data_emiliaromagna - convert_number(regioni['Emilia-Romagna']['somministrate'])
        else:
            additional_emiliaromagna = 0

        # Toscana scraping
        driver.get(URL_TOSCANA)
        data_toscana = convert_number(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'inner'))
        ).find_element_by_css_selector("h3").text)

        if data_toscana > convert_number(regioni['Toscana']['somministrate']):
            addional_toscana = data_toscana - convert_number(regioni['Toscana']['somministrate'])
        else:
            addional_toscana = 0

        total_additional = additional_lazio + additional_piemonte + additional_emiliaromagna + addional_toscana
        if total_additional == 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Non ci sono ulteriori dati aggiornati da parte delle regioni.", parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            additional_msg = f"*Stima dati aggiornati in base alle comunicazioni delle regioni:*\n{convert_number(totale['somministrate']) + total_additional} dosi somministrate\n(Questo dato potrebbe non essere accurato.)"
            context.bot.send_message(chat_id=update.effective_chat.id, text=additional_msg, parse_mode=telegram.ParseMode.MARKDOWN)

    except TimeoutException:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Si è verificato un errore nel recupero dei dati.")
    finally:
        driver.quit()


def info(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.MARKDOWN,
        text="Questo bot legge la pagina web del report vaccinazioni anti COVID-19 del Commissario Straordinario per l'Emergenza e quelle di alcune regioni. (Al momento Toscana, Emilia-Romagna, Lazio e Piemonte)\n Creato da @Bananaglassata\n [Github](https://github.com/sphoneix22/ReportVacciniBot)")

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