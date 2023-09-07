import java.util.Map;
import java.util.GregorianCalendar;
import java.util.Calendar;

int top = 25;
int numDays;

HashMap<String, PImage> flags = new HashMap<String, PImage>(); // map from 2 letter id to flag image
HashMap<String, Player> players = new HashMap<String, Player>(); // map from id to player object
String[][] lbs; // list of top 50 players on each day
float[] maxes; // max value on each day
float[] mins; // min value on each day

String[] parseCsvLine(String dataLine) {
    return dataLine.split(",", -1);
}

String[] listFileNames(String dir) {
    File file = new File(dir);
    if (file.isDirectory()) {
        String names[] = file.list();
        return names;
    } else {
        return null;
    }
}

void generateFlags() {

    String flagPath = sketchPath() + "/data/flags";
    String[] flagFiles = listFileNames(flagPath);

    for (String flagFile : flagFiles) {
        String flagString = flagFile.substring(0, 2);
        PImage flag = loadImage(flagPath + "/" + flagFile);
        flags.put(flagString, flag);
    }
}

color generateColor(String id) {

    int h = int(random(255));
    int s = 255;
    int b = 255;

    return color(h, s, b);
}

void generatePlayers(String[] playerData) {

    for (int i = 0; i < playerData.length; i++) {
        String[] playerVals = parseCsvLine(playerData[i]);

        String id = playerVals[0];
        String username = playerVals[1];
        String country = playerVals[2].toLowerCase();

        Player p = new Player(username, country, generateColor(id));

        players.put(id, p);
    }
}

void generateLBData(String[] lbData) {
    
    maxes = new float[numDays];
    mins = new float[numDays];
    lbs = new String[numDays][50];

    for (int i = 0; i < numDays; i++) {
        String[] values = parseCsvLine(lbData[i]);
        int numEntries = (values.length - 1) / 2;
        int day = Integer.parseInt(values[0]);

        for (int j = 0; j < numEntries; j++) {

            String id = values[j * 2 + 1];
            float pp = (float)Long.parseLong(values[j * 2 + 2]);

            if (j == 0) {
                maxes[i] = pp;
            }
            if (j == min(numEntries - 1, top - 1)) {
                mins[i] = pp;
            }

            lbs[i][j] = id;

            Player player = players.get(id);
            if (player != null) {
                player.pps[i] = pp;
                player.ranks[i] = (float)(j+1);
            }
        }
    }
}

void setup() {

    randomSeed(432765);

    size(1920, 1080);
    colorMode(HSB, 255);
    frameRate(60);

    String[] lbData = loadStrings("lb_continuous.csv");
    numDays = 1728; //= lbData.length;

    String[] playerData = loadStrings("player_data.csv");

    generatePlayers(playerData);
    generateFlags();
    generateLBData(lbData);
    
    GRAPHBOTTOMLEFT = new PVector(width * (1.0/10), height);
    GRAPHTOPRIGHT = new PVector(width * (4.0/5), height * (1.0/4));
}

PVector GRAPHBOTTOMLEFT;
PVector GRAPHTOPRIGHT;

float framesPerDay = 4;
float window = 3;
int frameCountReal = 0;

int numDaysShown = 500;

void drawBackground() {

    background(0);

    rectMode(CORNERS);
    strokeWeight(1);
    stroke(30);
    fill(0);
    rect(GRAPHBOTTOMLEFT.x, GRAPHBOTTOMLEFT.y, GRAPHTOPRIGHT.x, GRAPHTOPRIGHT.y);
}

float weightedAverageValueAt(float[] p, float x, float w) {
    int startIndex = max(0, ceil(x - w));
    int endIndex = min(floor(x + w), numDays - 1);

    float totalValue = 0;
    float totalWeight = 0;

    for (int i = startIndex; i <= endIndex; i++) {

        float value = p[i];
        float weight = 0.5 * cos((i - x) / (w * PI)) + 0.5;

        totalValue += value*weight;
        totalWeight += weight;
    }
    return totalValue / totalWeight;
}

float getHighestVal(float day) {
    return weightedAverageValueAt(maxes, day, 30);
}

float getLowestVal(float day) {
    return weightedAverageValueAt(mins, day, 30);
}

float valueToY(float value, float lowestVal, float highestVal) {
    return map(value, lowestVal, highestVal, GRAPHBOTTOMLEFT.y, GRAPHTOPRIGHT.y);
}

float dayToX(float day, float startDay, float endDay) {
    return map(day, startDay, endDay, GRAPHBOTTOMLEFT.x, GRAPHTOPRIGHT.x);
}

float rankToY(float rank) {
    return map(rank, (float)top, 1, GRAPHBOTTOMLEFT.y, GRAPHTOPRIGHT.y);
}

void drawPlayerData(float curDay) {

    textSize(16);
    textAlign(LEFT, CENTER);
    imageMode(CENTER);
    strokeWeight(3);

    float startDay = max(curDay - numDaysShown, 0);

    float lowestVal = getLowestVal(startDay);
    float highestVal = getHighestVal(curDay);

    for (float i = startDay+1; i < curDay-1; i++) {

        String[] lb = lbs[floor(i)];

        for (int j = 0; j < min(lb.length, top); j++) {

            String id = lb[j];
            Player player = players.get(id);
            if (player == null) {
                continue;
            }
            float index0 = i-1;
            float index1 = i;
            float index2 = i+1;
            float index3 = i+2;

            if (index3 >= curDay) {
                index3 = curDay;
            }
            float pp0 = weightedAverageValueAt(player.pps, index0, window);
            float pp1 = weightedAverageValueAt(player.pps, index1, window);
            float pp2 = weightedAverageValueAt(player.pps, index2, window);
            float pp3 = weightedAverageValueAt(player.pps, index3, window);

            if (pp1 < lowestVal || pp2 < lowestVal) {
                continue;
            }

            color c = player.c;

            float yVal0 = valueToY(pp0, lowestVal, highestVal);
            float yVal3 = valueToY(pp3, lowestVal, highestVal);

            float yVal1 = valueToY(pp1, lowestVal, highestVal);
            float yVal2 = valueToY(pp2, lowestVal, highestVal);

            float xVal1 = dayToX(index1, curDay - numDaysShown, curDay);
            float xVal2 = dayToX(index2, curDay - numDaysShown, curDay);

            float xVal0 = dayToX(index0, curDay - numDaysShown, curDay);
            float xVal3 = dayToX(index3, curDay - numDaysShown, curDay);

            stroke(c);
            fill(c);
            curve(xVal0, yVal0, xVal1, yVal1, xVal2, yVal2, xVal3, yVal3);

            if (i+2 >= curDay) {

                String username = player.username;
                String country = player.country;

                PImage flag = flags.get(country.toLowerCase());
                point(xVal2, yVal2);
                image(flag, xVal2 + 12, yVal2);
                text(username, xVal2 + 20, yVal2);
            }
        }
    }
}

void drawDate(float curDay) {

    textSize(100);
    fill(255);
    textAlign(LEFT, TOP);
    Calendar g = new GregorianCalendar(2007, 9, 11);
    g.add(Calendar.DAY_OF_MONTH, (int)curDay);
    text(g.get(Calendar.YEAR) + "/" + (g.get(Calendar.MONTH) + 1) + "/" + g.get(Calendar.DAY_OF_MONTH), 0, 0);
}

void draw() {
    float curDay = frameCountReal / framesPerDay;

    drawBackground();
    drawPlayerData(curDay);
    drawDate(curDay);
    
    if (curDay >= numDays - 2) {
        noLoop();
    }
    frameCountReal++;
}