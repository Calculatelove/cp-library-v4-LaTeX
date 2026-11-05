// Lyndon 分解
auto duval(const auto &s) {
    int n = s.size() - 1; // s 下标从 1 开始
    std::vector<int> res;
    // std::vector<int> ans(n + 1);
    for (int i = 1; i <= n;) {
        // if (!ans[i]) ans[i] = i;
        int j = i + 1, k = i;
        for (; j <= n && s[k] <= s[j]; j ++) {
            // if (!ans[j]) ans[j] = i;
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