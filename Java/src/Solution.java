import java.util.Arrays;

class Solution {
    public int minimumPushes(String word) {
        int[] freqs = new int[26];
        int count = 0;
        int unique = 0;
        for (int i = 0; i < word.length(); i++) {
            freqs[word.charAt(i) - 'a']++;
        }
        Arrays.sort(freqs);
        for (int i = 25; i >= 0; i--) {
            if (freqs[i] != 0) {
                count++;
                if (count > 24) {
                    unique += freqs[i]*4;
                } else if (count > 16) {
                    unique += freqs[i]*3;
                } else if (count > 8) {
                    unique += freqs[i]*2;
                } else {
                    unique += freqs[i];
                }

            }
        }
        return unique;
    }
}