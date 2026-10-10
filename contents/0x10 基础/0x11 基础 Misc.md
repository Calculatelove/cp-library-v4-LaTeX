# 0x11 基础 Misc

## 常用常数表

<img src="https://cdn.luogu.com.cn/upload/image_hosting/tmzjcvie.png" style="zoom:67%;" />

## 常用公式

### 日期公式

==0x11 日期公式.cpp==：

```c++
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
```

### xorshift

==0x11 xorshift.cpp==：

```c++
u64 mask = std::mt19937_64(std::random_device{}())();
u64 xorshift(u64 x) {
    x ^= mask;
    x ^= x << 13, x ^= x >> 7, x ^= x << 17;
    x ^= mask;
    return x;
}
```

### xorsum

$$
\operatorname{xor}_{i = 1}^n i = \begin{cases}
n, & n \bmod 4 = 0 \\
1, & n \bmod 4 = 1 \\
n + 1, & n \bmod 4 = 2 \\
0, & n \bmod 4 = 3
\end{cases}
$$

==0x11 xorsum.cpp==：

```c++
int xorsum(int n) {
    int r = n % 4;
    if (r == 0) {
        return n;
    } else if (r == 1) {
        return 1;
    } else if (r == 2) {
        return n + 1;
    } else {
        return 0;
    }
}
```

### Sum of Powers

$$
\sum_{i = 1}^n i^2 = \frac{n(n + 1)(2n + 1)}{6}, \quad \sum_{i = 1}^n i^3 = \left( \frac{n(n + 1)}{2} \right)^2 \\
\sum_{i = 1}^n i^4 = \frac{n(n + 1)(2n + 1)(3n^2 + 3n - 1)}{30} \\
\sum_{i = 1}^n i^5 = \frac{n^2(n + 1)^2(2n^2 + 2n - 1)}{12}
$$

## 常用配置

### makefile

```makefile
CXXFLAGS = -std=c++23 -O2 -Wall -fsanitize=undefined

# -D_GLIBCXX_DEBUG : STL debug mode
# -fsanitize=address : 内存错误检查
# -fsanitize=undefined : UB 检查
```

### pragma

```c++
#pragma GCC optimize("O3,unroll-loops")
#pragma GCC target("avx2")
```

### ulimit

```c++
ulimit -s 1048576
```

### Linux 对拍脚本

需要 `chmod +x cmp.sh`，然后才能 `./cmp.sh`。

```bash
while true; do
    ./gen >0.in
    ./obj <0.in >1.out
    ./std <0.in >2.out
    let cnt=cnt+1; echo "Test $cnt:"
    if diff 1.out 2.out; then
        echo ac
    else
        echo wa
        break;
    fi
done
```

### Windows 对拍程序

```c++
#include <bits/stdc++.h>
int main() {
    int T = 100;
    for (int i = 1; i <= T; i ++) {
        system("gen.exe >0.in");
        system("obj.exe <0.in >1.out");
        system("std.exe <0.in >2.out");
        std::cout << "Test " << i << ":\n";
        if (system("fc 1.out 2.out")) {
            std::cout << "wa\n";
            break;
        } else {
            std::cout << "ac\n";
        }
    }
}
```

## 随机数据生成

### 生成区间 [l,r] 中的随机整数

==0x11 生成区间 [l,r] 中的随机整数.cpp==：

```c++
std::mt19937_64 mtrand{std::random_device{}()};

// 生成区间 [l, r] 中的随机整数
int rand(int l, int r) {
    std::uniform_int_distribution<int> range(l, r);
    return range(mtrand);
}
```

### 生成区间 [l,r) 中的随机浮点数

==0x11 生成区间 [l,r) 中的随机浮点数.cpp==：

```c++
std::mt19937_64 mtrand{std::random_device{}()};

// 生成区间 [l, r) 中的随机浮点数
double rand(double l, double r) {
    std::uniform_real_distribution<double> range(l, r);
    return range(mtrand);
}
```

### 生成互不相同的随机整数

==0x11 生成互不相同的随机整数.cpp==：

