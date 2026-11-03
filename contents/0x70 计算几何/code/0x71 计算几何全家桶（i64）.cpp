// 二维点
struct point {
    i64 x, y;
    point() {}
    point(i64 x, i64 y) : x(x), y(y) {}
};

point operator + (point a, point b) {
    return point(a.x + b.x, a.y + b.y);
}
point operator - (point a, point b) {
    return point(a.x - b.x, a.y - b.y);
}
point operator * (point a, i64 b) {
    return point(a.x * b, a.y * b);
}

// 叉积
i128 cross(point a, point b) {
    return i128(a.x) * b.y - i128(a.y) * b.x;
}
// ab 与 ac 的叉积
// 检测连续三个点的凸性，按 x 递增时 >0 下凸 <0 上凸，按 x 递减时反之
i128 cross(point a, point b, point c) {
    return i128(b.x - a.x) * (c.y - a.y) - i128(c.x - a.x) * (b.y - a.y);
}