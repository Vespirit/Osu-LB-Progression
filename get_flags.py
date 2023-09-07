import urllib.request as request

def get_flags(player_data_file: str) -> None:

    completed = []

    with open(player_data_file, "r") as f_player_data:
        cur_line = f_player_data.readline()

        while(cur_line):
            print(cur_line)

            cur_country = cur_line.split(",")[2].lower()[:-1]
            if cur_country not in completed and cur_country != "":
                request.urlretrieve("https://s.ppy.sh/images/flags/" + cur_country + ".gif", "data/flags/" + cur_country + ".gif")

            cur_line = f_player_data.readline()

if __name__ == '__main__':
    get_flags("data\player_data.csv")