// 라벨이 붙은 배치열을 하드드롭으로 재생해 퍼펙트 클리어인지 확인한다 (tunits.py 의 독립 검산용).
// 입력: argv[1] = 폭 w, argv[2] = "U@0,L@2,R@0,D@1" 형식의 배치열 (T 의 네 회전 U D L R).
// 출력: "w=.. pieces=.. clears=.. final=empty|nonempty : OK|MISMATCH". 비트마스크를 쓰지 않는다.
#include <bits/stdc++.h>
using namespace std;

int w, cap;
vector<vector<int>> grid;
map<char, vector<pair<int,int>>> shape;

void buildshapes() {
    vector<pair<int,int>> u;
    u.push_back(make_pair(0,0)); u.push_back(make_pair(0,1));
    u.push_back(make_pair(0,2)); u.push_back(make_pair(1,1));
    shape['U'] = u;
    vector<pair<int,int>> d;
    d.push_back(make_pair(0,1)); d.push_back(make_pair(1,0));
    d.push_back(make_pair(1,1)); d.push_back(make_pair(1,2));
    shape['D'] = d;
    vector<pair<int,int>> l;
    l.push_back(make_pair(0,1)); l.push_back(make_pair(1,0));
    l.push_back(make_pair(1,1)); l.push_back(make_pair(2,1));
    shape['L'] = l;
    vector<pair<int,int>> r;
    r.push_back(make_pair(0,0)); r.push_back(make_pair(1,0));
    r.push_back(make_pair(1,1)); r.push_back(make_pair(2,0));
    shape['R'] = r;
}

bool occupied(int r, int c) {
    if (r < 0) return true;
    if (r >= cap) return false;
    if (c < 0 || c >= w) return true;
    return grid[r][c] == 1;
}

bool collides(char label, int col, int r) {
    for (size_t k = 0; k < shape[label].size(); k++) {
        int rr = r + shape[label][k].first;
        int cc = col + shape[label][k].second;
        if (occupied(rr, cc)) return true;
    }
    return false;
}

int clearfull() {
    vector<vector<int>> keep;
    int cnt = 0;
    for (int r = 0; r < cap; r++) {
        int full = 1;
        for (int c = 0; c < w; c++) if (grid[r][c] == 0) full = 0;
        if (full == 1) { cnt++; continue; }
        keep.push_back(grid[r]);
    }
    while ((int)keep.size() < cap) keep.push_back(vector<int>(w, 0));
    grid = keep;
    return cnt;
}

int main(int argc, char **argv) {
    if (argc < 3) { printf("usage: ./tplay <w> <U@0,L@2,...>\n"); return 1; }
    w = atoi(argv[1]);
    buildshapes();
    string s = argv[2];
    vector<pair<char,int>> seq;
    size_t i = 0;
    while (i < s.size()) {
        size_t j = s.find(',', i);
        if (j == string::npos) j = s.size();
        string tok = s.substr(i, j - i);
        size_t at = tok.find('@');
        if (at == string::npos) { printf("bad token: %s\n", tok.c_str()); return 1; }
        char label = tok[0];
        int col = atoi(tok.substr(at + 1).c_str());
        if (shape.count(label) == 0) { printf("bad label: %c\n", label); return 1; }
        seq.push_back(make_pair(label, col));
        i = j + 1;
    }
    cap = 4 + 6;
    grid.assign(cap, vector<int>(w, 0));
    int clears = 0;
    for (size_t k = 0; k < seq.size(); k++) {
        char label = seq[k].first;
        int col = seq[k].second;
        int mw = 0;
        for (size_t t = 0; t < shape[label].size(); t++)
            mw = max(mw, shape[label][t].second + 1);
        if (col < 0 || col + mw > w) {
            printf("w=%d : placement %zu out of board\n", w, k + 1);
            return 1;
        }
        int r = cap;
        while (r > 0 && !collides(label, col, r - 1)) r--;
        for (size_t t = 0; t < shape[label].size(); t++) {
            int rr = r + shape[label][t].first;
            int cc = col + shape[label][t].second;
            if (rr >= cap) { printf("w=%d : placement %zu above cap\n", w, k + 1); return 1; }
            if (grid[rr][cc] == 1) { printf("w=%d : placement %zu overlaps\n", w, k + 1); return 1; }
            grid[rr][cc] = 1;
        }
        clears += clearfull();
    }
    int left = 0;
    for (int r = 0; r < cap; r++) for (int c = 0; c < w; c++) left += grid[r][c];
    int good = 0;
    if (left == 0 && clears == 4 && (int)seq.size() == w) good = 1;
    string verdict = "MISMATCH";
    if (good == 1) verdict = "OK";
    printf("w=%-3d pieces=%-3zu clears=%d cells_left=%-3d : %s\n",
           w, seq.size(), clears, left, verdict.c_str());
    if (good == 1) return 0;
    return 3;
}
