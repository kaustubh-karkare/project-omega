#include<iostream>

using namespace std;



//random comment

void quickSort(int arr[], int low, int high);
void mergeSort(int array[], int l, int r);
void bubbleSort(int arr[], int n); 

void display(int *array, int size) 
{
   for(int i = 0; i<size; i++)
      cout << array[i] << " ";
   cout << endl;
}

int main()
{
    int arr_1[5] = {1, 3, 2, 5, 4};
    int arr_2[5] = {3, 2, 1, 5, 4};
    int arr_3[5] = {5, 4, 3, 2, 1};
    
    bubbleSort(arr_1, 5);
    mergeSort(arr_2, 0, 4);
    quickSort(arr_3, 0, 4);
    
    display(arr_1, 5);
    display(arr_2, 5);
    display(arr_3, 5);
    
    return 0;
}
    
