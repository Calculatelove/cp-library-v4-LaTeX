std::vector<int> roots{0, 1};
void dft(std::vector<int> &a) {
    int n = a.size();
    for (int i = 1, j = 0; i < n; i ++) {
        for (int k = n >> 1; (j ^= k) < k; k >>= 1);
        if (i < j) std::swap(a[i], a[j]);
    }
    for (int k = roots.size(); k < n; k <<= 1) {
        int w = qpow(3, (mod - 1) / (k << 1), mod);
        roots.resize(k << 1);
        for (int i = k >> 1; i < k; i ++) {
            roots[i * 2] = roots[i];
            roots[i * 2 + 1] = 1ll * roots[i] * w % mod;
        }
    }
    for (int k = 1; k < n; k <<= 1) {
        for (int i = 0; i < n; i += (k << 1)) {
            for (int j = 0; j < k; j ++) {
                int u = a[i + j], v = 1ll * a[i + j + k] * roots[k + j] % mod;
                add(a[i + j] = u, v), dec(a[i + j + k] = u, v);
            }
        }
    }
}
void idft(std::vector<int> &a) {
    int n = a.size(), inv = (1 - mod) / n + mod;
    std::reverse(a.begin() + 1, a.end());
    dft(a);
    for (int i = 0; i < n; i ++) {
        mul(a[i], inv);
    }
}

// 多项式全家桶（2026-10-25）
struct poly : public std::vector<int> {
    using std::vector<int>::vector;
    explicit poly(const std::vector<int> &a) : std::vector<int>(a) {}

    // 多项式乘法
    friend poly operator * (poly a, poly b) {
        int tot = a.size() + b.size() - 1;
        if (tot < 128) {
            poly c(tot);
            for (int i = 0; i < a.size(); i ++) {
                for (int j = 0; j < b.size(); j ++) {
                    c[i + j] = (c[i + j] + 1ll * a[i] * b[j]) % mod;
                }
            }
            return c;
        }
        int L = 1;
        while (L < tot) L <<= 1;
        a.resize(L), b.resize(L);
        dft(a), dft(b);
        for (int i = 0; i < L; i ++) {
            mul(a[i], b[i]);
        }
        idft(a);
        a.resize(tot);
        return a;
    }

    // 多项式乘法（暴力）
    friend poly mul_bf(poly a, poly b) {
        poly c(a.size() + b.size() - 1);
        for (int i = 0; i < a.size(); i ++) {
            for (int j = 0; j < b.size(); j ++) {
                c[i + j] = (c[i + j] + 1ll * a[i] * b[j]) % mod;
            }
        }
        return c;
    }
    // 多项式除法（暴力）
    friend poly div_bf(poly a, poly b) {
        int t = 0;
        while (t < b.size() && b[t] == 0) t ++;
        if (t == b.size()) return poly(a.size() - b.size() + 1); // 除以全 0 多项式无意义
        a = poly(a.begin() + t, a.end());
        b = poly(b.begin() + t, b.end());
        int m = b.size() - 1, inv = qpow(b[0], mod - 2, mod);
        poly c(a.size() - b.size() + 1);
        for (int i = 0; i < c.size(); i ++) {
            c[i] = a[i];
            for (int j = std::max(0, i - m); j < i; j ++) {
                dec(c[i], 1ll * c[j] * b[i - j] % mod);
            }
            mul(c[i], inv);
        }
        return c;
    }
    
    friend poly operator + (poly a, poly b) {
        poly c(std::max(a.size(), b.size()));
        for (int i = 0; i < a.size(); i ++) add(c[i], a[i]);
        for (int i = 0; i < b.size(); i ++) add(c[i], b[i]);
        return c;
    }
    friend poly operator - (poly a, poly b) {
        poly c(std::max(a.size(), b.size()));
        for (int i = 0; i < a.size(); i ++) add(c[i], a[i]);
        for (int i = 0; i < b.size(); i ++) dec(c[i], b[i]);
        return c;
    }
    friend poly operator - (poly a) {
        for (int &x : a) neg(x);
        return a;
    }

