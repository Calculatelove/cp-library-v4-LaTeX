// 预处理单位根
constexpr auto findRootPower(int mod, int g) {
    std::array<int, 32> w{};
    for (int k = 1, idx = 0; (mod - 1) % (k << 1) == 0; k <<= 1) {
        w[idx ++] = qpow(g, (mod - 1) / (k << 1), mod); // 2k 阶单位根
    }
    return w;
}

std::vector<int> rev;
template <const int mod>
struct ntt {
    std::array<int, 32> RootPower;
    ntt() { RootPower = findRootPower(mod, 3); }

    inline void add(int &x, const int &y) { x += y; if (x >= mod) x -= mod; }
    inline void dec(int &x, const int &y) { x -= y; if (x < 0) x += mod; }
    inline void mul(int &x, const int &y) { x = 1ll * x * y % mod; }

    void dft(std::vector<int> &a) {
        int n = a.size();
        for (int i = 0; i < n; i ++) {
            if (i < rev[i]) {
                std::swap(a[i], a[rev[i]]);
            }
        }
        for (int k = 1, idx = 0; k < n; k <<= 1) {
            int omega = RootPower[idx ++];
            for (int i = 0; i < n; i += (k << 1)) {
                int x = 1;
                for (int j = 0; j < k; j ++, mul(x, omega)) {
                    int u = a[i + j], v = 1ll * x * a[i + j + k] % mod;
                    add(a[i + j] = u, v), dec(a[i + j + k] = u, v);
                }
            }
        }
    }
    void idft(std::vector<int> &a) {
        int n = a.size(), inv = qpow(n, mod - 2, mod);
        std::reverse(a.begin() + 1, a.end());
        dft(a);
        for (int i = 0; i < n; i ++) {
            mul(a[i], inv);
        }
    }

    auto mul(std::vector<int> a, std::vector<int> b, int L) {
        for (int &x : a) x %= mod;
        for (int &x : b) x %= mod;
        a.resize(L), b.resize(L);
        dft(a), dft(b);
        for (int i = 0; i < L; i ++) {
            mul(a[i], b[i]);
        }
        idft(a);
        return a;
    }
};

const int
    mod1 = 998244353,
    mod2 = 1004535809,
    mod3 = 469762049;
ntt<mod1> ntt1;
ntt<mod2> ntt2;
ntt<mod3> ntt3;

// 完整地得出 CRT 的解
int CRT(int x1, int x2, int x3) {
    static const i128 M = i128(mod1) * mod2 * mod3;
    static const i64 M1 = M / mod1, M2 = M / mod2, M3 = M / mod3;
    static const int
        V1 = qpow(M1 % mod1, mod1 - 2, mod1),
        V2 = qpow(M2 % mod2, mod2 - 2, mod2),
        V3 = qpow(M3 % mod3, mod3 - 2, mod3);
    i128 x = 0;
    x += i128(x1) * M1 * V1;
    x += i128(x2) * M2 * V2;
    x += i128(x3) * M3 * V3;
    x %= M; // 此时的 x 即为 CRT 的解
    return x % mod;
}

struct poly : public std::vector<int> {
    poly() : std::vector<int>() {}
    explicit constexpr poly(int n) : std::vector<int>(n) {}
    explicit constexpr poly(const std::vector<int> &a) : std::vector<int>(a) {}
    constexpr poly(const std::initializer_list<int> &a) : std::vector<int>(a) {}

    template <class InputIt, class = std::_RequireInputIter<InputIt>>
    explicit constexpr poly(InputIt st, InputIt ed) : std::vector<int>(st, ed) {}

    constexpr friend poly operator * (poly a, poly b) {
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

        int L = 1, P = 0;
        while (L < tot) L <<= 1, P ++;
        rev.resize(L);
        for (int i = 0; i < L; i ++) {
            rev[i] = (rev[i >> 1] >> 1) | ((i & 1) << (P - 1));
        }

        auto c1 = ntt1.mul(a, b, L), c2 = ntt2.mul(a, b, L), c3 = ntt3.mul(a, b, L);
        poly c(tot);
        for (int i = 0; i < tot; i ++) {
            c[i] = CRT(c1[i], c2[i], c3[i]);
        }
        return c;
    }
};