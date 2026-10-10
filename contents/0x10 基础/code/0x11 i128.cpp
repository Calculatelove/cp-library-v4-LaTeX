using i128 = __int128;

// 重载 i128 标准输入流
std::istream &operator >> (std::istream &is, i128 &x) {
    std::string s;
    is >> s;
    int n = s.length(), f = s[0] == '-';
    x = 0;
    for (int i = f; i < n; i ++) {
        x = x * 10 + s[i] - '0';
    }
    if (f) x = -x;
    return is;
}
// 重载 i128 标准输出流
std::ostream &operator << (std::ostream &os, i128 x) {
    if (x < 0) x = -x, os << '-';
    std::string s;
    do {
        s += char(x % 10 + '0'), x /= 10;
    } while (x);
    std::reverse(s.begin(), s.end());
    return os << s;
}