    friend poly operator * (poly a, int b) {
        for (int &x : a) mul(x, b);
        return a;
    }
    friend poly operator / (poly a, int b) {
        int inv = qpow(b, mod - 2, mod);
        for (int &x : a) mul(x, inv);
        return a;
    }

    poly &operator += (poly b) {
        return (*this) = (*this) + b;
    }
    poly &operator -= (poly b) {
        return (*this) = (*this) - b;
    }
    poly &operator *= (poly b) {
        return (*this) = (*this) * b;
    }
    poly &operator *= (int b) {
        return (*this) = (*this) * b;
    }
    poly &operator /= (int b) {
        return (*this) = (*this) / b;
    }

    poly mulxk(int k) const {
        auto res = *this;
        res.insert(res.begin(), k, 0);
        return res;
    }
    poly divxk(int k) const {
        if (k >= size()) return poly();
        return poly((*this).begin() + k, (*this).end());
    }
    poly modxk(int k) const {
        if (k >= size()) return *this;
        return poly((*this).begin(), (*this).begin() + k);
    }
    poly cirxk(int k) const {
        auto res = *this;
        for (int i = k; i < size(); i ++) {
            add(res[i % k], res[i]); // 若多项式次数 <2k，可改成 res[i - k]
        }
        return res.modxk(k);
    }

    poly flip() const {
        auto res = *this;
        std::reverse(res.begin(), res.end());
        return res;
    }

    poly mulT(poly b) const {
        if (b.size() == 0) return poly();
        std::reverse(b.begin(), b.end());
        return ((*this) * b).divxk(b.size() - 1);
        // 等价于“翻转卷积”，a.mulT(b) 相当于是求 a[i] * b[j] -> c[i - j]
    }

    // 多项式导数
    poly deriv() const {
        if (empty()) return poly();
        poly res(size() - 1);
        for (int i = 1; i < size(); i ++) {
            res[i - 1] = 1ll * (*this)[i] * i % mod;
        }
        return res;
    }

    // 多项式积分
    poly integ() const {
        poly res(size() + 1);
        for (int i = 0; i < size(); i ++) {
            res[i + 1] = 1ll * (*this)[i] * qpow(i + 1, mod - 2, mod) % mod;
        }
        return res;
    }

    // 多项式求逆
    poly inv(int m) const { // 需要保证常数项不为 0
        poly x{qpow((*this)[0], mod - 2, mod)};
        int k = 1;
        while (k < m) {
            k <<= 1;
            x = (x * (poly{2} - modxk(k) * x)).modxk(k);
        }
        return x.modxk(m);
    }
    // 少项式求逆
    poly inv_bf(int m) const { // 需要保证常数项不为 0
        auto &&a = *this;
        int n = a.size() - 1, inv = qpow(a[0], mod - 2, mod);

        poly b(m);
        for (int i = 0; i < m; i ++) {
            b[i] = i == 0;
            for (int j = std::max(0, i - n); j < i; j ++) {
                dec(b[i], 1ll * b[j] * a[i - j] % mod);
            }
            mul(b[i], inv);
        }
        return b;
    }

    // 多项式开方
    poly sqrt(int m) const {
        poly x{1}; // 默认常数项为 1
        int k = 1;
        while (k < m) {
            k <<= 1;
            x = (x + (modxk(k) * x.inv(k)).modxk(k)) / 2;
        }
        return x.modxk(m);
    }

    // 多项式带余除法
    friend std::pair<poly, poly> divmod(poly a, poly b) {
        int n = a.size(), m = b.size(), L = n - m + 1;
        if (n < m) return {poly{0}, a};
        poly q = (a.flip().modxk(L) * b.flip().inv(L)).modxk(L).flip();
        poly r = a - b * q;
        while (r.size() > 1 && !r.back()) {
            r.pop_back();
        }
        return {q, r};
    }

