#!/usr/bin/env python3
import argparse
import base64
import binascii
import json
import os
import sys
from pathlib import Path

from simple_term_menu import TerminalMenu

"""
top_level_ctors = ['PlayerSave', 'AllServersSave',
                   'CompaniesSave', 'FactionsSave',
                   'AliasesSave', 'GlobalAliasesSave',
                   'MessagesSave', 'StockMarketSave',
                   'SettingsSave', 'VersionSave',
                   'AllGangsSave', 'LastExportBonus',
                   'StaneksGiftSave', 'SaveTimestamp']
"""


class EditPlayerData:
    def __init__(self, bitburner_save_data):
        self.bitburner_save_data = bitburner_save_data
        self.jdata = None

    def __enter__(self):
        self.jdata = json.loads(self.bitburner_save_data.get('PlayerSave'))
        player_data = self.jdata.get('data')
        return player_data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bitburner_save_data['PlayerSave'] = json.dumps(self.jdata)


class BitBurnerSaveModifier:
    def __init__(self, raw_data, verbose=False):
        self.verbose = verbose
        self.raw_data = raw_data
        self.outer_save = json.loads(raw_data)
        name = self.outer_save.get('ctor')
        data = self.outer_save.get('data')
        if name and data:
            if 'BitburnerSaveObject' == name:
                self.bitburner_save_data = data
                return

        raise Exception('Couldn\'t load save data')

    def join_all_factions(self):
        jdata = json.loads(self.bitburner_save_data.get('FactionsSave'))
        factions = []
        for faction in jdata:
            print(f'Editing {faction}')
            factions.append(faction)
            jdata[faction]['data']['alreadyInvited'] = True
            jdata[faction]['data']['isMember'] = True
            jdata[faction]['data']['isBanned'] = False
            jdata[faction]['data']['favor'] = 50000
            jdata[faction]['data']['playerReputation'] = 1000000 * 100
            if self.verbose:
                print(f'    Setting favor: {jdata[faction]["data"]["favor"]}')
                print(f'    Setting Reputation: {jdata[faction]["data"]["playerReputation"]}')
        self.bitburner_save_data['FactionsSave'] = json.dumps(jdata)

        with EditPlayerData(self.bitburner_save_data) as player_data:
            player_data['factions'] = factions

    def upgrade_home_server(self):
        jdata = json.loads(self.bitburner_save_data.get('AllServersSave'))
        print('Modifying home Server Data')
        jdata['home']['data']['cpuCores'] = 2 ** 10
        jdata['home']['data']['maxRam'] = 2 ** 30
        print('  Adding programs to home PC...')
        jdata['home']['data']['programs'] = ['NUKE.exe', 'b1t_flum3.exe', 'Formulas.exe',
                                             'BruteSSH.exe', 'FTPCrack.exe', 'relaySMTP.exe',
                                             'HTTPWorm.exe', 'SQLInject.exe', 'HTTPWorm.exe',
                                             'ServerProfiler.exe', 'DeepscanV1.exe', 'DeepscanV2.exe', 'AutoLink.exe']
        if self.verbose:
            print(f'    Setting cpuCores: {jdata["home"]["data"]["cpuCores"]}')
            print(f'    Setting maxRam: {jdata["home"]["data"]["maxRam"]}')

        self.bitburner_save_data['AllServersSave'] = json.dumps(jdata)

    def upgrade_player_stats(self):
        with EditPlayerData(self.bitburner_save_data) as player_data:
            value = 1.0 * 1000000 * 1000000 * 1000000 * 1000000
            player_data['hacking_exp'] = value * 1000000 * 1000000
            player_data['strength_exp'] = value
            player_data['defense_exp'] = value
            player_data['dexterity_exp'] = value
            player_data['agility_exp'] = value
            player_data['charisma_exp'] = value
            player_data['intelligence_exp'] = player_data['intelligence_exp'] * 2 * 2 * 2 * 2

    def enable_stanek_gift(self):
        with EditPlayerData(self.bitburner_save_data) as player_data:
            print("Adding Stanek's Gift Augments")
            stanek_level1 = {'level': 1, 'name': "Stanek's Gift - Genesis"}
            stanek_level2 = {'level': 1, 'name': "Stanek's Gift - Awakening"}
            stanek_level3 = {'level': 1, 'name': "Stanek's Gift - Serenity"}

            desired_augments = [stanek_level1, stanek_level2, stanek_level3]
            for i in desired_augments:
                if i not in player_data['augmentations']:
                    if self.verbose:
                        print(f'    Adding {i}')
                    player_data['augmentations'].append(i)

    def modify_last_update_timestamp(self, days=7):
        with EditPlayerData(self.bitburner_save_data) as player_data:
            print(f'Modifying lastUpdate save game timestamp - {days} days')
            player_data['lastUpdate'] = player_data['lastUpdate'] - 1000 * 60 * 60 * 24 * days

    def export_player_save_data(self):
        self.outer_save['data'] = self.bitburner_save_data
        return json.dumps(self.outer_save)

    def give_player_money(self):
        with EditPlayerData(self.bitburner_save_data) as player_data:
            value = 1.0 * 1000000 * 1000000 * 1000000 * 1000000
            player_data['money'] = value

    def bad_karma(self):
        with EditPlayerData(self.bitburner_save_data) as player_data:
            player_data['karma'] = -60000

    def enable_stock_market_access(self):
        with EditPlayerData(self.bitburner_save_data) as player_data:
            # Stock market access
            player_data['hasWseAccount'] = True
            player_data['hasTixApiAccess'] = True
            player_data['has4SData'] = True
            player_data['has4SDataTixApi'] = True


