class Player {

    String username;
    String country;
    color c;
    float[] pps;
    float[] ranks;

    public Player(String username, String country, color c) {
        this.username = username;
        this.country = country;
        this.c = c;
        this.pps = new float[numDays];
        this.ranks = new float[numDays];
    }
}