```c++
// 生成 n 个在区间 [l, r] 中互不相同的随机整数
auto GenSequence(int n, int l, int r) {
    assert(n <= r - l + 1);
    std::map<int, int> buc;
    std::vector<int> res(n);
    for (int i = 0; i < n; i ++) {
        do {
            res[i] = rand(l, r);
        } while (buc.contains(res[i]));
        buc[res[i]] = 1;
    }
    return res;
}
```

### 生成随机树

- 均匀随机树的期望直径为 $\mathcal{O}(\sqrt{n})$ 级别。

==0x11 生成随机树.cpp==：

```c++
// 生成 n 个点的随机树
auto GenTree(int n) {
    std::vector<std::pair<int, int>> res;
    std::vector<int> prufer(n - 1), deg(n + 1, 1);
    for (int i = 1; i <= n - 2; i ++) {
        prufer[i] = rand(1, n);
        deg[prufer[i]] ++;
    }
    int leaf = 0, p = 0;
    for (int i = 1; i <= n; i ++) {
        if (deg[i] == 1) {
            leaf = p = i;
            break;
        }
    }
    for (int i = 1; i <= n - 2; i ++) {
        int x = prufer[i];
        res.push_back({leaf, x});
        if (-- deg[x] == 1 && x < p) {
            leaf = x;
        } else {
            p ++;
            while (deg[p] != 1) p ++;
            leaf = p;
        }
    }
    if (n > 1) {
        res.push_back({leaf, n});
    }
    return res;
}
```

## 常用库函数重载

### i128

==0x11 i128.cpp==：重载了 `__int128` 的标准输入输出流。

```c++
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
```

### 整数除法精确取整

==0x11 整数除法精确取整.cpp==：

```c++
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
```

### 取最值

==0x11 取最值.cpp==：

```c++
template <class T>
inline void chmin(T &x, const T &y) {
    if (x > y) {
        x = y;
    }
}
template <class T>
inline void chmax(T &x, const T &y) {
    if (x < y) {
        x = y;
    }
}
```

### 取模

==0x11 取模.cpp==：

```c++
const int mod = 998244353; // 模数需要根据实际问题调整

template <class T>
inline int norm(T x) {
    x %= mod;
    return x < 0 ? x + mod : x;
}

inline void add(int &x, const int &y) {
    x += y; if (x >= mod) x -= mod;
}
inline void dec(int &x, const int &y) {
    x -= y; if (x < 0) x += mod;
}
inline void mul(int &x, const int &y) {
    x = 1ll * x * y % mod;
}
inline void neg(int &x) {
    if (x) x = mod - x;
}

template <class T>
constexpr int qpow(int a, T b, int p) {
    int ans = 1;
    for (; b; b >>= 1) {
        if (b & 1) ans = 1ll * ans * a % p;
        a = 1ll * a * a % p;
    }
    return ans;
}
```

### 精确开根号

==0x11 精确开根号.cpp==：

```c++
// 精确开根号：找到最大整数 d，使得 d * d <= n
i64 isqrt(i64 n) {
    i64 d = sqrt(n);
    while (d * d > n) {
        d --;
    }
    while ((d + 1) * (d + 1) <= n) {
        d ++;
    }
    return d;
}
```

### 精确取对数

==0x11 精确取对数.cpp==：

```c++
// 精确取对数（下取整）：找到最大整数 t，使得 a^t <= b
int ilog(i64 a, i64 b) {
    int t = 0;
    i64 v = 1;
    while (v <= b / a) {
        t ++;
        v *= a;
    }
    return t;
}

// 精确取对数（上取整）：找到最小整数 t，使得 a^t >= b
int iLog(i64 a, i64 b) {
    int t = 0;
    i64 v = 1;
    while (v < b) {
        t ++; if (v > b / a) break;
        v *= a;
    }
    return t;
}
```

### 快读

==0x11 快读.cpp==：

