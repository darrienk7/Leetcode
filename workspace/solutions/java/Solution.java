import java.util.HashMap;
import java.util.Map;

// PLACEHOLDER: replace this method for the active problem.
class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();

        for (int index = 0; index < nums.length; index++) {
            int complement = target - nums[index];
            if (seen.containsKey(complement)) {
                return new int[] {seen.get(complement), index};
            }
            seen.put(nums[index], index);
        }

        return new int[0];
    }
}

