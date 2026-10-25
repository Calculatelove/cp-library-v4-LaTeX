// 分式远处系数
int BostanMori(poly p, poly q, int n) {
    for (; n; n >>= 1) {
        poly nq = q;
        for (int i = 1; i < nq.size(); i += 2) {
            neg(nq[i]);
        }
        p *= nq, q *= nq;

        int i = n & 1;
        while (i < p.size()) {
            p[i / 2] = p[i], i += 2;
        }
        p.resize(i / 2);

        int j = 0;
        while (j < q.size()) {
            q[j / 2] = q[j], j += 2;
        }
        q.resize(j / 2);
    }
    return 1ll * p[0] * qpow(q[0], mod - 2, mod) % mod;
}

// 常系数齐次线性递推（Bostan-Mori）
int linearRecurrence(std::vector<int> c, std::vector<int> y, int n) {
    int k = y.size(); // k 阶齐次线性递推数列
    if (n < k) return norm(y[n]);

    for (int &x : c) x = norm(x);
    for (int &x : y) x = norm(x);

    poly q = poly{1} - poly(c);
    poly p = (poly(y) * q).modxk(k);
    return BostanMori(p, q, n);
}