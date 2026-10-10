// 连续点值的拉格朗日插值
int lagrange(std::vector<int> y, int k) {
    int n = y.size() - 1; // y 下标从 1 开始，连续点值为 f(1), ..., f(n)
    if (k >= 1 && k <= n) {
        return y[k];
    }

    std::vector<int> pre(n + 2), suf(n + 2);
    pre[0] = 1;
    for (int i = 1; i <= n; i ++) {
        pre[i] = 1ll * pre[i - 1] * (k - i) % mod;
    }
    suf[n + 1] = 1;
    for (int i = n; i >= 1; i --) {
        suf[i] = 1ll * suf[i + 1] * (k - i) % mod;
    }

    std::vector<int> fact(n + 1), facv(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; i ++) {
        fact[i] = 1ll * fact[i - 1] * i % mod;
    }
    facv[n] = qpow(fact[n], mod - 2, mod);
    for (int i = n - 1; i >= 0; i --) {
        facv[i] = 1ll * facv[i + 1] * (i + 1) % mod;
    }

    int ans = 0;
    for (int i = 1; i <= n; i ++) {
        int cur = y[i];
        cur = 1ll * cur * pre[i - 1] % mod * suf[i + 1] % mod;
        cur = 1ll * cur * facv[i - 1] % mod * facv[n - i] % mod;
        if ((n - i) & 1) cur = -cur;
        add(ans, norm(cur));
    }

    return ans;
}