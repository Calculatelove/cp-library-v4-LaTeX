// 类欧几里得算法（要求 a, b >= 0 以及 c > 0）
i64 euclid(i64 a, i64 b, i64 c, i64 n) {
    if (a == 0) {
        return (n + 1) * (b / c);
    }
    if (a >= c || b >= c) {
        return euclid(a % c, b % c, c, n) + (n * (n + 1) / 2) * (a / c) + (n + 1) * (b / c);
    }
    i64 m = (a * n + b) / c;
    if (m == 0) {
        return 0;
    }
    return n * m - euclid(c, c - b - 1, a, m - 1);
}
// 类欧几里得算法
i64 euclid_norm(i64 a, i64 b, i64 c, i64 n) {
    if (c < 0) {
        a = -a, b = -b, c = -c;
    }
    i64 sum = 0;
    if (a < 0) {
        i64 t = (a - c + 1) / c;
        a -= t * c, sum += (n * (n + 1) / 2) * t;
    }
    if (b < 0) {
        i64 t = (b - c + 1) / c;
        b -= t * c, sum += (n + 1) * t;
    }
    return euclid(a, b, c, n) + sum;
}