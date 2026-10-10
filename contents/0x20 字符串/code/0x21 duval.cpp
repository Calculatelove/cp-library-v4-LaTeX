// Lyndon 分解
auto duval(const auto &s) {
    int n = s.size(); // s 下标从 0 开始
    std::vector<int> res;
    for (int i = 0; i < n;) {
        int j = i + 1, k = i;
        for (; j < n && s[k] <= s[j]; j ++) {
            if (s[k] < s[j]) {
                k = i;
            } else {
                k ++;
            }
        }
        for (; i <= k; i += j - k) {
            res.push_back(i);
        }
    }
    return res;
}