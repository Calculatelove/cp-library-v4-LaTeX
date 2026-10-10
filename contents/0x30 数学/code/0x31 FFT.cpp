const double pi = acos(-1);
using comp = std::complex<double>;

std::vector<int> rev;
void dft(std::vector<comp> &a) {
    int n = a.size();
    for (int i = 0; i < n; i ++) {
        if (i < rev[i]) {
            std::swap(a[i], a[rev[i]]);
        }
    }
    for (int k = 1; k < n; k <<= 1) {
        comp omega(cos(pi / k), sin(pi / k)); // 2k 阶单位根
        for (int i = 0; i < n; i += (k << 1)) {
            comp x(1, 0);
            for (int j = 0; j < k; j ++, x *= omega) {
                comp u = a[i + j], v = x * a[i + j + k];
                a[i + j] = u + v, a[i + j + k] = u - v;
            }
        }
    }
}
void idft(std::vector<comp> &a) {
    int n = a.size();
    std::reverse(a.begin() + 1, a.end());
    dft(a);
    for (int i = 0; i < n; i ++) {
        a[i] /= n;
    }
}

struct poly : public std::vector<comp> {
    poly() : std::vector<comp>() {}
    explicit constexpr poly(int n) : std::vector<comp>(n) {}
    explicit constexpr poly(const std::vector<comp> &a) : std::vector<comp>(a) {}
    constexpr poly(const std::initializer_list<comp> &a) : std::vector<comp>(a) {}

    template <class InputIt, class = std::_RequireInputIter<InputIt>>
    explicit constexpr poly(InputIt st, InputIt ed) : std::vector<comp>(st, ed) {}

    constexpr friend poly operator * (poly a, poly b) {
        int tot = a.size() + b.size() - 1;
        if (tot < 128) {
            poly c(tot);
            for (int i = 0; i < a.size(); i ++) {
                for (int j = 0; j < b.size(); j ++) {
                    c[i + j] += a[i] * b[j];
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

        a.resize(L), b.resize(L);
        dft(a), dft(b);
        for (int i = 0; i < L; i ++) {
            a[i] *= b[i];
        }
        idft(a);
        a.resize(tot);
        return a;
    }
};