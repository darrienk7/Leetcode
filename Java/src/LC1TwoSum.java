import java.util.HashMap;

/*
Junior
Array
Hash Table
 */

public class LC1TwoSum {
    class Solution {
        public int[] twoSum(int[] nums, int target) {
            HashMap<Integer, Integer> m = new HashMap<>();
            for (int i = 0; i < nums.length; i++) {
                int check = target - nums[i];
                if (m.containsKey(check)) {
                    return new int[] {i, m.get(check)};
                }
                m.put(nums[i], i);
            }
            return new int[] {};
        }
    }
}