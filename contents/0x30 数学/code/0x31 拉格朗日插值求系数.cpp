// 拉格朗日插值求系数
std::vector<int> lagrange(std::vector<std::pair<int, int>> seq) {
    int n = seq.size(); // seq 下标从 0 开始，至多 n-1 次的多项式需要 n 个点值

    std::vector<int> a(n); // 系数部分 a[]
    for (int i = 0; i < n; i ++) {
        int q = 1;
        for (int j = 0; j < n; j ++) {
            if (i == j) continue;
            mul(q, seq[i].first - seq[j].first);
        }
        a[i] = 1ll * seq[i].second * qpow(q, mod - 2, mod) % mod;
    }

    std::vector<int> g(n + 1); // 总多项式 g
    g[0] = 1;
    for (int i = 0; i < n; i ++) {
        for (int j = i + 1; j >= 1; j --) {
            g[j] = (1ll * g[j] * -seq[i].first + g[j - 1]) % mod;
        }
        g[0] = 1ll * g[0] * -seq[i].first % mod;
    }
    
    std::vector<int> f(n); // 答案多项式 f
    for (int i = 0; i < n; i ++) {
        std::vector<int> h(n); // 分多项式 h_i
        h[n - 1] = g[n];
        for (int j = n - 2; j >= 0; j --) {
            h[j] = (g[j + 1] + 1ll * h[j + 1] * seq[i].first) % mod;
        }

        for (int j = 0; j < n; j ++) {
            f[j] = (f[j] + 1ll * a[i] * h[j]) % mod;
        }
    }

    for (int &x : f) x = norm(x);
    return f;
}

int func(const std::vector<int> &f, int k) {
    int n = f.size();
    int y = 0;
    for (int i = n - 1; i >= 0; i --) {
        y = (1ll * y * k + f[i]) % mod;
    }
    return norm(y);
}