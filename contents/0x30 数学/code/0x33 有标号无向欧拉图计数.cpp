// 有标号无向欧拉图计数
poly GraphCount(int n) {
    std::vector<int> fact(n + 1), facv(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; i ++) {
        fact[i] = 1ll * fact[i - 1] * i % mod;
    }
    facv[n] = qpow(fact[n], mod - 2, mod);
    for (int i = n - 1; i >= 0; i --) {
        facv[i] = 1ll * facv[i + 1] * (i + 1) % mod;
    }

    poly g(n + 1);
    g[0] = 1;
    for (int i = 1; i <= n; i ++) {
        g[i] = 1ll * qpow(2, 1ll * (i - 1) * (i - 2) / 2, mod) * facv[i] % mod;
    }
    poly f = g.ln(n + 1);
    for (int i = 0; i <= n; i ++) {
        mul(f[i], fact[i]);
    }
    return f;
}