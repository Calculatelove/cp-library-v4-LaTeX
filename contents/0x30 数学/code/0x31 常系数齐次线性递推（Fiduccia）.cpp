// 常系数齐次线性递推（Fiduccia）
int linearRecurrence(std::vector<int> c, std::vector<int> y, int n) {
    int k = y.size(); // k 阶齐次线性递推数列
    if (n < k) return norm(y[n]);

    poly g(k + 1);
    g[k] = 1;
    for (int i = 1; i <= k; i ++) {
        g[k - i] = norm(-c[i]);
    }

    poly res{1}, a{0, 1};
    for (int b = n; b; b >>= 1) {
        if (b & 1) res = divmod(res * a, g).second;
        a = divmod(a * a, g).second;
    }

    int ans = 0;
    for (int i = 0; i < res.size(); i ++) {
        ans = (ans + 1ll * y[i] * res[i]) % mod;
    }
    return norm(ans);
}