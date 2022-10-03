from typing import List, Dict
from celery.utils.log import get_task_logger
import os

import requests

from googleapiclient.discovery import build
from google.oauth2 import service_account

from app.models import DataBase
from sheet_task import settings
from sheet_task.celery import app
from datetime import datetime, timedelta
import defusedxml.ElementTree as ET

logger = get_task_logger(__name__)


def get_file_path(file_credentials):
    """Concatenate the path with the filename"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(BASE_DIR, file_credentials)


def get_service_sheet(sheets: str = None, vers: str = None, file_credentials: str = None, scopes: str = None):
    """Read google sheets"""
    service_account_file = get_file_path(file_credentials)
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes)
    service = build(sheets, vers, credentials=credentials, cache_discovery=False).spreadsheets().values()
    return service


def read_sheet(service=None, sheets_id: str = None, range_row: str = None):
    result = service.get(spreadsheetId=sheets_id,
                         range=range_row).execute()
    data_from_sheet = result.get('values')
    return data_from_sheet



@app.task(bind=True)
def read_and_google_sheets(*args, sheets: str = 'sheets', vers: str = 'v4', file_credentials: str = '',
                                 scopes: List = None, sheets_id: str = None, range_row: str = None) -> Dict:
    """Reading processing and writing to the database"""
    service = get_service_sheet(sheets=sheets, vers=vers, file_credentials=file_credentials, scopes=scopes)
    data_from_sheet = read_sheet(service=service, sheets_id=sheets_id, range_row=range_row)
    """Writing to the database"""
    list_data = []
    # list_obj_database = []
    # date_min = datetime.now() + timedelta(days=30000)
    # date_max = datetime.now() - timedelta(days=30000)
    for count, element in enumerate(data_from_sheet[1:], start=2):
        column_number, order_number, order_cost, delivery_time_str = element
        delivery_time_data = datetime.strptime(delivery_time_str, '%d.%m.%Y')
        # obj, _ = DataBase.objects.create(delivery_time=delivery_time_data.date(), order_cost=order_cost,
        #                                  column_number=column_number, order_number=order_number, column_index=count)
    #     """MIN MAX DATE"""
    #     if delivery_time_data > date_max:
    #         date_max = delivery_time_data
    #     elif delivery_time_data < date_min:
    #         date_min = delivery_time_data
    #     list_obj_database.append(list_obj_database)
        list_data.append(DataBase(delivery_time=delivery_time_data.date(), order_cost=order_cost,
                                         column_number=column_number, order_number=order_number, column_index=count))
    DataBase.objects.bulk_create(list_data)


def valid_date_in_requests(list_keys: List, min_date=None, max_date=None):
    max_bool, min_bool = True, True
    if not max_date <= list_keys[0]:
        max_date += timedelta(days=5)
        max_bool = False
    elif not min_date >= list_keys[-1]:
        min_date -= timedelta(days=5)
        min_bool = False
    return max_bool and min_bool, max_date, min_date


def parse_response_CBR(response):
    DICT_DATA_CURRENCY = {}
    tree = ET.fromstring(response.text)
    for el in tree.findall('Record'):
        DICT_DATA_CURRENCY[datetime.strptime(el.attrib.get('Date'), '%d.%m.%Y').date()] = el.find('Value').text.replace(
            ',', '.')
    return dict(sorted(DICT_DATA_CURRENCY.items(), reverse=True))


def create_requestsCBR(*args, currency_id: str = 'R01235', url_pattern: str = None, number_of_attempts=5):
    attempts = 0
    dict_data_currency = {}
    map_data = list(map(lambda x: x.strftime("%d/%m/%Y"), args))

    url = url_pattern.format(*map_data, currency_id)
    min_data, max_data = args
    while attempts <= number_of_attempts:
        response = requests.get(url)
        if response.status_code == 200:
            dict_data_currency = parse_response_CBR(response)
            list_keys = list(dict_data_currency.keys())
            bool_response, data_min, data_max = valid_date_in_requests(list_keys, min_data, max_data)
            if bool_response:
                return dict_data_currency
        attempts += 1
    else:
        return dict_data_currency


def gen_data(dict_data_currency: Dict, obj_delivery_time=None):
    for key, value in dict_data_currency.items():
        if obj_delivery_time >= key:
            return value


def update_base_objects(data_base_object, dict_data_currency: Dict):
    update_bulk_list = []
    for obj in data_base_object.all():
        value_currency = gen_data(dict_data_currency, obj.delivery_time)
        if value_currency:
            obj.rate = value_currency
            update_bulk_list.append(obj)
    DataBase.objects.bulk_update(update_bulk_list, ['rate'])


@app.task(bind=True)
def request_api_cbr(*args, currency_id: str = 'R01235', url_pattern: str = None):
    data_base_object = DataBase.objects
    if data_base_object.exists():
        max_data = data_base_object.first().delivery_time
        min_data = data_base_object.last().delivery_time
        dict_data_currency = create_requestsCBR(min_data, max_data, url_pattern=url_pattern, currency_id=currency_id)
        update_base_objects(data_base_object, dict_data_currency)

def batchUpdate_service(service=None, sheets_id: str = None, range_row: str = None, values=None):
    service.batchUpdate(
        spreadsheetId=sheets_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": range_row,
                 "majorDimension": "ROWS",
                 "values": [[values], ]},
            ]
        }
    ).execute()


@app.task(bind=True)
def write_sheets(*args, sheets: str = 'sheets', vers: str = 'v4', file_credentials: str = '',
                                 scopes: List = None, sheets_id: str = None, range_row: str = None, values: str = None):

    service = get_service_sheet(sheets=sheets, vers=vers, file_credentials=file_credentials, scopes=scopes)
    batchUpdate_service(service, sheets_id, range_row, values=values)
