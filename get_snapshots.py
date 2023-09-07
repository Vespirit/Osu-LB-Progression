'''
Script to update leaderboard data from the Wayback machine.
Older timestamps were done with different global parameters. Newer ones should work barring major website layout changes.
'''

import urllib.request as request, re, os, json
from bs4 import BeautifulSoup
from datetime import date, timedelta

EARLIEST_DATA = "20071011"

websites = ["http://osu.ppy.sh/index.php?p=player",
            "http://osu.ppy.sh/?p=playerranking",
            "http://osu.ppy.sh/p/playerranking",
            "http://osu.ppy.sh/p/pp/",
            "https://osu.ppy.sh/rankings/osu/performance"
            ]

regexes = [r"https:\/\/web\.archive\.org\/web\/\d+\/http:\/\/osu\.ppy\.sh\/forum\/memberlist\.php\?mode=viewprofile&u=(\d+)",
            r"\?p=profile&u=(\d+)",
            r"\/web\/\d+\/http:\/\/osu\.ppy\.sh\/u\/(\d+)",
            r"\/web\/\d+\/https:\/\/osu\.ppy\.sh\/u\/(\d+)",
            r"\/web\/\d+\/https:\/\/www\.osu\.ppy\.sh\/u\/(\d+)",
            r"\/web\/\d+\/http:\/\/www\.osu\.ppy\.sh\/u\/(\d+)",
            r"\/web\/\d+mp_\/https:\/\/osu\.ppy\.sh\/users\/(\d+)",
            r"\/web\/\d+mp_\/http:\/\/osu\.ppy\.sh\/users\/(\d+)",
            r"https:\/\/web\.archive\.org\/web\/\d+\/https:\/\/osu\.ppy\.sh\/users\/(\d+)",
            r"https:\/\/web.archive.org\/web\/\d+\/https:\/\/osu\.ppy\.sh\/users\/(\d+)\/osu"]

regexes_c = []
for regex in regexes:
    regexes_c.append(re.compile(regex))

cur_website = 4

link_col = 1
a_tag = 1

pp_col = 4

def get_most_recent_entry(csv_file: str) -> str:
    with open(csv_file, "rb") as file:
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:
            file.seek(0)
        last_line = file.readline().decode()

    return last_line.split(",")[0]

def date_to_timestamp(d: date) -> str:
    if d.month < 10:
        ms = "0" + str(d.month)
    else:
        ms = str(d.month)

    if d.day < 10:
        ds = "0" + str(d.day)
    else:
        ds = str(d.day)

    return str(d.year) + ms + ds

def timestamp_to_date(timestamp: str) -> date:
    year = int(timestamp[0:4])
    month = int(timestamp[4:6])
    day = int(timestamp[6:8])

    return date(year, month, day)

def date_to_day(d: date) -> int:
    td = d - timestamp_to_date(EARLIEST_DATA)
    return td.days

def timestamp_to_day(timestamp: str) -> int:
    return date_to_day(timestamp_to_date(timestamp))

def only_digits(s: str) -> int:
    result = ""
    for c in s:
        if c.isdigit():
            result += c
    return int(result)

def get_snapshots(csv_file: str) -> None:
    start_day = get_most_recent_entry(csv_file)

    start_d = date(2007,10,11) + timedelta(days=int(start_day))
    start_timestamp = date_to_timestamp(start_d)

    with request.urlopen("http://web.archive.org/cdx/search/cdx?url=" + websites[cur_website] + "&output=json&from=" + start_timestamp) as api_open:
        site_snaplist = json.loads(api_open.read().decode())[1:]

    cur_timestamp = start_timestamp
    for snap in site_snaplist:
        if snap[1][:8] == cur_timestamp:
            continue
        else:
            cur_timestamp = snap[1][:8]
        original_website = snap[2]

        print(cur_timestamp)

        with request.urlopen("https://web.archive.org/web/" + cur_timestamp + "/" + original_website) as snap_open:
            snap_html = snap_open.read().decode()

        rank = 1

        soup = BeautifulSoup(snap_html, 'lxml')
        table = soup.find_all('table')[1]

        with open(csv_file, 'a') as f_csv:
            day = str(timestamp_to_day(cur_timestamp))
            if (day == start_day):
                continue

            f_csv.write("\n" + day)

            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if (len(cols) > 0):

                    link_str = cols[link_col].find_all('a')[a_tag].get('href')
                    id = ""
                    for regex in regexes_c:
                        match = re.match(regex, link_str)
                        if match:
                            id = match.group(1)
                    if id == "":
                        raise LookupError
                    f_csv.write("," + id)

                    pp = only_digits(cols[pp_col].get_text())
                    f_csv.write("," + str(pp))

                    rank += 1

if __name__ == '__main__':
    get_snapshots("data/lb_data.csv")