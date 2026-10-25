// 线性筛
int primeCount, prime[MaxV], fac[MaxV];
void sieve(int n) {
    for (int i = 2; i <= n; i ++) {
        if (!fac[i]) {
            prime[++ primeCount] = i, fac[i] = i;
        }
        for (int j = 1; j <= primeCount; j ++) {
            if (prime[j] > fac[i] || prime[j] > n / i) break;
            fac[i * prime[j]] = prime[j];
        }
    }
}