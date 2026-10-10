// 大步小步算法
int BSGS(int a, int b, int p) { // a^x = b (mod p)
    if (b == 1 || p == 1) return 0;
    if (a == 0) return b == 0 ? 1 : -1;

    int S = sqrt(p) + 1;
    std::unordered_map<int, int> buc;

    int w = 1;
    for (int j = 0; j < S; j ++, w = 1ll * w * a % p) {
        int v = 1ll * w * b % p;
        buc[v] = j;
    }
    int x = w;
    for (int i = 1; i <= S; i ++, x = 1ll * x * w % p) {
        if (buc.contains(x)) {
            return i * S - buc[x];
        }
    }
    return -1;
}