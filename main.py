#!/usr/bin/env python3

"""
Credit to https://rocketleaguestats.com for maintaining the API that we use
to update our user statistics within TAW.
"""

__author__ = "Steven Lakin"
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "steven.m.lakin@gmail.com"
__status__ = "Beta"


from taw_rlg_rest.TawRlgRest import TawRlgRest


TRN_RLG_API_URL = r'https://api.rocketleaguestats.com/v1/player'
TAW_STEAM_GROUP_URL = R'http://steamcommunity.com/groups/TAWRLG/memberslistxml?xml=1'


if __name__ == '__main__':
    with open('D:\\1TAW\\api.txt', 'r') as f:
        k = f.read().strip()
    with open('D:\\1TAW\\spreadsheet_id.txt', 'r') as f:
        sid = f.read().strip()
    TRR = TawRlgRest(r'https://api.rocketleaguestats.com/v1/player', sid, k,
                    r'http://steamcommunity.com/groups/TAWRLG/memberslistxml?xml=1')
    TRR.get_taw_player_ids()
    TRR.retrieve_player_stats()
    TRR.update_local_player_stats()
