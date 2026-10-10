// 更相减损术
int gcd(int a, int b) {
    if (a == b) {
        return a;
    }
    if (a == 0 || b == 0) {
        return a ^ b;
    }
    int az = __builtin_ctz(a), bz = __builtin_ctz(b), z = az < bz ? az : bz, v = 0;
    a >>= az, b >>= bz;
    while (b) {
        v = b - a;
        a = a < b ? a : b;
        b = v < 0 ? -v : v;
        if (b) b >>= __builtin_ctz(b);
    }
    return a << z;
}