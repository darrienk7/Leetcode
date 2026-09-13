class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> seen;

        for (int index = 0; index < static_cast<int>(nums.size()); ++index) {
            int complement = target - nums[index];
            if (seen.contains(complement)) {
                return {seen[complement], index};
            }
            seen[nums[index]] = index;
        }

        return {};
    }
};

