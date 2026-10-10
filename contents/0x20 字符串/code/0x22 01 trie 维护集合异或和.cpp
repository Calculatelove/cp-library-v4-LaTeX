// 01 trie 维护集合异或和
namespace trie {
    const int pond = 10001000; // 内存池大小，需要根据实际问题调整

    int nodeCount;
    struct node {
        int trans[2];
        int cnt;
        int xr;
        #define lc trans[0]
        #define rc trans[1]
    } t[pond];

    int newnode() {
        int p = ++ nodeCount;
        t[p].lc = t[p].rc = t[p].cnt = t[p].xr = 0;
        return p;
    }
    
    void upd(int p) {
        t[p].cnt = t[t[p].lc].cnt + t[t[p].rc].cnt;
        t[p].xr = (t[t[p].lc].xr << 1) ^ (t[t[p].rc].xr << 1) ^ (t[t[p].rc].cnt & 1);
    }

    void insert(int &p, int d, int x, int y) {
        if (!p) p = newnode();
        if (d == 31) {
            t[p].cnt += y;
            return;
        }
        int v = x >> d & 1;
        insert(t[p].trans[v], d + 1, x, y);
        upd(p);
    }

    void addone(int p) {
        std::swap(t[p].lc, t[p].rc);
        if (t[p].lc) addone(t[p].lc);
        upd(p);
    }
}