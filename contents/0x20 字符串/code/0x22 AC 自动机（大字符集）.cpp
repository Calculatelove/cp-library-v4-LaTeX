// 可持久化数组
namespace SGT {
    const int pond = 10001000; // 内存池大小，需要根据实际问题调整

    int nodeCount;
    struct node {
        int lc, rc;
        int val;
    } t[pond];

    void init() {
        nodeCount = 0, t[0].val = 1;
    }

    void insert(int &p, int q, int l, int r, int x, int y) {
        p = ++ nodeCount, t[p] = t[q];
        if (l == r) { t[p].val = y; return; }
        int mid = (l + r) >> 1;
        if (x <= mid) {
            insert(t[p].lc, t[q].lc, l, mid, x, y);
        } else {
            insert(t[p].rc, t[q].rc, mid + 1, r, x, y);
        }
    }
    
    int ask(int p, int l, int r, int x) {
        if (l == r) return t[p].val;
        int mid = (l + r) >> 1;
        if (x <= mid) {
            return ask(t[p].lc, l, mid, x);
        } else {
            return ask(t[p].rc, mid + 1, r, x);
        }
    }
}

// AC 自动机（大字符集）
namespace AC {
    const int SIZE = 1000100; // 多模式串长度总和，需要根据实际问题调整

    int nodeCount;
    struct node {
        std::map<int, int> trans;
        int fail;
    } t[SIZE];

    int root[SIZE];

    int newnode() {
        int p = ++ nodeCount;
        t[p].trans.clear();
        t[p].fail = 0;
        return p;
    }
    void init() {
        nodeCount = 0, newnode(); // 根节点为 1
    }

    void insert(const std::vector<int> &a) {
        int p = 1;
        for (int v : a) {
            if (!t[p].trans.contains(v)) t[p].trans[v] = newnode();
            p = t[p].trans[v];
        }
    }

    void build_fail() {
        SGT::init(), root[0] = 0;
        t[1].fail = 0;

        std::queue<int> q;
        q.push(1);

        while (q.size()) {
            int u = q.front(); q.pop();
            root[u] = root[t[u].fail];
            for (auto [c, v] : t[u].trans) {
                SGT::insert(root[u], root[u], 1, V, c, v);
                t[v].fail = SGT::ask(root[t[u].fail], 1, V, c);
                q.push(v);
            }
        }
    }
}