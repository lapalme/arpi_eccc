import os
import pprint
import sys
from datetime import datetime


def __load_timeranges():
    result = {}
    rsrc_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timeranges.txt')
    with open(rsrc_filename, 'rt', encoding='utf-8') as fin:
        for line in fin:
            parts = line.strip().split('|')
            assert len(parts) == 6
            region, issue_hour, _, start, end, period_name = parts
            result[region] = result.get(region, {'today': {}, 'tonight': {}, 'tomorrow': {}, 'tomorrow_night': {}})
            result[region][period_name][int(issue_hour)] = (int(start), int(end))

    return result


__PERIOD_TO_TIMERANGE = __load_timeranges()


def get_nb_tokens(bulletin: dict, lang: str) -> int:
    result = 0
    tok_dict = bulletin[lang]['tok']
    for k, sents in tok_dict.items():
        result += sum([len(cur_sent) for cur_sent in sents])
    return result


def pretty_print_bulletin(bulletin: dict, stm):
    print('=' * 120, file=stm)
    print(f"{bulletin['id']} : {' '.join([str(x) for x in bulletin['header']])}", file=stm)
    print('=' * 120, file=stm)

    for lang in ['en', 'fr']:
        print(lang + ' ' + ('-' * 117), file=stm)
        for period_name, sentences in bulletin[lang]['tok'].items():
            print(period_name + ': ' + '     '.join([' '.join(x) for x in sentences]), file=stm)
        print('-' * 120, file=stm)

    for field_name in ['accum', 'avert', 'ciel', 'climat_temp', 'indice_uv', 'pcpn', 'prob', 'rosee', 'temp', 'vents', 'visib']:
        if field_name in bulletin:
            print(field_name, file=stm)
            print('-' * 120, file=stm)
            pprint.pprint(bulletin[field_name], stream=stm)
            print('-' * 120, file=stm)


def dummy_nlg_english(bulletin: dict) -> dict:
    """
    A NLG system should return a dict with the same structure as that in the field bulletin['en' or 'fr']['tok'], i.e.
    the same periods (e.g. today) with the corresponding text, as list of sentences. Each sentence is a list of strings.

    :param bulletin: The input bulleting.
    :return: The NLG dict, for English here.
    """

    # we need to have the same periods as in the input
    result = {period_name: [] for period_name in bulletin['en']['tok'].keys()}

    # we provide dummy results
    for period_name, sentence_list in result.items():
        sentence_list.append(['Mainly', 'cloudy', '.'])  # first sentence for this period
        sentence_list.append(['Wind', 'up', 'to', '15', 'km/h', '.'])  # second sentence for this period

    return result


# taken from https://en.wikipedia.org/wiki/Daylight_saving_time_in_the_United_States
__DST2018 = (datetime(2018, 3, 11), datetime(2018, 11, 4))
__DST2019 = (datetime(2019, 3, 10), datetime(2019, 11, 3))

def get_delta_with_utc(bulletin):
    issue_date = datetime(bulletin['header'][4], bulletin['header'][5], bulletin['header'][6])
    is_dst = __DST2018[0] <= issue_date < __DST2018[1] or __DST2019[0] <= issue_date < __DST2019[1]
    return +4 if is_dst else +5
    

def get_time_interval_for_period(bulletin: dict, period: str) -> tuple:
    """
    Returns the time interval (start hour UTC, end hour UTC) for the given period.
    :param bulletin: The bulletin.
    :param period: One of `today`, `tonight`, `tomorrow`, `tomorrow_night`
    :return: A tuple (start hour, end hour) in UTC, i.e. the same timezone as the hours in the meteocode data.
    """
    issue_time_utc = bulletin['header'][7]  # e.g. 2045 (always UTC)
    # issue_date = datetime(bulletin['header'][4], bulletin['header'][5], bulletin['header'][6])
    # is_dst = __DST2018[0] <= issue_date < __DST2018[1] or __DST2019[0] <= issue_date < __DST2019[1]
    delta_with_utc = get_delta_with_utc(bulletin)
    issue_time_local = issue_time_utc - delta_with_utc * 100
    station = bulletin['header'][0]
    if period=="day_2":period="tomorrow"
    elif period=="day_2_night":period="tomorrow_night"

    try:
        local_range = __PERIOD_TO_TIMERANGE[station][period][issue_time_local]
    except KeyError:
        # this happens when a period is missing from the DB for a given issue_time_local. Recovery attempt necessary.
#         print(f"Invalid issue_time_local: {issue_time_local}", file=sys.stderr)
        periods = ['today', 'tonight', 'tomorrow', 'tomorrow_night']
        local_range = None
        for recovery_period in periods:
            if issue_time_local in __PERIOD_TO_TIMERANGE[station][recovery_period]:
                local_range = __PERIOD_TO_TIMERANGE[station][recovery_period][issue_time_local]
                # print(f"Recovered with {local_range}", file=sys.stderr)
                break

    utc_range = (local_range[0] + delta_with_utc, local_range[1] + delta_with_utc)
    return utc_range
