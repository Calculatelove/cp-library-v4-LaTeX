void dwtOr(std::vector<int> &a, int opt) {
    int n = a.size();
    for (int k = 1; k < n; k <<= 1) {
        for (int i = 0; i < n; i += (k << 1)) {
            for (int j = 0; j < k; j ++) {
                opt > 0 ? add(a[i + j + k], a[i + j]) : dec(a[i + j + k], a[i + j]);
            }
        }
    }
}
void dwtAnd(std::vector<int> &a, int opt) {
    int n = a.size();
    for (int k = 1; k < n; k <<= 1) {
        for (int i = 0; i < n; i += (k << 1)) {
            for (int j = 0; j < k; j ++) {
                opt > 0 ? add(a[i + j], a[i + j + k]) : dec(a[i + j], a[i + j + k]);
            }
        }
    }
}
void dwtXor(std::vector<int> &a, int opt) {
    int n = a.size();
    for (int k = 1; k < n; k <<= 1) {
        for (int i = 0; i < n; i += (k << 1)) {
            for (int j = 0; j < k; j ++) {
                int u = a[i + j], v = a[i + j + k];
                add(a[i + j] = u, v), dec(a[i + j + k] = u, v);
            }
        }
    }
    if (opt < 0) {
        int inv = qpow(n, mod - 2, mod);
        for (int i = 0; i < n; i ++) {
            mul(a[i], inv);
        }
    }
}

// 位运算卷积
using dwtFunc = void(*)(std::vector<int>&, int);
std::vector<int> conv(std::vector<int> a, std::vector<int> b, dwtFunc dwt) {
    dwt(a, +1), dwt(b, +1);
    for (int i = 0; i < a.size(); i ++) {
        mul(a[i], b[i]);
    }
    dwt(a, -1);
    return a;
}