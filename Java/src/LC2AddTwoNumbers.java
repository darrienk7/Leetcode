import util.ListNode;

/*
Principal
Linked List
Math
Recursion
 */
public class LC2AddTwoNumbers {
    class Solution {
        public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
            return nodeHelp(l1, l2, 0);
        }

        private ListNode nodeHelp(ListNode l1, ListNode l2, int remainder) {
            if (l2 == null && l1 == null) {
                if (remainder != 0) {
                    return new ListNode(remainder);
                }
                return null;
            }
            if (l1 == null) l1 = new ListNode(0, null);
            if (l2 == null) l2 = new ListNode(0, null);
            ListNode node = new ListNode((l1.val + l2.val + remainder)%10);
            remainder = l1.val + l2.val + remainder >= 10 ? (l1.val + l2.val + remainder) / 10 : 0;
            node.next = nodeHelp(l1.next, l2.next, remainder);
            return node;
        }
    }
}
