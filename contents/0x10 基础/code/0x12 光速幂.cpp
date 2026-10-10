// 光速幂
struct flashPower {
    int b;
    std::vector<int> w1, w2;

    flashPower() {}
    flashPower(int a, int n) {
        init(a, n);
    }

    void init(int a, int n) {
        b = sqrt(n) + 1;
        w1.resize(b + 1), w2.resize(b + 1);

        w1[0] = 1;
        for (int i = 1; i <= b; i ++) {
            w1[i] = 1ll * w1[i - 1] * a % mod;
        }

        w2[0] = 1;
        for (int i = 1; i <= b; i ++) {
            w2[i] = 1ll * w2[i - 1] * w1[b] % mod;
        }
    }

    int pow(int n) {
        return 1ll * w2[n / b] * w1[n % b] % mod;
    }
} fp;