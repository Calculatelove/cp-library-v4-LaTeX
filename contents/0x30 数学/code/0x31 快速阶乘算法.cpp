// 快速阶乘算法
int fastFactorial(int n) {
    if (n == 0) return 1;
    if (n >= mod) return 0;

    int v = sqrt(n), iv = qpow(v, mod - 2, mod);
    std::function<std::vector<int>(int)> solve = [&] (int d) {
        if (d == 1) {
            return std::vector<int>{1, v + 1};
        }
        if (d & 1) {
            auto y = solve(d - 1);
            for (int i = 0; i < y.size(); i ++) {
                mul(y[i], i * v + d);
            }
            int num = 1;
            for (int i = 1; i <= d; i ++) {
                mul(num, d * v + i);
            }
            y.push_back(num);
            return y;
        } else {
            auto y = solve(d / 2);
            auto y1 = shift_conti(y, d / 2);
            y.insert(y.end(), y1.begin() + 1, y1.end());
            auto y2 = shift_conti(y, 1ll * (d / 2) * iv % mod);
            for (int i = 0; i < y.size(); i ++) {
                mul(y[i], y2[i]);
            }
            return y;
        }
    };

    auto res = solve(v);
    int ans = 1;
    for (int i = 0; i < v; i ++) {
        mul(ans, res[i]);
    }
    for (int i = v * v + 1; i <= n; i ++) {
        mul(ans, i);
    }
    return ans;
}