// 最小表示法
// std::rotate(s.begin(), s.begin() + minrep(s), s.end());
int minrep(const auto &s) {
    int n = s.size(), k = 0, i = 0, j = 1; // s 下标从 0 开始
    while (k < n && i < n && j < n) {
        int d = s[(i + k) % n] - s[(j + k) % n];
        if (d == 0) {
            k ++;
        } else {
            (d > 0 ? i : j) += k + 1;
            if (i == j) i ++;
            k = 0;
        }
    }
    return std::min(i, j);
}