    // 多项式 ln
    poly ln(int m) const { // 需要保证常数项为 1
        return (deriv() * inv(m)).integ().modxk(m);
    }

    // 多项式 exp
    poly exp(int m) const { // 需要保证常数项为 0
        poly x{1};
        int k = 1;
        while (k < m) {
            k <<= 1;
            x = (x * (poly{1} - x.ln(k) + modxk(k))).modxk(k);
        }
        return x.modxk(m);
    }

    // 多项式快速幂
    poly pow(int k, int m) const {
        int i = 0;
        while (i < size() && (*this)[i] == 0) i ++;
        if (i == size() || 1ll * i * k >= m) return poly(m);
        int v = (*this)[i];
        poly f = divxk(i) * qpow(v, mod - 2, mod);
        return (f.ln(m - i * k) * k).exp(m - i * k).mulxk(i * k) * qpow(v, k, mod);
        /*
            当实际 k < mod 时，可以放心使用
            当实际 k >= mod 时，请注意：
            - 当 i > 0 时，直接返回 poly(m)
            - 当 i = 0 时
              - 在多项式 ln 与多项式 exp 部分，k 需要对 mod 取模
              - 在 qpow(v, k, mod) 部分，k 需要对 mod - 1 取模
        */
    }
    // 少项式快速幂
    poly pow_bf(int k, int m) const { // 需要保证常数项不为 0
        std::vector<int> v(m); // 需要保证 m > 1
        v[1] = 1;
        for (int i = 2; i < m; i ++) {
            v[i] = 1ll * v[mod % i] * (mod - mod / i) % mod;
        }

        auto &&a = *this;
        int n = a.size() - 1, inv = qpow(a[0], mod - 2, mod);

        poly b(m);
        b[0] = qpow(a[0], k, mod);
        for (int i = 0; i + 1 < m; i ++) {
            b[i + 1] = 0;
            for (int j = std::max(0, i - n + 1); j <= i; j ++) {
                add(b[i + 1], 1ll * (i - j + 1) * a[i - j + 1] % mod * b[j] % mod);
            }
            mul(b[i + 1], k);
            for (int j = std::max(0, i - n); j < i; j ++) {
                dec(b[i + 1], 1ll * (j + 1) * b[j + 1] % mod * a[i - j] % mod);
            }
            mul(b[i + 1], v[i + 1]), mul(b[i + 1], inv);
        }
        return b;
    }

    // 多项式多点求值
    std::vector<int> eval(std::vector<int> x) const {
        if (empty()) return std::vector<int>(x.size(), 0);

        int n = std::max(x.size(), size());
        std::vector<poly> t(n * 4);
        std::vector<int> ans(x.size());
        x.resize(n);

        std::function<void(int, int, int)> build = [&] (int p, int l, int r) {
            if (l == r) {
                t[p] = poly{1, norm(-x[l])};
                return;
            }
            int mid = (l + r) >> 1;
            build(p * 2, l, mid), build(p * 2 + 1, mid + 1, r);
            t[p] = t[p * 2] * t[p * 2 + 1];
        };
        build(1, 0, n - 1);

        std::function<void(int, int, int, const poly &)> solve = [&] (int p, int l, int r, const poly &num) {
            if (l >= ans.size()) return;
            if (l == r) {
                ans[l] = num[0];
                return;
            }
            int mid = (l + r) >> 1;
            solve(p * 2, l, mid, num.mulT(t[p * 2 + 1]).modxk(mid - l + 1));
            solve(p * 2 + 1, mid + 1, r, num.mulT(t[p * 2]).modxk(r - mid));
        };
        solve(1, 0, n - 1, mulT(t[1].inv(n)));

        return ans;
    }

