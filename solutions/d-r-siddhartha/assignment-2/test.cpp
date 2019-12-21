#include<iostream>
#include<vector>

using namespace std;

void sort(vector<int> &list);

void display(vector<int> &list, int size)
{
   for(int i = 0; i<size; i++)
      cout << list[i] << " ";
   cout << endl;
}

int main()
{
    vector<int> arr{1, 3, 2, 5, 4};

    sort(arr);

    display(arr, 5);

    return 0;
}
