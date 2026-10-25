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

struct poly : public std::vector<comp> {
    using std::vector<comp>::vector;
    explicit poly(const std::vector<comp> &a) : std::vector<comp>(a) {}

    friend poly operator * (poly a, poly b) {
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
        int L = 1;
        while (L < tot) L <<= 1;
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