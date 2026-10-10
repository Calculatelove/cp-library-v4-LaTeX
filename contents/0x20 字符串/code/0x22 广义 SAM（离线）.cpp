// 广义 SAM（离线）
namespace GSAM {
    const int SIZE = N * 2;
    
    int trieCount, trie[N][26], site[N];
    int nodeCount;
    struct node {
        int trans[26];
        int link, maxl;
    } t[SIZE];

    int newtrie() {
        int p = ++ trieCount;
        for (int c = 0; c < 26; c ++) trie[p][c] = 0;
        site[p] = 0;
        return p;
    }
    int newnode() {
        int p = ++ nodeCount;
        for (int c = 0; c < 26; c ++) t[p].trans[c] = 0;
        t[p].link = t[p].maxl = 0;
        return p;
    }
    void init() {
        trieCount = 0, newtrie(); // trie 根节点为 1
        nodeCount = 0, newnode(); // GSAM 根节点为 1
    }

    void insert(const std::string &s) {
        int p = 1;
        for (char ch : s) {
            int v = ch - 'a';
            if (!trie[p][v]) trie[p][v] = newtrie();
            p = trie[p][v];
        }
    }

    int extend(int Last, int c) {
        int p = Last, np = newnode();

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
        return np;
    }

    void build() {
        std::queue<int> q;
        q.push(1), site[1] = 1;

        while (q.size()) {
            int u = q.front(); q.pop();
            for (int i = 0; i < 26; i ++) {
                if (trie[u][i]) {
                    site[trie[u][i]] = extend(site[u], i);
                    q.push(trie[u][i]);
                }
            }
        }
    }
}