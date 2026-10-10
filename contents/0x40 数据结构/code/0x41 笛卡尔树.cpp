// 笛卡尔树（默认：大根堆）
namespace dkr {
    int rt;
    int lc[N], rc[N];

    int top, stk[N];
    void build() {
        for (int i = 1; i <= n; i ++) {
            lc[i] = rc[i] = 0;
        }

        top = 0;
        for (int i = 1; i <= n; i ++) {
            int k = top;
            while (k > 0 && a[stk[k]] < a[i]) { // 若要求小根堆，改成 ">"
                k --;
            }
            if (k > 0) rc[stk[k]] = i;
            if (k < top) lc[i] = stk[k + 1];
            stk[top = k + 1] = i;
        }
        rt = stk[1];
    }
}