from __future__ import print_function
import requests
import time
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from xlsxwriter.utility import xl_rowcol_to_cell
from xml.etree import ElementTree


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'D:\\1TAW\\client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def remove_non_ascii(string):
    return ''.join([i if ord(i) < 128 else ' ' for i in string])


class TawRlgRest(object):
    def __init__(self, query_url, result_url, api_key, taw_group_url):
        self.taw_group_url = taw_group_url
        self.query_url = query_url
        self.result_url = result_url
        self.player_id_list = []
        self.api_key = str(api_key)
        self.player_stats = {}
        self.tier_names = {
            0: 'Unranked',
            1: 'BronzeI',
            2: 'BronzeII',
            3: 'BronzeIII',
            4: 'SilverI',
            5: 'SilverII',
            6: 'SilverIII',
            7: 'GoldI',
            8: 'GoldII',
            9: 'GoldIII',
            10: 'PlatinumI',
            11: 'PlatinumII',
            12: 'PlatinumIII',
            13: 'DiamondI',
            14: 'DiamondII',
            15: 'DiamondIII',
            16: 'ChampionI',
            17: 'ChampionII',
            18: 'ChampionIII',
            19: 'Grand Champion'
        }
        self.division_names = {
            0: 'DivisionI',
            1: 'DivisionII',
            2: 'DivisionIII',
            3: 'DivisionIV'
        }

    def get_taw_player_ids(self):
        response = requests.get(self.taw_group_url)
        tree = ElementTree.ElementTree(ElementTree.fromstring(response.content))
        root = tree.getroot()[6]
        for memberID in root.iter('steamID64'):
            self.player_id_list.append(memberID.text)

    def retrieve_player_stats(self):
        for player_id in self.player_id_list:
            print(player_id)
            params = {'unique_id': player_id, 'platform_id': '1'}
            headers = {'Authorization': self.api_key}
            response = requests.get(self.query_url, params=params, headers=headers)
            if response.status_code == requests.codes.ok:
                data = response.json()
                self.player_stats.setdefault(
                    data['uniqueId'], {'overall_stats': [data['displayName'],
                                       data['profileUrl'],
                                       data['stats']['wins'],
                                       data['stats']['goals'],
                                       data['stats']['mvps'],
                                       data['stats']['saves'],
                                       data['stats']['shots'],
                                       data['stats']['assists']],
                                       '1v1': {'MMR': 0, 'Matches': 0, 'Tier': 0, 'Division': 0},
                                       '2v2': {'MMR': 0, 'Matches': 0, 'Tier': 0, 'Division': 0},
                                       'Solo3v3': {'MMR': 0, 'Matches': 0, 'Tier': 0, 'Division': 0},
                                       'Standard3v3': {'MMR': 0, 'Matches': 0, 'Tier': 0, 'Division': 0}}
                )
                if len(data['rankedSeasons']) > 0:
                    max_season = max([int(x) for x in data['rankedSeasons'].keys()])
                    if max_season > 3:
                        if '10' in data['rankedSeasons'][str(max_season)]:
                            self.player_stats[data['uniqueId']]['1v1']['MMR'] = data['rankedSeasons'][str(max_season)]['10']['rankPoints']
                            self.player_stats[data['uniqueId']]['1v1']['Matches'] = data['rankedSeasons'][str(max_season)]['10']['matchesPlayed']
                            self.player_stats[data['uniqueId']]['1v1']['Tier'] = data['rankedSeasons'][str(max_season)]['10']['tier']
                            self.player_stats[data['uniqueId']]['1v1']['Division'] = data['rankedSeasons'][str(max_season)]['10']['division']
                        if '11' in data['rankedSeasons'][str(max_season)]:
                            self.player_stats[data['uniqueId']]['2v2']['MMR'] = data['rankedSeasons'][str(max_season)]['11']['rankPoints']
                            self.player_stats[data['uniqueId']]['2v2']['Matches'] = data['rankedSeasons'][str(max_season)]['11']['matchesPlayed']
                            self.player_stats[data['uniqueId']]['2v2']['Tier'] = data['rankedSeasons'][str(max_season)]['11']['tier']
                            self.player_stats[data['uniqueId']]['2v2']['Division'] = data['rankedSeasons'][str(max_season)]['11']['division']
                        if '12' in data['rankedSeasons'][str(max_season)]:
                            self.player_stats[data['uniqueId']]['Solo3v3']['MMR'] = data['rankedSeasons'][str(max_season)]['12']['rankPoints']
                            self.player_stats[data['uniqueId']]['Solo3v3']['Matches'] = data['rankedSeasons'][str(max_season)]['12']['matchesPlayed']
                            self.player_stats[data['uniqueId']]['Solo3v3']['Tier'] = data['rankedSeasons'][str(max_season)]['12']['tier']
                            self.player_stats[data['uniqueId']]['Solo3v3']['Division'] = data['rankedSeasons'][str(max_season)]['12']['division']
                        if '13' in data['rankedSeasons'][str(max_season)]:
                            self.player_stats[data['uniqueId']]['Standard3v3']['MMR'] = data['rankedSeasons'][str(max_season)]['13']['rankPoints']
                            self.player_stats[data['uniqueId']]['Standard3v3']['Matches'] = data['rankedSeasons'][str(max_season)]['13']['matchesPlayed']
                            self.player_stats[data['uniqueId']]['Standard3v3']['Tier'] = data['rankedSeasons'][str(max_season)]['13']['tier']
                            self.player_stats[data['uniqueId']]['Standard3v3']['Division'] = data['rankedSeasons'][str(max_season)]['13']['division']
                    else:
                        if '10' in data['rankedSeasons'][str(max_season)]:
                            self.player_stats[data['uniqueId']]['1v1']['MMR'] = data['rankedSeasons'][str(max_season)]['10']['rankPoints']
                        if '11' in data['rankedSeasons'][str(max_season)]:
                            self.player_stats[data['uniqueId']]['2v2']['MMR'] = data['rankedSeasons'][str(max_season)]['11']['rankPoints']
                        if '12' in data['rankedSeasons'][str(max_season)]:
                            self.player_stats[data['uniqueId']]['Solo3v3']['MMR'] = data['rankedSeasons'][str(max_season)]['12']['rankPoints']
                        if '13' in data['rankedSeasons'][str(max_season)]:
                            self.player_stats[data['uniqueId']]['Standard3v3']['MMR'] = data['rankedSeasons'][str(max_season)]['13']['rankPoints']
            else:
                print('Error: status code of {} for player {}'.format(response.status_code, player_id))
            time.sleep(0.75)

    def update_local_player_stats(self):
        sheet_headers = ['\"SteamName', 'SteamProfileLink', 'TrackerLink',
                         '1v1 Matches', '1v1 MMR', '1v1 Tier', '1v1 Division',
                         '2v2 Matches', '2v2 MMR', '2v2 Tier', '2v2 Division',
                         'Solo 3v3 Matches', 'Solo 3v3 MMR', 'Solo 3v3 Tier', 'Solo 3v3 Division',
                         'Standard 3v3 Matches', 'Standard 3v3 MMR', 'Standard 3v3 Tier', 'Standard 3v3 Division',
                         'Wins', 'Goals', 'MVPs', 'Saves', 'Shots', 'Assists\"']
        data = [sheet_headers]

        for k, d in self.player_stats.items():
            row_data = ['\"' + str(d['overall_stats'][0]),
                        '=HYPERLINK(\"\"http://steamcommunity.com/profiles/{}\"\", \"\"Steam Profile\"\")'.format(k),
                        '=HYPERLINK(\"\"{}\"\", \"\"Tracker Profile\"\")'.format(d['overall_stats'][1]),
                        d['1v1']['Matches'], d['1v1']['MMR'], self.tier_names[d['1v1']['Tier']],
                        self.division_names[d['1v1']['Division']],
                        d['2v2']['Matches'], d['2v2']['MMR'], self.tier_names[d['2v2']['Tier']],
                        self.division_names[d['2v2']['Division']],
                        d['Solo3v3']['Matches'], d['Solo3v3']['MMR'], self.tier_names[d['Solo3v3']['Tier']],
                        self.division_names[d['Solo3v3']['Division']],
                        d['Standard3v3']['Matches'], d['Standard3v3']['MMR'], self.tier_names[d['Standard3v3']['Tier']],
                        self.division_names[d['Standard3v3']['Division']],
                        d['overall_stats'][2], d['overall_stats'][3], d['overall_stats'][4], d['overall_stats'][5],
                        d['overall_stats'][6], str(d['overall_stats'][7]) + '\"']
            if row_data[5] == 'Unranked':
                row_data[6] = 'Unranked'
            if row_data[9] == 'Unranked':
                row_data[10] = 'Unranked'
            if row_data[13] == 'Unranked':
                row_data[14] = 'Unranked'
            if row_data[17] == 'Unranked':
                row_data[18] = 'Unranked'
            data.append(row_data)
        with open('D:\\1TAW\\current_player_stats.csv', 'w') as out:
            for row in data:
                try:
                    out.write('\",\"'.join([str(x) for x in row]) + '\n')
                except UnicodeEncodeError as e:
                    print(row, e)
                    for i, x in enumerate(row):
                        row[i] = remove_non_ascii(str(x))
                    out.write('\",\"'.join(row) + '\n')

    def update_remote_player_stats(self):
        # Not yet working
        sheet_headers = ['SteamName', 'SteamProfileLink', 'TrackerLink',
                         '1v1 Matches', '1v1 MMR', '1v1 Tier', '1v1 Division',
                         '2v2 Matches', '2v2 MMR', '2v2 Tier', '2v2 Division',
                         'Solo 3v3 Matches', 'Solo 3v3 MMR', 'Solo 3v3 Tier', 'Solo 3v3 Division',
                         'Standard 3v3 Matches', 'Standard 3v3 MMR', 'Standard 3v3 Tier', 'Standard 3v3 Division',
                         'Wins', 'Goals', 'MVPs', 'Saves', 'Shots', 'Assists']

        data = [sheet_headers]

        for k, d in self.player_stats.items():
            row_data = [d['overall_stats'][0], k, '=HYPERLINK({})'.format(d['overall_stats'][1]),
                        d['1v1']['Matches'], d['1v1']['MMR'], self.tier_names[d['1v1']['Tier']], self.division_names[d['1v1']['Division']],
                        d['2v2']['Matches'], d['2v2']['MMR'], self.tier_names[d['2v2']['Tier']], self.division_names[d['2v2']['Division']],
                        d['Solo3v3']['Matches'], d['Solo3v3']['MMR'], self.tier_names[d['Solo3v3']['Tier']], self.division_names[d['Solo3v3']['Division']],
                        d['Standard3v3']['Matches'], d['Standard3v3']['MMR'], self.tier_names[d['Standard3v3']['Tier']], self.division_names[d['Standard3v3']['Division']],
                        d['overall_stats'][2], d['overall_stats'][3], d['overall_stats'][4], d['overall_stats'][5],
                        d['overall_stats'][6], d['overall_stats'][7]]
            data.append(row_data)

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

        cell_range_end = xl_rowcol_to_cell(len(self.player_stats)+1, 25)
        rangeName = 'Sheet1!A1:' + cell_range_end
        result = service.spreadsheets().values().update(
            spreadsheetId=self.result_url, range=rangeName, body=data).execute()
        #values = result.update('values', data)

        # if not values:
        #     print('No data found.')
        # else:
        #     print('Name, Major:')
        #     for row in values:
        #         # Print columns A and E, which correspond to indices 0 and 4.
        #         print('%s, %s' % (row[0], row[4]))


if __name__ == '__main__':
    with open('D:\\1TAW\\api.txt', 'r') as f:
        k = f.read().strip()
    with open('D:\\1TAW\\spreadsheet_id.txt', 'r') as f:
        sid = f.read().strip()
    tr = TawRlgRest(r'https://api.rocketleaguestats.com/v1/player', sid, k,
                    r'http://steamcommunity.com/groups/TAWRLG/memberslistxml?xml=1')