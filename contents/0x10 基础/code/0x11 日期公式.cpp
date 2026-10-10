// 返回从 1/1/1 到 y/m/d 的天数，由于 1/1/1 是周一，所以 mod 7 可以算出是周几
int getday(int y, int m, int d) {
    if (m < 3) y --, m += 12;
    return (365 * y + y / 4 - y / 100 + y / 400 + (153 * (m - 3) + 2) / 5 + d - 307);
}

// 返回从 1/1/1 开始经过 n 天的日期（getday 的逆函数）
std::array<int, 3> date(int n) {
    int y, m, d;
    n += 429 + ((4 * n + 1227) / 146097 + 1) * 3 / 4;
    y = (4 * n - 489) / 1461;
    n -= y * 1461 / 4;
    m = (5 * n - 1) / 153;
    d = n - m * 153 / 5;
    if (-- m > 12) m -= 12, y ++;
    return {y, m, d};
}