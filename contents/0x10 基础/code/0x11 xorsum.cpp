i64 xorsum(i64 n) {
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