    // 多项式平移
    poly shift(int c) const {
        int n = size() - 1;

        std::vector<int> fact(n + 1), facv(n + 1);
        fact[0] = 1;
        for (int i = 1; i <= n; i ++) {
            fact[i] = 1ll * fact[i - 1] * i % mod;
        }
        facv[n] = qpow(fact[n], mod - 2, mod);
        for (int i = n - 1; i >= 0; i --) {
            facv[i] = 1ll * facv[i + 1] * (i + 1) % mod;
        }

        c = norm(c);
        poly a(n + 1), b(n + 1);
        for (int i = 0; i <= n; i ++) {
            a[i] = 1ll * (*this)[i] * fact[i] % mod;
        }
        for (int i = 0, w = 1; i <= n; i ++, mul(w, c)) {
            b[i] = 1ll * w * facv[i] % mod;
        }

        poly res = a.mulT(b);
        for (int i = 0; i <= n; i ++) {
            mul(res[i], facv[i]);
        }
        return res;
    }
};

// 多项式快速插值
poly lagrange(std::vector<std::pair<int, int>> seq) {
    int n = seq.size(); // seq 下标从 0 开始，至多 n-1 次多项式需要 n 个点值
    std::vector<poly> t(n * 4);
    std::vector<int> x(n);
    for (int i = 0; i < n; i ++) {
        x[i] = seq[i].first;
    }

    std::function<void(int, int, int)> build = [&] (int p, int l, int r) {
        if (l == r) {
            t[p] = poly{norm(-x[l]), 1};
            return;
        }
        int mid = (l + r) >> 1;
        build(p * 2, l, mid), build(p * 2 + 1, mid + 1, r);
        t[p] = t[p * 2] * t[p * 2 + 1];
    };
    build(1, 0, n - 1);

    auto res = (t[1].deriv()).eval(x);
    std::function<poly(int, int, int)> solve = [&] (int p, int l, int r) {
        if (l == r) {
            return poly{norm(1ll * seq[l].second * qpow(res[l], mod - 2, mod))};
        }
        int mid = (l + r) >> 1;
        return solve(p * 2, l, mid) * t[p * 2 + 1] + solve(p * 2 + 1, mid + 1, r) * t[p * 2];
    };
    return solve(1, 0, n - 1);
}

// 连续点值平移
std::vector<int> shift_conti(std::vector<int> y, int c) {
    int n = y.size() - 1; // y 下标从 0 开始，连续点值为 f(0), ..., f(n)

    std::vector<int> fact(n + 1), facv(n + 1);
    fact[0] = 1;
    for (int i = 1; i <= n; i ++) {
        fact[i] = 1ll * fact[i - 1] * i % mod;
    }
    facv[n] = qpow(fact[n], mod - 2, mod);
    for (int i = n - 1; i >= 0; i --) {
        facv[i] = 1ll * facv[i + 1] * (i + 1) % mod;
    }

    poly a(2 * n + 1), b(n + 1);
    for (int i = 0; i <= 2 * n; i ++) {
        a[i] = qpow(norm(c - n + i), mod - 2, mod);
    }
    for (int i = 0; i <= n; i ++) {
        b[i] = 1ll * facv[i] * facv[n - i] % mod * norm(y[i]) % mod;
        if ((n - i) & 1) neg(b[i]);
    }

    poly res = a * b;
    int num = 1, z = 0;
    for (int i = c - n; i <= c; i ++) {
        int v = norm(i);
        if (v) mul(num, v); else z ++;
    }
    std::vector<int> ans(n + 1);
    for (int i = 0; i <= n; i ++) {
        if (z) {
            ans[i] = y[norm(c + i)];
        } else {
            ans[i] = 1ll * num * res[i + n] % mod;
        }
        int v1 = norm(c - n + i), v2 = norm(c + i + 1);
        if (v1) mul(num, a[i]); else z --;
        if (v2) mul(num, v2); else z ++;
    }
    return ans;
}