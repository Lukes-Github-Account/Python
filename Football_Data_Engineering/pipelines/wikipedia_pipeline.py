import json
import pandas as pd

NO_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
def get_wikipedia_page(url):
    import requests

    print("getting wikipedia page...", url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # check if request is successful

        return response.text
    except requests.RequestException as e:
        print(f"The following exception occurred: {e}")


def get_wikipedia_data(html):
    from bs4 import BeautifulSoup


    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find_all("table", {"class": "wikitable sortable"})[0]

    table_rows = table.find_all('tr')

    return table_rows


def clean_text(text):
    text = str(text).strip()
    text = text.replace('&nbsp', '')

    if text.find(' ♦'):
        text = text.split(' ♦')[0]
    if text.find('[') != -1:
        text = text.split('[')[0]
    if text.find('formerly') != -1:
        text = text.split(' (formerly)')[0]
    if text == '\n' :
        return ""

    return text.replace('\n', "")



def extract_wikipedia_data(**kwargs):

    url = kwargs['url']
    html = get_wikipedia_page(url)
    rows = get_wikipedia_data(html)

    print(rows)

    data = []

    for i in range(1, len(rows)):
        tds = rows[i].find_all('td')
        values = {
            'rank': i,
            'stadium': clean_text(tds[0].text),
            'capacity': clean_text(tds[1].text).replace(',', "").replace('.', ""),
            'region': clean_text(tds[2].text),
            'country': clean_text(tds[3].text),
            'city': clean_text(tds[4].text),
            'images': 'https://' + tds[5].find('img').get('src').split("//")[1] if tds[5].find('img') else "NO_IMAGE",
            'team': clean_text(tds[6].text),
        }
        data.append(values)

    json_rows = json.dumps(data)
    kwargs['ti'].xcom_push(key='rows', value= json_rows)
    return "OK"

#
# def get_lat_long(country, city):
#     from geopy import Nominatim
#     geolocator = Nominatim(user_agent='geoapiExercises')
#     location = geolocator.geocode(f"{city}, {country}")
#
#     if location:
#         return location.latitude, location.longitude
#
#     return None

def get_lat_long(country, city):

    import requests

    location = f"{city}, {country}"
    url = f'https://nominatim.openstreetmap.org/search?format=json&q={location}'

    response = requests.get(url)
    data = response.json()

    if data:
        return data[0]['lat'], data[0]['lon']

    return None

def transform_wikipedia_data(**kwargs):

    data = kwargs['ti'].xcom_pull(key='rows', task_ids='extract_data_from_wikipedia')

    data = json.loads(data)

    stadiums_df = pd.DataFrame(data)
    stadiums_df['location'] = stadiums_df.apply(lambda x: get_lat_long(x['country'], x['stadium']), axis=1)
    stadiums_df['images'] = stadiums_df['images'].apply(lambda x: x if x not in ['NO_IMAGE', '', None] else NO_IMAGE)
    stadiums_df['capacity'] = stadiums_df['capacity'].astype(int)

    #handle duplicates
    duplicates = stadiums_df[stadiums_df.duplicated(['location'])]
    duplicates['location'] = duplicates.apply(lambda x: get_lat_long(x['country'], x['city']), axis=1)
    stadiums_df.update(duplicates)

    #push to xcom
    kwargs['ti'].xcom_push(key='rows', value=stadiums_df.to_json())

    return "OK"


def write_wikipedia_data(**kwargs):
    from datetime import datetime

    data = kwargs['ti'].xcom_pull(key='rows', task_ids='transform_wikipedia_data')

    if data is not None:  # Add this check
        data = json.loads(data)
        data = pd.DataFrame(data)

        file_name = ('stadium_cleaned_' + str(datetime.now().date()) + "_" +
                     str(datetime.now().time()).replace(":", "_") + '.csv')

        # data.to_csv('data/' + file_name, index=False
        data.to_csv('abfs://footballdataengineering@footballdataengineering.dfs.core.windows.net/data/' + file_name,
                    storage_options={
                        'account_key': 'FR7c0ZIwnxIPUy9oTvovs2eBvtf+4naHcb4JavKUZ1rb7vlAWQW0WUHUtNxFPrpZuoRrvJ7j3gpj+ASt1et5VA=='
                    }, index=False)


    else:
        print("No data retrieved from XCom. Exiting without writing to file.")

    # data = json.loads(data)
    # data = pd.DataFrame(data)
    #
    # file_name = ('stadium_cleaned_' + str(datetime.now().date()) + "_" +
    #              str(datetime.now().time()).replace(":", "_") + 'csv')
    #
    # data.to_csv('data/' + file_name, index=False)
    #


# get_date = get_wikipedia_page("https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg")
