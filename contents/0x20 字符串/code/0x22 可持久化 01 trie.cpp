// 可持久化 01 trie
namespace trie {
    const int pond = 10001000; // 内存池大小，需要根据实际问题调整

    int nodeCount;
    struct node {
        int trans[2];
        int cnt;
    } t[pond];

    void insert(int &p, int q, int d, int x) {
        p = ++ nodeCount, t[p] = t[q], t[p].cnt ++;
        if (d < 0) return;
        int v = x >> d & 1;
        insert(t[p].trans[v], t[q].trans[v], d - 1, x);
    }
}