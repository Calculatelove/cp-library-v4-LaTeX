// 素性测试与质因数分解
template <class T, auto qmul>
struct primeTools {
    constexpr T qpow(T a, T b, T p) {
        T ans = 1;
        for (; b; b >>= 1) {
            if (b & 1) ans = qmul(ans, a, p);
            a = qmul(a, a, p);
        }
        return ans;
    }

    std::mt19937_64 mtrand{std::random_device{}()};
    T rand(T l, T r) {
        std::uniform_int_distribution<T> range(l, r);
        return range(mtrand);
    }

    // 素性测试 Miller-Rabin
    bool isPrime(T n) {
        assert(n > 1);
        if (n % 2 == 0) return n == 2;
        if (n % 3 == 0) return n == 3;

        T t = __builtin_ctzll(n - 1);
        T u = (n - 1) >> t;

        int test = 6;
        while (test --) {
            T a = rand(2, n - 1);
            T v = qpow(a, u, n);
            if (v == 1 || v == n - 1) {
                continue;
            }
            for (int i = 1; i < t; i ++) {
                v = qmul(v, v, n);
                if (v == n - 1) {
                    break;
                }
            }
            if (v != n - 1) {
                return 0;
            }
        }
        return 1;
    }

    T walk(T n) {
        T c = rand(1, n - 1);
        T x = rand(1, n - 1), y, v, d;
        for (int k = 1;; k <<= 1) {
            y = x, v = 1;
            for (int i = 1; i <= k; i ++) {
                x = (qmul(x, x, n) + c) % n;
                v = qmul(v, x - y + n, n);
                if (i % 127 == 0 || i == k) {
                    d = std::gcd(v, n);
                    if (d > 1) return d;
                }
            }
        }
    }
    // 质因数分解 Pollard-Rho
    auto primeFactor(T n) {
        std::map<T, int> buc;
        std::function<void(T)> solve = [&] (T n) {
            if (n == 1) {
                return;
            }
            if (isPrime(n)) {
                buc[n] ++;
                return;
            }
            T d = 0;
            while (d = walk(n), d == n);
            solve(d), solve(n / d);
        };
        solve(n);
        return std::vector<std::pair<T, int>>(buc.begin(), buc.end());
    }
};

// primeTools<int, [] (int a, int b, int p) { return 1ll * a * b % p; }> mrpr;
// primeTools<i64, [] (i64 a, i64 b, i64 p) { return i128(a) * b % p; }> mrpr;
// primeTools<i64, [] (i64 a, i64 b, i64 p) {
//     i64 c = static_cast<long double>(a) * b / p + 1e-8;
//     i64 ans = a * b - c * p;
//     if (ans < 0) ans += p;
//     if (ans >= p) ans -= p;
//     return ans;
// }> mrpr;