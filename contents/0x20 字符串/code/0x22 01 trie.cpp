// 01 trie
namespace trie {
    const int pond = 10001000; // 内存池大小，需要根据实际问题调整

    int nodeCount;
    struct node {
        int trans[2];
        int cnt;
        #define lc trans[0]
        #define rc trans[1]
    } t[pond];

    int newnode() {
        int p = ++ nodeCount;
        t[p].lc = t[p].rc = t[p].cnt = 0;
        return p;
    }

    void insert(int &p, int d, int x) {
        if (!p) p = newnode();
        t[p].cnt ++;
        if (d < 0) return;
        int v = x >> d & 1;
        insert(t[p].trans[v], d - 1, x);
    }

    int merge(int p, int q) {
        if (!p || !q) return p ^ q;
        t[p].cnt += t[q].cnt;
        t[p].lc = merge(t[p].lc, t[q].lc);
        t[p].rc = merge(t[p].rc, t[q].rc);
        return p;
    }
    
    // 可持久化 01 trie 合并
    // int merge(int p, int q) {
    //     if (!p || !q) return p ^ q;
    //     int u = newnode();
    //     t[u].cnt = t[p].cnt + t[q].cnt;
    //     t[u].lc = merge(t[p].lc, t[q].lc);
    //     t[u].rc = merge(t[p].rc, t[q].rc);
    //     return u;
    // }
}