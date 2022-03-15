from django.http import HttpResponse
from django.shortcuts import render
import requests
import json
from datetime import date
from datetime import timedelta


def get_web_data():
    for day in range(7):
        date_in_web = (date.today() - timedelta(days=day)).strftime("%d/%m/%Y")
        Occupancy_of_quarantine_centres = {
            "resource": "http://www.chp.gov.hk/files/misc/occupancy_of_quarantine_centres_eng.csv",
            "section": 1,
            "format": "json",
            "sorts": [
                [8, "desc"]
            ],
            "filters": [
                [1, "eq", [date_in_web]]
            ]
        }
        Occupancy_of_quarantine_centres_string = json.dumps(Occupancy_of_quarantine_centres)
        response_Occupancy_of_quarantine_centres = requests.get(
            "https://api.data.gov.hk/v2/filter",
            params={'q': Occupancy_of_quarantine_centres_string})
        Occupancy_of_quarantine_centres_result = response_Occupancy_of_quarantine_centres.json()
        Number_of_confines_by_types_in_the_quarantine_centres = {
            "resource": "http://www.chp.gov.hk/files/misc/no_of_confines_by_types_in_quarantine_centres_eng.csv",
            "section": 1,
            "format": "json",
            "filters": [
                [1, "eq", [date_in_web]]
            ]
        }
        Number_of_confines_by_types_in_the_quarantine_centres_string = json.dumps(
            Number_of_confines_by_types_in_the_quarantine_centres)
        response_Number_of_confines_by_types_in_the_quarantine_centres = requests.get(
            "https://api.data.gov.hk/v2/filter",
            params={'q': Number_of_confines_by_types_in_the_quarantine_centres_string})
        Number_of_confines_by_types_in_the_quarantine_centres_result = response_Number_of_confines_by_types_in_the_quarantine_centres.json()
        if len(Occupancy_of_quarantine_centres_result) != 0 and len(
                Number_of_confines_by_types_in_the_quarantine_centres_result) != 0:
            return True, True, Occupancy_of_quarantine_centres_result, Number_of_confines_by_types_in_the_quarantine_centres_result
    return True, False, None, None


def sum_of_unit_in_use_and_available_and_total_quarantined(OOQC):
    Quarantine_units_in_use = 0
    Quarantine_units_available = 0
    total_number_of_persons_quarantined = 0
    for centre in OOQC:
        Quarantine_units_in_use += centre['Current unit in use']
        Quarantine_units_available += centre['Ready to be used (unit)']
        total_number_of_persons_quarantined += centre['Current person in use']

    return Quarantine_units_in_use, Quarantine_units_available, total_number_of_persons_quarantined


def top_3(OOQC):
    top_3_centre = []
    count = 0
    for centre in OOQC:
        top_3_centre.append({'name': centre['Quarantine centres'],
                             'units': centre['Ready to be used (unit)']})
        count += 1
        if count == 3:
            break
    return top_3_centre


def check_same_sum(OOQC, NOCBTITQC):
    total_people_OOQC = 0
    total_people_NOCBTITQC = 0
    for centre in OOQC:
        total_people_OOQC += centre['Current person in use']
    total_people_NOCBTITQC = NOCBTITQC[0]['Current number of close contacts of confirmed cases'] + NOCBTITQC[0][
        'Current number of non-close contacts']
    return True if total_people_OOQC == total_people_NOCBTITQC else False


def view_data_date(request):
    connected, has_data, OOQC, NOCBTITQC = get_web_data()
    Quarantine_units_in_use, Quarantine_units_available, total_number_of_persons_quarantined = sum_of_unit_in_use_and_available_and_total_quarantined(
        OOQC)
    top_3_centre = top_3(OOQC)
    context = {'connected': connected,
               'has_data': has_data,
               'data': {'date': NOCBTITQC[0]['As of date'],
                        'units_in_use': Quarantine_units_in_use,
                        'units_available': Quarantine_units_available,
                        'persons_quarantined': total_number_of_persons_quarantined,
                        'non_close_contacts': NOCBTITQC[0]['Current number of non-close contacts'],
                        'count_consistent': check_same_sum(OOQC, NOCBTITQC)
                        },
               'centres': top_3_centre
               }
    return render(request, 'dashboard3.html', context=context)
