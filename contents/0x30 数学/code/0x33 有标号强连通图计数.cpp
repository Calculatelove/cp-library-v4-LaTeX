// 有标号强连通图计数
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

    poly h(n + 1);
    h[0] = 1;
    for (int i = 1; i <= n; i ++) {
        h[i] = 1ll * qpow(2, 1ll * i * (i - 1) / 2, mod) * facv[i] % mod;
    }
    poly g2 = poly{1} - h.inv(n + 1);
    for (int i = 1; i <= n; i ++) {
        mul(g2[i], qpow(2, 1ll * i * (i - 1) / 2, mod));
    }
    poly g1 = g2;
    for (int i = 1; i <= n; i ++) {
        mul(g1[i], i);
    }
    poly f = (g1 * (poly{1} - g2).inv(n + 1)).modxk(n + 1);
    for (int i = 1; i <= n; i ++) {
        mul(f[i], fact[i - 1]);
    }
    return f;
}