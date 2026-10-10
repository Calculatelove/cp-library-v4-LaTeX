// AC 自动机
namespace AC {
    const int SIZE = 1000100; // 多模式串长度总和，需要根据实际问题调整

    int nodeCount;
    struct node {
        int trans[26];
        int fail;
    } t[SIZE];

    int newnode() {
        int p = ++ nodeCount;
        for (int c = 0; c < 26; c ++) t[p].trans[c] = 0;
        t[p].fail = 0;
        return p;
    }
    void init() {
        nodeCount = 0, newnode(); // 根节点为 1
    }

    void insert(const std::string &s) {
        int p = 1;
        for (char ch : s) {
            int v = ch - 'a';
            if (!t[p].trans[v]) t[p].trans[v] = newnode();
            p = t[p].trans[v];
        }
    }

    void build_fail() {
        for (int i = 0; i < 26; i ++) t[0].trans[i] = 1;
        t[1].fail = 0;

        std::queue<int> q;
        q.push(1);

        while (q.size()) {
            int u = q.front(); q.pop();
            for (int i = 0; i < 26; i ++) {
                if (t[u].trans[i]) {
                    t[t[u].trans[i]].fail = t[t[u].fail].trans[i];
                    q.push(t[u].trans[i]);
                } else {
                    t[u].trans[i] = t[t[u].fail].trans[i];
                }
            }
        }
    }
}