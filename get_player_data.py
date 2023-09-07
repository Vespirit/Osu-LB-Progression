import json, urllib.request as request
from typing import List

API_KEY = "154a7e8b4ffb2e3242bed716c8d20174c2ba99a1"

def get_completed(player_data_file: str) -> List[str]:

    result = []

    with open(player_data_file, "r") as f_player_data:
        cur_line = f_player_data.readline()

        while cur_line:
            id = cur_line.split(",")[0]
            result.append(id)

            cur_line = f_player_data.readline()
    
    return result

def generate(lb_data_file: str, player_data_file: str) -> List[str]:

    completed_ids = get_completed(player_data_file)
    dead_ids = []

    urlskel = urlskel = "https://osu.ppy.sh/api/get_user?k=" + API_KEY + "&u="

    with open(lb_data_file, "r") as f_data:
        with open(player_data_file, "a") as f_player_data:
            cur_line = f_data.readline()

            while cur_line:
                cur_line_cells = cur_line.split(",")
                
                print("Timestamp: " + cur_line_cells[0])

                i = 1 # ids are every other cell
                while i < len(cur_line_cells) - 1:

                    cur_id = cur_line_cells[i]
                    print("On user " + str(cur_id))

                    if cur_id in completed_ids:
                        i += 2
                        continue

                    with request.urlopen(urlskel + cur_id) as f_api:
                        user_data = json.loads(f_api.read().decode())

                    if len(user_data) < 1:
                        dead_ids.append((cur_id, cur_line_cells[0]))
                        i += 2
                        continue
                    else:
                        user_data = user_data[0]

                    username = user_data["username"].replace("_old", "")
                    f_player_data.write("\n" + cur_id + "," + username + "," + user_data["country"])

                    i += 2
                    completed_ids.append(cur_id)
                
                cur_line = f_data.readline()

    return dead_ids

if __name__ == '__main__':
    print(generate("data\lb_data.csv", "data\player_data.csv"))