from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import json
import logging
import time


ALL_BUERGERAMTS = (
    122210, 122217, 122219, 122227, 122231, 122238, 122243, 122252, 122260, 122262, 122254, 122271, 122273, 122277,
    122280, 122282, 122284, 122291, 122285, 122286, 122296, 150230, 122301, 122297, 122294, 122312, 122314, 122304,
    122311, 122309, 317869, 324433, 325341, 324434, 122281, 122283, 122279, 122276, 122274, 122267, 122246, 122251,
    122257, 122208, 122226
)

ANMELDUNG_SERVICE_ID = 120335

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
        'anliegen': (service_id, ),
    }
    response = requests.get('https://service.berlin.de/terminvereinbarung/termin/tag.php', params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    month_widgets = soup.find_all(class_='calendar-month-table')
    today = datetime.now().date()

    # Current month and next month
    available_dates = []
    for index, month_widget in enumerate(month_widgets):
        # Get a list of available dates for each calendar widget. The first widget shows the current month.
        displayed_month = (today.month + index) % 12
        available_day_links = month_widget.find_all('a', class_='tagesauswahl')
        available_days = [int(link.find('span').text) for link in available_day_links]
        available_dates += [today.replace(month=displayed_month, day=available_day) for available_day in available_days]

    return available_dates


def log_appointment_dates(dates):
    """
    Writes the appointment dates in a file. Each line is written as a JSON object.
    """
    logging.basicConfig(filename='dates.log', format='%(message)s', level=logging.INFO)
    date_strings = [d.strftime('%Y-%m-%dT%H:%M:%S') for d in dates]
    logging.info(json.dumps({
    	'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    	'available_dates': date_strings
    }))


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
    observe(timedelta(days=30), polling_delay=60)