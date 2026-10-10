// 单个逆元的求解
i64 inverse(i64 a, i64 m) {
    auto [d, x, y] = exgcd(a, m);
    // assert(d == 1);
    return (x % m + m) % m;
}