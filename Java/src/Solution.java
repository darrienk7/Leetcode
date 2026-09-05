class Solution {
    public int firstStableIndex(int[] nums, int k) {
        int max = 0;
        for (int i = 0; i < nums.length; i++) {
            max = Math.max(max, nums[i]);
            int min = nums[i];
            for (int j = i; j < nums.length; j++) {
                min = Math.min(min, nums[j]);
            }
            if (max - min <= k) {
                return i;
            }
        }
        return -1;
    }
}