// 扩展中国剩余定理
struct equ {
    i64 a, m; // {a, m} 表示方程 x = a (mod m)
    equ() {}
    equ(i64 a, i64 m) : a(a), m(m) {}

    friend equ operator + (equ l, equ r) {
        auto [a1, m1] = l;
        auto [a2, m2] = r;
        if (a1 == -1 || a2 == -1) {
            return {-1, -1};
        }
        auto [d, x, y] = exgcd(m1, m2);
        if ((a2 - a1) % d) {
            return {-1, -1};
        }
        x = x * ((a2 - a1) / d) % (m2 / d); // 必要时，使用“快速乘”防止爆 long long
        if (x < 0) x += (m2 / d);
        i64 m = m1 * (m2 / d);
        i64 a = (x * m1 + a1) % m; // 必要时，使用“快速乘”防止爆 long long
        return {a, m};
    }
};