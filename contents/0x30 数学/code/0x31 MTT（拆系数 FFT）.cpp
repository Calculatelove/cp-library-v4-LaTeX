const double pi = acos(-1);
using comp = std::complex<double>;

std::vector<comp> roots{0, 1};
void dft(std::vector<comp> &a) {
    int n = a.size();
    for (int i = 1, j = 0; i < n; i ++) {
        for (int k = n >> 1; (j ^= k) < k; k >>= 1);
        if (i < j) std::swap(a[i], a[j]);
    }
    for (int k = roots.size(); k < n; k <<= 1) {
        comp w(cos(pi / k), sin(pi / k));
        roots.resize(k << 1);
        for (int i = k >> 1; i < k; i ++) {
            roots[i * 2] = roots[i];
            roots[i * 2 + 1] = roots[i] * w;
        }
    }
    for (int k = 1; k < n; k <<= 1) {
        for (int i = 0; i < n; i += (k << 1)) {
            for (int j = 0; j < k; j ++) {
                comp u = a[i + j], v = a[i + j + k] * roots[k + j];
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
        std::vector<comp> P(L), Q(L), R(L), S(L);
        for (int i = 0; i < a.size(); i ++) {
            P[i] = comp(a[i] & 32767, a[i] >> 15);
        }
        for (int i = 0; i < b.size(); i ++) {
            Q[i] = comp(b[i] & 32767, b[i] >> 15);
        }
        dft(P), dft(Q);
        for (int i = 0; i < L; i ++) {
            int j = (L - i) & (L - 1);
            comp a0 = (P[i] + std::conj(P[j])) * 0.5;
            comp a1 = (P[i] - std::conj(P[j])) * comp(0, -0.5);
            R[i] = a0 * Q[i], S[i] = a1 * Q[i];
        }
        idft(R), idft(S);
        poly c(tot);
        for (int i = 0; i < tot; i ++) {
            i64 c0 = llround(R[i].real()) % mod;
            i64 c1 = (llround(R[i].imag()) + llround(S[i].real())) % mod;
            i64 c2 = llround(S[i].imag()) % mod;
            c[i] = ((c2 << 30) + (c1 << 15) + c0) % mod;
        }
        return c;
    }
};