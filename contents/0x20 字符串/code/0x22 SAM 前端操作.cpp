// 后缀自动机（前端操作）
namespace SAM {
    const int SIZE = N * 2;

    int strL, str[N];
    int nodeCount, Last;
    struct node {
        int trans[26];
        int link, maxl, pos;
    } t[SIZE];

    int net[SIZE][26];
    std::vector<int> son[SIZE];

    int newnode() {
        int p = ++ nodeCount;
        for (int c = 0; c < 26; c ++) t[p].trans[c] = net[p][c] = 0;
        t[p].link = t[p].maxl = t[p].pos = 0;
        son[p].clear();
        return p;
    }
    void init() {
        nodeCount = 0, Last = 1, newnode(); // 根节点为 1
        str[strL = 0] = -1;
    }

    void extend(int c) {
        int p = Last, np = Last = newnode();

        str[++ strL] = c, t[np].pos = strL;
        t[np].maxl = t[p].maxl + 1;
        for (; p && t[p].trans[c] == 0; p = t[p].link) {
            t[p].trans[c] = np;
        }

        if (!p) {
            t[np].link = 1;
        } else {
            int q = t[p].trans[c];
            if (t[q].maxl == t[p].maxl + 1) {
                t[np].link = q;
            } else {
                int nq = newnode();
                t[nq] = t[q], t[nq].maxl = t[p].maxl + 1;
                t[np].link = t[q].link = nq;
                for (; p && t[p].trans[c] == q; p = t[p].link) {
                    t[p].trans[c] = nq;
                }
            }
        }
    }

    void dfs_init(int u) {
        for (int v : son[u]) {
            net[u][str[t[v].pos - t[u].maxl]] = v;
            dfs_init(v);
        }
    }
    void build_tree() {
        for (int i = 2; i <= nodeCount; i ++) {
            son[t[i].link].push_back(i);
        }
        dfs_init(1);
    }

    void push_front(int &p, int &len, int c) {
        if (len == t[p].maxl) {
            p = net[p][c];
        } else if (str[t[p].pos - len] != c) {
            p = 0;
        }
        len = p ? len + 1 : 0;
    }
}