// 转化为形如 #a#b#c# 的字符串
auto manacher_init(const std::string &s) {
    std::string t = " #";
    for (char ch : s) {
        t += ch, t += "#";
    }
    return t;
}

// p[i]：区间 [i - p[i] + 1, i + p[i] - 1] 回文
auto manacher(const auto &s) {
    int n = s.size() - 1; // s 下标从 1 开始
    std::vector<int> p(n + 1);
    for (int i = 1, mid = 0, r = 1; i <= n; i ++) {
        int &x = p[i] = i < r ? std::min(r - i, p[mid - i]) : 0;
        while (i - x > 0 && i + x <= n && s[i - x] == s[i + x]) {
            x ++;
        }
        if (i + x > r) {
            mid = i * 2, r = i + x;
        }
    }
    return p;
}

// 以位置 i 为回文中心的最长回文子串，在原串中的长度为 p[i] - 1（转换成 #a#b#c# 形式后）
// 判断原串区间 [l, r] 是否回文：p[l + r] - 1 >= r - l + 1（转换成 #a#b#c# 形式后）