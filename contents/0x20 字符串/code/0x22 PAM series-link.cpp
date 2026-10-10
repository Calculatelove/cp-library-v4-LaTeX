// 回文自动机 series-link
namespace PAM {
    int strL, str[N];
    int nodeCount, Last;
    struct node {
        int trans[26];
        int link, len;
        int diff, slink;
    } t[N];
    int g[N];

    int newnode() {
        int p = ++ nodeCount;
        for (int c = 0; c < 26; c ++) t[p].trans[c] = 0;
        t[p].link = t[p].len = 0;
        t[p].diff = t[p].slink = 0;
        g[p] = 0x3f3f3f3f;
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
    void extend(int c) {
        str[++ strL] = c;
        int p = find(Last);
        if (!t[p].trans[c]) {
            int np = newnode();
            t[np].len = t[p].len + 2;
            t[np].link = t[find(t[p].link)].trans[c];
            t[np].diff = t[np].len - t[t[np].link].len;
            t[np].slink = t[np].diff == t[t[np].link].diff ? t[t[np].link].slink : t[np].link;
            t[p].trans[c] = np;
        }
        Last = t[p].trans[c];
    }

    int ask(int x, int i) {
        int ans = 0x3f3f3f3f;
        for (int u = x; u > 1; u = t[u].slink) {
            g[u] = f[i - t[u].diff - t[t[u].slink].len];
            if (t[u].diff == t[t[u].link].diff) {
                chmin(g[u], g[t[u].link]);
            }
            chmin(ans, g[u]);
        }
        return ans;
    }
}