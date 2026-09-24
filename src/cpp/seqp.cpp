// seq.cpp 와 같은 고정 수열 탐색이되, 단계마다 phi 와 클리어 보정항을 함께 찍는다 (A 항등식 손검산용).
// 입력: argv[1]=폭 w, argv[2]=조각 문자열.
// 출력: step 별 "phi X->Y | clear-corr Z" 와 마지막에 #T 및 보정항 합.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned __int128 bb;

int w, hcap, totclear;
vector<vector<int>> oricell;
vector<int> oripiece, oriwidth;
vector<int> seq;
vector<int> chosen;
int lastclearcount;

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
                seen.insert(key);
                oricell.push_back(key); oripiece.push_back(p);
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

bb clearlines(bb board) {
    bb full = ((bb)1 << w) - (bb)1, out = 0;
    int outrow = 0, cnt = 0;
    for (int r = 0; r < hcap; r++) {
        bb row = (board >> (r*w)) & full;
        if (row == full) { cnt++; continue; }
        out = out | (row << (outrow*w));
        outrow++;
    }
    lastclearcount = cnt;
    return out;
}

int heightof(bb board) {
    int h = 0;
    for (int r = 0; r < hcap; r++)
        if (((board >> (r*w)) & (((bb)1 << w)-(bb)1)) != 0) h = r+1;
    return h;
}

bool dfs(bb board, int k, int clears) {
    if (k == (int)seq.size()) return board == 0;
    for (size_t oi = 0; oi < oricell.size(); oi++) {
        if (oripiece[oi] != seq[k]) continue;
        for (int col = 0; col + oriwidth[oi] <= w; col++) {
            int r = hcap;
            while (r > 0 && !collides(board, (int)oi, col, r-1)) r--;
            bool over = false;
            bb b2 = board;
            for (int t = 0; t < 4; t++) {
                int rr = r + oricell[oi][2*t], cc = col + oricell[oi][2*t+1];
                if (rr >= hcap) { over = true; break; }
                b2 = b2 | ((bb)1 << bitindex(rr,cc));
            }
            if (over) continue;
            b2 = clearlines(b2);
            int nc = clears + lastclearcount;
            if (nc > totclear) continue;
            if (heightof(b2) > totclear - nc) continue;
            chosen.push_back((int)(oi*100 + col));
            if (dfs(b2, k+1, nc)) return true;
            chosen.pop_back();
        }
    }
    return false;
}

int main(int argc, char **argv) {
    w = atoi(argv[1]);
    string s = argv[2];
    string names = "IOTSZJL";
    for (size_t i = 0; i < s.size(); i++) seq.push_back((int)names.find(s[i]));
    totclear = 4*(int)seq.size()/w;
    hcap = totclear + 4;
    // 보드 비트폭. hcap*w <= 128 이어야 한다. 넘으면 조용히 틀린다 (2026-09-15 추가).
    if (hcap * w > 128) {
        printf("w=%d seq=%s: REFUSED  hcap*w = %d > 128, board does not fit __int128\n", w, argv[2], hcap * w);
        return 2;
    }
    buildorientations();
    if (!dfs(0, 0, 0)) { printf("w=%d seq=%s : NO perfect clear\n", w, argv[2]); return 0; }
    printf("w=%d seq=%s : PERFECT CLEAR FOUND\n", w, argv[2]);
    bb board = 0; long long totcorr=0; int tcount=0;
    for (size_t i = 0; i < chosen.size(); i++) {
        int oi = chosen[i]/100, col = chosen[i]%100;
        int r = hcap;
        while (r > 0 && !collides(board, oi, col, r-1)) r--;
        for (int t = 0; t < 4; t++)
            board = board | ((bb)1 << bitindex(r+oricell[oi][2*t], col+oricell[oi][2*t+1]));
        long long phibefore=0;
        for(int rr=0;rr<hcap;rr++) for(int cc=0;cc<w;cc++) if((board>>bitindex(rr,cc))&(bb)1) phibefore += 1-2*((rr+cc)&1);
        board = clearlines(board);
        long long phiafter=0;
        for(int rr=0;rr<hcap;rr++) for(int cc=0;cc<w;cc++) if((board>>bitindex(rr,cc))&(bb)1) phiafter += 1-2*((rr+cc)&1);
        long long corr=(phiafter-phibefore)/2;
        totcorr += corr;
        if(oripiece[oi]==2) tcount++;
        printf("step %2d: %c col%d -> cleared %d | phi %lld->%lld | clear-corr %lld\n", (int)i+1, names[oripiece[oi]], col, lastclearcount, phibefore, phiafter, corr);
        for (int rr = hcap-1; rr >= 0; rr--) {
            printf("         ");
            for (int cc = 0; cc < w; cc++) {
                if ((board >> bitindex(rr,cc)) & (bb)1) printf("#"); else printf(".");
            }
            printf("\n");
        }
    }
    printf("\n#T = %d   sum of clear-corrections = %lld\n", tcount, totcorr);
    printf("CHECK:  #T mod 2 = %d ,  (-corr) mod 2 = %d  -> %s\n", tcount&1, (int)(((-totcorr)%2+2)%2), ((tcount&1)==(int)(((-totcorr)%2+2)%2))?"INVARIANT HOLDS":"VIOLATED");
    return 0;
}
