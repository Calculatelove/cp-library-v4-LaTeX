// 整数除法 精确上取整
i64 ceilDiv(i64 n, i64 m) {
    // assert(m);
    if (m < 0) n = -n, m = -m;
    return n >= 0 ? (n + m - 1) / m : n / m;
}

// 整数除法 精确下取整
i64 floorDiv(i64 n, i64 m) {
    // assert(m);
    if (m < 0) n = -n, m = -m;
    return n >= 0 ? n / m : (n - m + 1) / m;
}