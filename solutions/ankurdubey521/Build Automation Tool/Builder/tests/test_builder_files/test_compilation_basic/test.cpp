#include<iostream>
#include<vector>

void sort_quick(std::vector<int>&);
void sort_merge(std::vector<int>&);
void sort_bubble(std::vector<int>&);

void print(const std::vector<int> &vec) {
    for(auto &x: vec) {
        std::cout << x << " ";
    }
    std::cout << "\n"; 
}

int main() {
    std::vector<int> a = {5, 4, 3, 2, 1}, b = a, c = a;
    sort_quick(a);
    sort_merge(b);
    sort_bubble(c);
    print(a);
    print(b);
    print(c);
    return 0;
}
