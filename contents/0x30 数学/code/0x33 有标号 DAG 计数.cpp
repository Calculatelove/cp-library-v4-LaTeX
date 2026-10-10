// 有标号 DAG 计数
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
    g[0] = 0;
    for (int i = 1, i2 = qpow(2, mod - 2, mod); i <= n; i ++) {
        g[i] = 1ll * facv[i] * qpow(i2, 1ll * i * (i - 1) / 2, mod) % mod;
        if ((i + 1) & 1) neg(g[i]);
    }
    poly f = (poly{1} - g).inv(n + 1);
    for (int i = 0; i <= n; i ++) {
        mul(f[i], fact[i]), mul(f[i], qpow(2, 1ll * i * (i - 1) / 2, mod));
    }
    return f;
}