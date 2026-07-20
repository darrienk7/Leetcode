#include <vector>
#include <unordered_map>
using namespace std;

/*
Junior
Array
Hash Table
 */

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int,int> map;

        for(int i = 0; i < nums.size(); i++) {
            int needed = target - nums[i];

            if(map.count(needed)) {
                return {map[needed], i};
            }

            map[nums[i]] = i;
        }

        return {};
    }
};