```c++
// 读入一个整数（无需在意类型）
template <class T>
inline void read(T &x) {
    char s;
    bool opt;
    while (s = getchar(), (s < '0' || s > '9') && s != '-');
    x = (opt = s == '-') ? 0 : s - '0';
    while (s = getchar(), s >= '0' && s <= '9') x = x * 10 + s - '0';
    if (opt) x = -x;
}
```

### 超级快读

==0x11 超级快读.cpp==：

```c++
/**
 * 注意，此代码的所有输出类函数，均不带“空格”与“换行”
 * 注意，虽然此代码使用了缓冲区，但不需要你手动清空，fastio 的析构函数会自动清空
 * 注意，此快读快写不能与 C/C++ 风格的 IO 混用，否则会导致 IO 的顺序混乱
 * 注意，如果你需要使用控制台调试，请在输入的最后使用 Ctrl+Z (Windows) 或 Ctrl+D (Linux/macOS) 手动输入 EOF 来结束输入
 */
struct fastio {
    static const int N = 1 << 20;

    char buf[N], *p1 = buf, *p2 = buf;
    #define gc() (p1 == p2 && (p2 = (p1 = buf) + fread(buf, 1, N, stdin), p1 == p2) ? EOF : *p1 ++)

    char pbuf[N], *pp = pbuf;
    void pc(const char &c) {
        if (pp - pbuf == N) fwrite(pbuf, 1, N, stdout), pp = pbuf;
        *pp ++ = c;
    }

    // 读入一个整数（无需在意类型）
    template <class T>
    void read(T &x) {
        char s;
        bool opt;
        while (s = gc(), (s < '0' || s > '9') && s != '-');
        x = (opt = s == '-') ? 0 : s - '0';
        while (s = gc(), s >= '0' && s <= '9') x = x * 10 + s - '0';
        if (opt) x = -x;
    }
    // 读入一个字符串
    void readString(std::string &x) {
        char s;
        while (s = gc(), std::isspace(s));
        x = s;
        while (s = gc(), !std::isspace(s)) x += s;
    }

    // 输出一个整数（无需在意类型）
    template <class T>
    void print(T x) {
        int top = 0; static int stk[40];
        if (x < 0) x = -x, pc('-');
        do {
            stk[++ top] = x % 10, x /= 10;
        } while (x);
        while (top) pc(stk[top --] + '0');
    }
    // 输出一个字符串（char 数组类型）
    void puts(const char *s) {
        while (*s) pc(*s), s ++;
    }
    // 输出一个字符串（std::string 类型）
    void puts(const std::string &s) {
        for (char ch : s) pc(ch);
    }

    ~fastio() {
        fwrite(pbuf, pp - pbuf, 1, stdout);
    }
} io;
```

## 高精度

==0x11 高精度.cpp==：

