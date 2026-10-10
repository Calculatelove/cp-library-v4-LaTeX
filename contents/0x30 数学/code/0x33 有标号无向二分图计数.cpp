// 有标号无向二分图计数
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

    poly a(n + 1);
    for (int i = 0, i2 = qpow(2, mod - 2, mod); i <= n; i ++) {
        a[i] = 1ll * facv[i] * qpow(i2, 1ll * i * (i - 1) / 2, mod) % mod;
    }
    poly g = (a * a).modxk(n + 1);
    for (int i = 0; i <= n; i ++) {
        mul(g[i], qpow(2, 1ll * i * (i - 1) / 2, mod));
    }
    poly f = g.sqrt(n + 1);
    for (int i = 0; i <= n; i ++) {
        mul(f[i], fact[i]);
    }
    return f;
}