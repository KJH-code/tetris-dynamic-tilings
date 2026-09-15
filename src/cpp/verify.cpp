// 동적 T-패리티 항등식을 퍼펙트 클리어 플레이 수열 전수로 검증한다 (dedup 없이 완전 열거).
// 입력: argv[1]=폭 w, argv[2]=조각 수 n, argv[3]=조각 마스크 (기본 127).
// 출력: PC 수열 개수와 네 항목(per-event / global / sum(A) odd / readable)의 실패 건수. 전부 0 이어야 정상.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned __int128 bb;

int w, hcap, target, totclear, pmask;
vector<vector<int>> oricell;
vector<int> oripiece, oriwidth;

int basecell[7][8] = {
    {0,0, 0,1, 0,2, 0,3}, {0,0, 0,1, 1,0, 1,1}, {0,0, 0,1, 0,2, 1,1},
    {0,0, 0,1, 1,1, 1,2}, {0,1, 0,2, 1,0, 1,1}, {0,0, 0,1, 0,2, 1,0},
    {0,0, 0,1, 0,2, 1,2}
};

void buildorientations() {
    for (int p = 0; p < 7; p++) {
        set<vector<int>> seen;
        vector<int> cur;
        for (int k = 0; k < 8; k++) cur.push_back(basecell[p][k]);
        for (int rot = 0; rot < 4; rot++) {
            int minr = 100, minc = 100;
            for (int k = 0; k < 4; k++) { minr = min(minr, cur[2*k]); minc = min(minc, cur[2*k+1]); }
            vector<pair<int,int>> pts;
            for (int k = 0; k < 4; k++) pts.push_back(make_pair(cur[2*k]-minr, cur[2*k+1]-minc));
            sort(pts.begin(), pts.end());
            vector<int> key;
            for (int k = 0; k < 4; k++) { key.push_back(pts[k].first); key.push_back(pts[k].second); }
            if (seen.count(key) == 0) {
                seen.insert(key); oricell.push_back(key); oripiece.push_back(p);
                int mw = 0;
                for (int k = 0; k < 4; k++) mw = max(mw, key[2*k+1]+1);
                oriwidth.push_back(mw);
            }
            vector<int> nxt;
            for (int k = 0; k < 4; k++) { nxt.push_back(cur[2*k+1]); nxt.push_back(-cur[2*k]); }
            cur = nxt;
        }
    }
}

int bitindex(int r, int c) { return r*w + c; }

bool collides(bb board, int oi, int col, int r) {
    for (int k = 0; k < 4; k++) {
        int rr = r + oricell[oi][2*k], cc = col + oricell[oi][2*k+1];
        if (rr >= hcap) continue;
        if ((board >> bitindex(rr,cc)) & (bb)1) return true;
    }
    return false;
}

long long phiof(bb board) {
    long long s = 0;
    for (int r = 0; r < hcap; r++)
        for (int c = 0; c < w; c++)
            if ((board >> bitindex(r,c)) & (bb)1) s += 1 - 2*((r+c)&1);
    return s;
}

// cells strictly above row j, EXCLUDING rows that are themselves full (cleared)
int cellsabove(bb board, int j) {
    bb full = ((bb)1 << w) - (bb)1;
    int n = 0;
    for (int r = j+1; r < hcap; r++) {
        if (((board >> (r*w)) & full) == full) continue;
        for (int c = 0; c < w; c++)
            if ((board >> bitindex(r,c)) & (bb)1) n++;
    }
    return n;
}

int heightof(bb board) {
    int h = 0;
    for (int r = 0; r < hcap; r++)
        if (((board >> (r*w)) & (((bb)1 << w)-(bb)1)) != 0) h = r+1;
    return h;
}

long long npc = 0, nmismatch = 0, nglobalbad = 0, naodd = 0, nreadbad = 0;
// per-event data buckets for odd width analysis: key = (k rows, C1 parity, altsum parity) -> corr parity counts
map<vector<int>, vector<long long>> bucket;

