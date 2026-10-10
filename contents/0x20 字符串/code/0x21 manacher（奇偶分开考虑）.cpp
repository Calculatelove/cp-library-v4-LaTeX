// p[i]：区间 [i - p[i] + 1, i + p[i] - !is_even] 回文，奇偶分开考虑
auto manacher(const auto &s, int is_even) {
    int n = s.size() - 1; // s 下标从 1 开始
    std::vector<int> p(n + 1);
    for (int i = 1, mid = 0, r = 1; i <= n - is_even; i ++) {
        int &x = p[i] = i < r ? std::min(r - i, p[mid - i]) : 0;
        while (i - x > 0 && i + x + is_even <= n && s[i - x] == s[i + x + is_even]) {
            x ++;
        }
        if (i + x > r) {
            mid = i * 2, r = i + x;
        }
    }
    return p;
}