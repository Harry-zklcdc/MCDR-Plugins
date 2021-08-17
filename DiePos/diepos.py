# -*- coding: utf-8 -*-

import re

from typing import Any, Tuple
from mcdreforged.api.all import *

PLUGIN_METADATA = {
    'id': 'die_position',
    'version': '1.0.0',
    'name': 'Die Position',
    'description': ' MCDR',
    'author': ['57767598', 'Fallen_Breath', 'Harry-zklcdc'],
    'link': 'https://github.com/Harry-zklcdc/MCDR-Plugins/tree/main/DiePos',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
    'minecraft_data_api': '*',
    'more_apis': '*',
    }
}

config = {
    'display_voxel_waypoint': True,
    'display_xaero_waypoint': True,
    'click_to_teleport': False
}

# variant for functionality demo
counter = 0
die_user = 0
die_name = []
playerlist = []

dimension_display = {
    '0': 'createWorld.customize.preset.overworld',
    '-1': 'advancements.nether.root.title',
    '1': 'advancements.end.root.title'
}

dimension_color = {
    '0': RColor.dark_green,
    '-1': RColor.dark_red,
    '1': RColor.dark_purple
}

def on_load(server: ServerInterface, old_module):
    server.register_event_listener('more_apis.death_message', on_death_message)

def on_death_message(server: ServerInterface, death_message: str):
    global die_user
    global die_name
    die_user+=1
    try:
        die_name.remove(death_message.split(" ")[0])
    except:
        pass
    die_name.append(death_message.split(" ")[0])
    if death_message.split(" ")[0] != '':
        server.execute('data get entity ' + death_message.split(" ")[0])

def on_info(server, info):
    global die_user
    global die_name
    dimension_convert = {"0":"主世界","-1":"地狱","1":"末地"}
    if("following entity data" in info.content):
        if die_user > 0:
            name = info.content.split(" ")[0]
        if name in die_name:
            try:
                die_name.remove(death_message.split(" ")[0])
            except:
                pass
            dimension = re.search("(?<=Dimension: )-?\d",info.content).group()
            position_str = re.search("(?<=Pos: )\[.*?\]",info.content).group()
            position = re.findall("\[(-?\d*).*?, (-?\d*).*?, (-?\d*).*?\]",position_str)[0]
            display(server, name, position, dimension)
            die_user-=1

def coordinate_text(x: float, y: float, z: float, dimension: str, opposite=False):
    dimension_coordinate_color = {
        '0': RColor.green,
        '-1': RColor.red,
        '1': RColor.light_purple
    }
    dimension_name = {
        '0': 'minecraft:overworld',
        '1': 'minecraft:the_end',
        '-1': 'minecraft:the_nether'
    }

    if opposite:
        dimension = '-1' if dimension == '0' else '0'
        x, z = (float(x) / 8, float(z) / 8) if dimension == '-1' else (x * 8, z * 8)

    pattern = RText('[{}, {}, {}]'.format(int(x), int(y), int(z)), dimension_coordinate_color[dimension])
    dim_text = RTextTranslation(dimension_display[dimension], color=dimension_color[dimension])

    return pattern.h(dim_text) if not config['click_to_teleport'] else pattern.h(
        dim_text + ': 点击以传送到' + pattern.copy()
        ).c(RAction.suggest_command, 
        '/execute in {} run tp {} {} {}'.format(dimension_name[dimension], int(x), int(y), int(z)))

def display(server: ServerInterface, name: str, position: Tuple[float, float, float], dimension: str):
    x, y, z = position
    dimension_convert = {
        'minecraft:overworld': '0',
        '"minecraft:overworld"': '0',
        'minecraft:the_nether': '-1',
        '"minecraft:the_nether"': '-1',
        'minecraft:the_end': '1',
        '"minecraft:the_end"': '1'
    }
    
    if dimension in dimension_convert:  # convert from 1.16 format to pre 1.16 format
        dimension = dimension_convert[dimension]

    # text base
    texts = RTextList(
        '§e{}§r'.format(name),
        ' 死于 ',
        RTextTranslation(dimension_display[dimension], color=dimension_color[dimension]),
        ' ',
        coordinate_text(x, y, z, dimension)
    )

    # click event to add waypoint
    if config['display_voxel_waypoint']:
        texts.append( ' ',
            RText('[+V]', RColor.aqua).h('§bVoxelmap§r: 点此以高亮坐标点, 或者Ctrl点击添加路径点').c(
                RAction.run_command, '/newWaypoint [x:{}, y:{}, z:{}, dim:{}]'.format(
                    int(x), int(y), int(z), dimension
                )))
    if config['display_xaero_waypoint']:
        texts.append( ' ',
            RText('[+X]', RColor.gold).h('§6Xaeros Minimap§r: 点击添加路径点').c(
                RAction.run_command, 'xaero_waypoint_add:{}:{}:{}:{}:{}:6:false:0:Internal_{}_waypoints'.format(
                    name + "'s Location", name[0], int(x), int(y), int(z), dimension.replace('minecraft:', '').strip()
                )))

    # coordinate conversion between overworld and nether
    if dimension in ['0', '-1']:
        texts.append(
            ' §7->§r ',
            coordinate_text(x, y, z, dimension, opposite=True)
            )

    server.tell(name, texts)