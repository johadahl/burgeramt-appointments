from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pync
import requests
import json
import logging
import time

TITLE = 'Bürgeramt Appointment Finder'
BASE_URL = 'https://service.berlin.de/terminvereinbarung/termin/'

ALL_BUERGERAMTS = (
    122210,122217,327316,122219,327312,122227,327314,122231,327346,122243,
    327348,122252,329742,122260,329745,122262,329748,122254,329751,122271,
    327278,122273,327274,122277,327276,122280,327294,122282,327290,122284,
    327292,327539,122291,327270,122285,327266,122286,327264,122296,327268,
    150230,329760,122301,327282,122297,327286,122294,327284,122312,329763,
    122304,327330,122311,327334,122309,327332,122281,327352,122279,329772,
    122276,327324,122274,327326,122267,329766,122246,327318,122251,327320,
    122257,327322,122208,327298,122226,327300
)

ANMELDUNG_SERVICE_ID = 120686

# Without a user agent, you will get a 403
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
}

def get_appointment_dates(buergeramt_ids=ALL_BUERGERAMTS, service_id=ANMELDUNG_SERVICE_ID):
    """
    Retrieves a list of appointment dates from the Berlin.de website.
    :param buergeramt_ids: A list of IDs of burgeramts to check
    :service_id: The service ID of the desired service. This is a URL parameter - the service ID has no meaning.
    :returns: A list of date objects
    """
    buergeramt_ids = [str(bid) for bid in buergeramt_ids]
    params = {
        'termin': 1,  # Not sure if necessary
        'dienstleisterlist': ','.join(buergeramt_ids),
        'anliegen[]': service_id,
    }
    response = requests.get(BASE_URL + 'tag.php', params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    month_widgets = soup.find_all(class_='calendar-month-table')
    today = datetime.now().date()

    # Current month and next month
    available_dates = []
    for index, month_widget in enumerate(month_widgets):
        # Get a list of available dates for each calendar widget. The first widget shows the current month.
        displayed_month = (today.month + index) % 12
        available_day_links = month_widget.find_all('td', class_='buchbar')
        available_days = [int(link.find('a').text) for link in available_day_links]
        available_dates += [today.replace(month=displayed_month, day=available_day) for available_day in available_days]
    if (response.status_code == 200):
        print('Checked on %s and found %i appointments' % (datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), len(available_day_links)))
    else:
        print('%s - Status code' % response.status_code)
    return available_dates


def log_appointment_dates(dates):
    """
    Logs results in a file. Each line is written as a JSON object.
    Notifies the user if a date is found.
    """
    logging.basicConfig(filename='dates.log', format='%(message)s', level=logging.INFO)
    date_strings = [d.strftime('%Y-%m-%dT%H:%M:%S') for d in dates]
    logging.info(json.dumps({
    	'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    	'available_dates': date_strings
    }))
    if (len(dates)):
        pync.notify('Found %s available time(s)' % len(date_strings), title=TITLE, open=BASE_URL+'day/')


def observe(limit, polling_delay):
    """
    Polls for available appointments every [polling_delay] seconds for [limit] minutes/hours/days.
    :param limit: A timedelta. The observer will stop after this amount of time is elapsed
    :param polling_delay: The polling delay, in seconds.
    """
    start = datetime.now()
    duration = timedelta()
    while duration < limit:
        duration = datetime.now() - start
        log_appointment_dates(get_appointment_dates())
        time.sleep(polling_delay)


if __name__ == "__main__":
    pync.notify('Started looking for available times...', title=TITLE)
    observe(timedelta(days=30), polling_delay=60)