def main():
    parser = argparse.ArgumentParser(description='Edit BitBurner Save game files')
    group_main = parser.add_mutually_exclusive_group()
    group_main.add_argument('-s', '--save', help='Save game file')
    group_main.add_argument('-d', '--directory', help='Save game directory (find latest version)')
    parser.add_argument('--manual', action='store_true', help='Edit file contents manually')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose prints')
    args = parser.parse_args()

    save_file = None
    if args.save:
        save_file = Path(args.save)
    else:
        save_dir = Path(args.directory)
        files = save_dir.glob('bitburnerSave_*.json')
        for i in reversed(sorted(list(files))):
            save_file = i
            break

    if not save_file:
        print(f'ERROR, couldn\'t locate save file to use')
        sys.exit(1)
    else:
        print(f'Using save game file: {save_file}')

    new_save_filename = f'{save_file.stem}_modified.json'

    with open(save_file, 'rb') as f:
        dataString = f.read()
        dataBytes = dataString

    try:
        decoded = base64.b64decode(dataBytes)
    except binascii.Error as e:
        print(f'Sorry, looks like the file contents wasn\'t base64 encoded: \n\t{e}')
        sys.exit(1)

    if args.manual:
        intermediate_filename = 'intermediate'

        with open(intermediate_filename, 'wb') as f:
            f.write(decoded)

        input(f"Please manually edit {intermediate_filename}, then Press Enter to continue...")

        with open(intermediate_filename, 'rb') as f:
            decoded = f.read()
        os.unlink(intermediate_filename)
        encoded = base64.b64encode(decoded)
    else:
        bb_inst = BitBurnerSaveModifier(decoded, verbose=args.verbose)

        MAX_HOME = 'Max home pc resources'
        JOIN_ALL = 'Join all factions'
        MONEY = 'Give player lots of money'
        CHANGE_SAVE_TIME = 'Change save game time'
        STANEK_GIFT = 'Add stanek gift augmentations'
        BAD_KARMA = 'Set karma to -60000'
        GIVE_STOCK_ACCESS = 'Enable stock market access'
        INCREASE_STATS = 'Increase all experience stats'

        terminal_menu = TerminalMenu(
            [MAX_HOME, JOIN_ALL, MONEY, CHANGE_SAVE_TIME, STANEK_GIFT, BAD_KARMA, GIVE_STOCK_ACCESS, INCREASE_STATS],
            multi_select=True,
            show_multi_select_hint=True,
        )
        _ = terminal_menu.show()

        if MAX_HOME in terminal_menu.chosen_menu_entries:
            bb_inst.upgrade_home_server()
        if JOIN_ALL in terminal_menu.chosen_menu_entries:
            bb_inst.join_all_factions()
        if STANEK_GIFT in terminal_menu.chosen_menu_entries:
            bb_inst.enable_stanek_gift()
        if CHANGE_SAVE_TIME in terminal_menu.chosen_menu_entries:
            bb_inst.modify_last_update_timestamp(days=7)
        if MONEY in terminal_menu.chosen_menu_entries:
            bb_inst.give_player_money()
        if BAD_KARMA in terminal_menu.chosen_menu_entries:
            bb_inst.bad_karma()
        if GIVE_STOCK_ACCESS in terminal_menu.chosen_menu_entries:
            bb_inst.enable_stock_market_access()
        if INCREASE_STATS in terminal_menu.chosen_menu_entries:
            bb_inst.upgrade_player_stats()

        modified = bb_inst.export_player_save_data()
        jstring = modified.encode('ascii')
        encoded = base64.b64encode(jstring)

    print(f'Writing out new save data to: {new_save_filename}')
    with open(new_save_filename, 'wb') as f:
        f.write(encoded)


if __name__ == '__main__':
    main()
