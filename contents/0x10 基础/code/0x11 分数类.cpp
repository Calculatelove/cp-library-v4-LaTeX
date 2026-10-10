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