void dfs(bb board, int k, int clears, int tcount, long long corrsum, long long extrasum, long long extrasum2) {
    if (k == target) {
        if (board != 0) return;
        npc++;
        // global:  sum of dphi  ==  2*#T  (mod 4)
        long long lhs = ((corrsum % 4) + 4) % 4;
        long long rhs = ((2*tcount) % 4 + 4) % 4;
        if (lhs != rhs) nglobalbad++;
        // readable form:  #T  ==  sum(D) + sum(A)/2   (mod 2)
        if (extrasum2 % 2 != 0) naodd++;
        else {
          long long f = (((extrasum + extrasum2/2) % 2) + 2) % 2;
          if (f != ((tcount % 2) + 2) % 2) nreadbad++;
        }
        return;
    }
    for (size_t oi = 0; oi < oricell.size(); oi++) {
        if (((pmask >> oripiece[oi]) & 1) == 0) continue;
        for (int col = 0; col + oriwidth[oi] <= w; col++) {
            int r = hcap;
            while (r > 0 && !collides(board, (int)oi, col, r-1)) r--;
            bool over = false;
            bb pre = board;
            for (int t = 0; t < 4; t++) {
                int rr = r + oricell[oi][2*t], cc = col + oricell[oi][2*t+1];
                if (rr >= hcap) { over = true; break; }
                pre = pre | ((bb)1 << bitindex(rr,cc));
            }
            if (over) continue;
            // find cleared rows
            bb full = ((bb)1 << w) - (bb)1;
            vector<int> rows;
            for (int rr = 0; rr < hcap; rr++)
                if (((pre >> (rr*w)) & full) == full) rows.push_back(rr);
            bb post = 0;
            int outrow = 0;
            for (int rr = 0; rr < hcap; rr++) {
                bb row = (pre >> (rr*w)) & full;
                if (row == full) continue;
                post = post | (row << (outrow*w));
                outrow++;
            }
            int nc = clears + (int)rows.size();
            if (nc > totclear) continue;
            if (heightof(post) > totclear - nc) continue;

            long long corr = 0, c1 = 0, alt = 0;
            if (!rows.empty()) {
                corr = phiof(post) - phiof(pre);
                for (size_t i = 0; i < rows.size(); i++) {
                    c1 += cellsabove(pre, rows[i]);
                    alt += (w & 1) * (1 - 2*(rows[i] & 1));
                }
                // conjecture:  dphi  ==  -2*D - A   (mod 4)
                long long pred = -2*c1 - alt;
                int cp = (int)(((corr % 4) + 4) % 4);
                int pp = (int)(((pred % 4) + 4) % 4);
                if (cp != pp) nmismatch++;
                vector<int> key;
                key.push_back((int)rows.size());
                key.push_back((int)((((-2*c1-alt) % 4) + 4) % 4));
                key.push_back((int)(((alt % 2) + 2) % 2));
                key.push_back(cp);
                if (bucket.count(key) == 0) bucket[key] = vector<long long>(1, 0);
                bucket[key][0]++;
            }
            int nt = tcount;
            if (oripiece[oi] == 2) nt++;
            dfs(post, k+1, nc, nt, corrsum + corr, extrasum + c1, extrasum2 + alt);
        }
    }
}

int main(int argc, char **argv) {
    w = atoi(argv[1]);
    target = atoi(argv[2]);
    pmask = 127;
    if (argc > 3) pmask = atoi(argv[3]);
    if ((4*target) % w != 0) { printf("w=%d n=%d: skip\n", w, target); return 0; }
    totclear = 4*target/w;
    hcap = totclear + 4;
    buildorientations();
    dfs((bb)0, 0, 0, 0, 0, 0, 0);
    printf("w=%2d n=%2d | PC: %lld | per-event [dphi = -2D-A mod 4] fail: %lld | global [sum dphi = 2#T mod 4] fail: %lld | sum(A) odd: %lld | readable [#T = sumD + sumA/2 mod 2] fail: %lld\n",
           w, target, npc, nmismatch, nglobalbad, naodd, nreadbad);
    if (nmismatch > 0) {
        printf("   buckets  [k rows, C1 par, alt par, corr par] -> count\n");
        for (map<vector<int>, vector<long long>>::iterator it = bucket.begin(); it != bucket.end(); ++it) {
            printf("   [%d %d %d %d] -> %lld\n", it->first[0], it->first[1], it->first[2], it->first[3], it->second[0]);
        }
    }
    return 0;
}