```c++
// 高精度
struct bint {
    static const int SIZE = 4000; // 位数上限需要根据实际问题调整
    int len, num[SIZE];

    explicit bint(int len = 1) : len(len) {
        memset(num, 0, sizeof(num));
    };

    auto operator <=> (const bint &b) const {
        if (len ^ b.len) return len <=> b.len;
        for (int i = len; i >= 1; i --)
            if (num[i] ^ b.num[i]) return num[i] <=> b.num[i];
        return std::strong_ordering::equal;
    }
    auto operator == (const bint &b) const {
        if (len ^ b.len) return false;
        for (int i = len; i >= 1; i --)
            if (num[i] ^ b.num[i]) return false;
        return true;
    }

    // 高精度加法
    bint operator + (const bint &b) const {
        bint c(std::max(len, b.len));
        for (int i = 1; i <= c.len; i ++) c.num[i] = num[i] + b.num[i];
        for (int i = 1; i <= c.len; i ++)
            if (c.num[i] >= 10) c.num[i + 1] ++, c.num[i] -= 10;
        while (c.num[c.len + 1]) {
            c.len ++;
            if (c.num[c.len] >= 10) c.num[c.len + 1] ++, c.num[c.len] -= 10;
        }
        return c;
    }
    // 高精度减法
    bint operator - (const bint &b) const {
        bint c(len);
        for (int i = 1; i <= c.len; i ++) c.num[i] = num[i] - b.num[i];
        for (int i = 1; i <= c.len; i ++)
            if (c.num[i] < 0) c.num[i + 1] --, c.num[i] += 10;
        while (c.len > 1 && !c.num[c.len]) c.len --;
        return c;
    }

    // 高精度乘以低精度
    bint operator * (const int &b) const {
        bint c(len);
        i64 x = 0;
        for (int i = 1; i <= len; i ++) {
            x += 1ll * num[i] * b;
            c.num[i] = x % 10, x /= 10;
        }
        while (x) {
            c.len ++;
            c.num[c.len] = x % 10, x /= 10;
        }
        while (c.len > 1 && !c.num[c.len]) c.len --;
        return c;
    }
    // 高精度乘以高精度
    bint operator * (const bint &b) const {
        bint c(len + b.len);
        for (int i = 1; i <= len; i ++) {
            for (int j = 1; j <= b.len; j ++) {
                c.num[i + j - 1] += num[i] * b.num[j];
            }
        }
        for (int i = 1; i <= c.len; i ++) {
            c.num[i + 1] += c.num[i] / 10;
            c.num[i] %= 10;
        }
        while (c.len > 1 && !c.num[c.len]) c.len --;
        return c;
    }

    // 高精度除以低精度（带余除法）
    std::pair<bint, int> divmod(const int &b) const {
        bint c(len);
        i64 r = 0;
        for (int i = len; i >= 1; i --) {
            c.num[i] = (r * 10 + num[i]) / b;
            r = (r * 10 + num[i]) % b;
        }
        while (c.len > 1 && !c.num[c.len]) c.len --;
        return {c, r};
    }
    // 高精度除以高精度（带余除法）
    std::pair<bint, bint> divmod(const bint &b) const {
        if (*this < b) return {bint(), *this};
        bint c(len - b.len + 1);
        bint r = *this;
        for (int i = c.len; i >= 1; i --) {
            bint tmp(b.len + i - 1);
            for (int j = 1; j <= b.len; j ++) {
                tmp.num[j + i - 1] = b.num[j];
            }
            while (tmp <= r) {
                r = r - tmp, c.num[i] ++;
            }
        }
        while (c.len > 1 && !c.num[c.len]) c.len --;
        return {c, r};
    }

    friend std::istream &operator >> (std::istream &is, bint &b) { // 默认没有前导 0
        std::string s;
        is >> s;
        b.len = s.length();
        memset(b.num, 0, sizeof(b.num));
        for (int i = 0; i < b.len; i ++) {
            b.num[b.len - i] = s[i] - '0';
        }
        return is;
    }
    friend std::ostream &operator << (std::ostream &os, const bint &b) {
        for (int i = b.len; i >= 1; i --) {
            os << b.num[i];
        }
        return os;
    }
};
```

## 分数类

==0x11 分数类.cpp==：

```c++
// 分数类
struct frac {
    i64 p, q;
    frac() : p(0), q(1) {}
    frac(i64 p, i64 q) : p(p), q(q) {} // 必要时，在此处规范化分数（保证 q>0 以及 p,q 最简）

    frac operator + (const frac &rhs) const {
        return frac(p * rhs.q + rhs.p * q, q * rhs.q);
    }
    frac operator - (const frac &rhs) const {
        return frac(p * rhs.q - rhs.p * q, q * rhs.q);
    }
    frac operator * (const frac &rhs) const {
        return frac(p * rhs.p, q * rhs.q);
    }
    frac operator / (const frac &rhs) const {
        return frac(p * rhs.q, q * rhs.p);
    }

    auto operator <=> (const frac &rhs) const { // 比较大小时，必须保证 q>0
        return i128(p) * rhs.q <=> i128(rhs.p) * q;
    }
    auto operator == (const frac &rhs) const {
        return i128(p) * rhs.q == i128(rhs.p) * q;
    }

    friend std::ostream &operator << (std::ostream &os, frac x) {
        i64 g = std::gcd(x.p, x.q);
        return os << x.p / g << '/' << x.q / g;
    }
};
```

