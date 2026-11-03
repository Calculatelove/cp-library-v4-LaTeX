// 凸壳（默认：按 x 递增的上凸壳）
auto gethull(std::vector<point> s) {
    std::sort(s.begin(), s.end(), [] (point l, point r) -> bool {
        return l.x != r.x ? l.x < r.x : l.y > r.y; // 若要求下凸壳，改成 l.y < r.y
    });

    std::vector<point> h;
    for (point p : s) {
        if (h.size() && h.back().x == p.x) {
            continue;
        }
        while (h.size() >= 2 && cross(h.rbegin()[1], h.back(), p) >= 0) { // 若要求下凸壳，改成 <=
            h.pop_back();
        }
        h.push_back(p);
    }
    return h;
}