// Power Projection
poly PowerProjection(poly a, poly b, int n) {
    // assert(n >= 1);
    // assert(!b.size() || !b[0]);

    a.resize(n), b.resize(n);
    for (int &x : b) {
        neg(x);
    }

    int n0 = n --;
    for (int m = 1; n; m <<= 1, n >>= 1) {
        int L = n * 2 + 2, len = 1;
        while (len < 2 * m * L) len <<= 1;

        poly d(len);
        for (int i = 0; i < m; i ++) {
            for (int j = 0; j <= n; j ++) {
                d[i * L + j] = b[i * (n + 1) + j];
            }
        }
        dft(d);

        int h = len >> 1;
        poly work(h);
        for (int i = 0; i < h; i ++) {
            work[i] = 1ll * d[i] * d[i + h] % mod;
            std::swap(d[i], d[i + h]);
        }
        idft(work);

        int t = n / 2 + 1;
        poly p(2 * m * t), q(2 * m * t);
        for (int i = 0; i < 2 * m - 1; i ++) {
            for (int j = 0; j < t; j ++) {
                q[i * t + j] = work[i * (n + 1) + j];
            }
        }
        for (int i = 0; i < m; i ++) {
            for (int j = 0; j < t; j ++) {
                add(q[(m + i) * t + j], b[i * (n + 1) + 2 * j]);
                add(q[(m + i) * t + j], b[i * (n + 1) + 2 * j]);
            }
        }

        poly c(len);
        for (int i = 0; i < m; i ++) {
            for (int j = 0; j <= n; j ++) {
                c[i * L + j] = a[i * (n + 1) + j];
            }
        }
        dft(c);
        for (int i = 0; i < len; i ++) {
            mul(c[i], d[i]);
        }
        idft(c);

        for (int i = 0; i < 2 * m - 1; i ++) {
            for (int j = 0; j < t; j ++) {
                p[i * t + j] = c[i * L + 2 * j + (n & 1)];
            }
        }
        for (int i = 0; i < m; i ++) {
            for (int j = 0; j < t; j ++) {
                add(p[(m + i) * t + j], a[i * (n + 1) + 2 * j + (n & 1)]);
            }
        }
        a.swap(p), b.swap(q);
    }

    std::reverse(a.begin(), a.end());
    a.resize(n0);
    return a;
}