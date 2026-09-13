#include <iostream>
#include "LC1TwoSum.cpp"

using namespace std;

int main() {
    Solution solution;
    vector<int> nums = {2,7,11,15};

    vector<int> ans = solution.twoSum(nums, 9);

    cout << ans[0] << " " << ans[1];

    return 0;
}
