template <const int mod>
struct ntt {
    inline void add(int &x, const int &y) { x += y; if (x >= mod) x -= mod; }
    inline void dec(int &x, const int &y) { x -= y; if (x < 0) x += mod; }
    inline void mul(int &x, const int &y) { x = 1ll * x * y % mod; }

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

    auto mul(std::vector<int> a, std::vector<int> b) {
        for (int &x : a) x %= mod;
        for (int &x : b) x %= mod;
        dft(a), dft(b);
        for (int i = 0; i < a.size(); i ++) {
            mul(a[i], b[i]);
        }
        idft(a);
        return a;
    }
};

const int mod1 = 998244353, mod2 = 1004535809, mod3 = 469762049;
ntt<mod1> ntt1;
ntt<mod2> ntt2;
ntt<mod3> ntt3;

int CRT(int x1, int x2, int x3) {
    static const i64 M12 = 1ll * mod1 * mod2;
    static const int
        inv1 = qpow(mod1, mod2 - 2, mod2),
        inv12 = qpow(M12 % mod3, mod3 - 2, mod3);
    int t1 = 1ll * (x2 - x1 + mod2) * inv1 % mod2;
    i64 x12 = x1 + 1ll * mod1 * t1;
    int t2 = (x3 - x12 % mod3 + mod3) * inv12 % mod3;
    return (x12 % mod + (M12 % mod) * t2) % mod;
}

// int CRT(int x1, int x2, int x3) {
//     static const i128 M = i128(mod1) * mod2 * mod3;
//     static const i64 M1 = M / mod1, M2 = M / mod2, M3 = M / mod3;
//     static const int
//         V1 = qpow(M1 % mod1, mod1 - 2, mod1),
//         V2 = qpow(M2 % mod2, mod2 - 2, mod2),
//         V3 = qpow(M3 % mod3, mod3 - 2, mod3);
//     i128 x = 0;
//     x += i128(x1) * M1 * V1;
//     x += i128(x2) * M2 * V2;
//     x += i128(x3) * M3 * V3;
//     x %= M; // 此时的 x 即为 CRT 的解
//     return x % mod;
// }

struct poly : public std::vector<int> {
    using std::vector<int>::vector;
    explicit poly(const std::vector<int> &a) : std::vector<int>(a) {}

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
        auto c1 = ntt1.mul(a, b), c2 = ntt2.mul(a, b), c3 = ntt3.mul(a, b);
        poly c(tot);
        for (int i = 0; i < tot; i ++) {
            c[i] = CRT(c1[i], c2[i], c3[i]);
        }
        return c;
    }
};