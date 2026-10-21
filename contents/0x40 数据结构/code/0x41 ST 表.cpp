// ST 表
template <class T, auto op>
struct SparseTable {
    int t;
    std::vector<std::vector<T>> f;

    SparseTable() {}
    SparseTable(int n, std::vector<T> a) {
        init(n, a);
    }

    void init(int n, std::vector<T> a) {
        t = std::__lg(n);
        f.assign(t + 1, std::vector<T>(n + 1));
        for (int i = 1; i <= n; i ++) {
            f[0][i] = a[i];
        }
        for (int j = 1; j <= t; j ++) {
            for (int i = 1; i <= n - (1 << j) + 1; i ++) {
                f[j][i] = op(f[j - 1][i], f[j - 1][i + (1 << (j - 1))]);
            }
        }
    }

    T ask(int l, int r) {
        int k = std::__lg(r - l + 1);
        return op(f[k][l], f[k][r - (1 << k) + 1]);
    }
};