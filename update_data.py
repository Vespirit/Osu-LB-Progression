'''
Updates all the necessary data files from where it left off with new Wayback data (assuming site format does not change.)
'''

from get_snapshots import get_snapshots
from get_player_data import generate
from get_flags import get_flags
from get_continuous_data import make_continuous

if __name__ == '__main__':
    csv_file = "data/lb_data.csv"
    player_data = "data/player_data.csv"
    continuous_file = "data/lb_continuous.csv"
    
    get_snapshots(csv_file)
    generate(csv_file, player_data)
    get_flags(player_data)
    make_continuous(csv_file, continuous_file)
    