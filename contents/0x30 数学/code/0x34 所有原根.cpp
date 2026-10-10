// 所有原根
std::vector<int> allPrimitiveRoot(int m) {
    if (m == 1) return {0};
    if (m == 2) return {1};

    int phi = m, x = m; // 若已知 m 为质数，则直接令 phi = m - 1
    for (int i = 2; i * i <= x; i ++) {
        if (x % i == 0) {
            phi = phi / i * (i - 1);
            while (x % i == 0) {
                x /= i;
            }
        }
    }
    if (x > 1) {
        phi = phi / x * (x - 1);
    }

    std::vector<int> pf;
    x = phi;
    for (int i = 2; i * i <= x; i ++) {
        if (x % i == 0) {
            pf.push_back(i);
            while (x % i == 0) {
                x /= i;
            }
        }
    }
    if (x > 1) {
        pf.push_back(x);
    }

    int g = 2;
    for (; g < m; g ++) {
        if (std::gcd(g, m) != 1) { // 若已知 m 为质数，则可以省略该判断
            continue;
        }
        int flag = 1;
        for (int p : pf) {
            if (qpow(g, phi / p, m) == 1) {
                flag = 0;
                break;
            }
        }
        if (flag) {
            break;
        }
    }
    if (g == m) {
        return {};
    }

    std::vector<int> res;
    x = 1;
    for (int i = 1; i <= phi; i ++) {
        x = 1ll * x * g % m;
        if (std::gcd(i, phi) == 1) {
            res.push_back(x);
        }
    }
    std::sort(res.begin(), res.end());
    return res;
}