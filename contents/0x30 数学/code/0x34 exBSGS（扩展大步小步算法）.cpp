// 扩展大步小步算法
int exBSGS(int a, int b, int p) { // a^x = b (mod p)
    if (b == 1 || p == 1) return 0;
    if (a == 0) return b == 0 ? 1 : -1;

    int d, r = 1, step = 0;
    while (d = std::gcd(a, p), d > 1) {
        if (b % d) {
            return -1;
        }
        b /= d, p /= d, r = 1ll * r * (a / d) % p;
        step ++;
        if (r == b) {
            return step;
        }
    }
    if (p == 1) {
        return step;
    }

    int S = sqrt(p) + 1;
    std::unordered_map<int, int> buc;

    int w = 1;
    for (int j = 0; j < S; j ++, w = 1ll * w * a % p) {
        int v = 1ll * w * b % p;
        buc[v] = j;
    }
    int x = 1ll * r * w % p;
    for (int i = 1; i <= S; i ++, x = 1ll * x * w % p) {
        if (buc.contains(x)) {
            return step + i * S - buc[x];
        }
    }
    return -1;
}