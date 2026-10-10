// 回文自动机 half
namespace PAM {
    int strL, str[N];
    int nodeCount, Last;
    struct node {
        int trans[26];
        int link, half, len;
    } t[N];

    int newnode() {
        int p = ++ nodeCount;
        for (int c = 0; c < 26; c ++) t[p].trans[c] = 0;
        t[p].link = t[p].half = t[p].len = 0;
        return p;
    }
    void init() {
        nodeCount = -1, Last = 1, newnode(), newnode(); // 偶根为 0，奇根为 1
        str[strL = 0] = -1;
        t[0].len = 0, t[0].link = 1;
        t[1].len = -1;
    }

    int find(int p) {
        while (str[strL - t[p].len - 1] != str[strL]) {
            p = t[p].link;
        }
        return p;
    }
    int find_half(int p, int L) {
        while (t[p].len + 2 > L || str[strL - t[p].len - 1] != str[strL]) {
            p = t[p].link;
        }
        return p;
    }
    void extend(int c) {
        str[++ strL] = c;
        int p = find(Last);
        if (!t[p].trans[c]) {
            int np = newnode();
            t[np].len = t[p].len + 2;
            t[np].link = t[find(t[p].link)].trans[c];
            t[np].half = t[np].len > 2 ? t[find_half(t[p].half, t[np].len / 2)].trans[c] : t[np].link;
            t[p].trans[c] = np;
        }
        Last = t[p].trans[c];
    }
}