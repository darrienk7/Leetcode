package leetcodeUtil;

import java.util.*;

/**
 * Central registry mapping a parameter's real Class<?> to the TypeAdapter that knows
 * how to build/print it. To support a new LeetCode type (TreeNode, char[][], etc.),
 * write one adapter and add one register(...) call below — nothing else changes.
 */
public final class TypeAdapters {

    private static final Map<Class<?>, TypeAdapter<?>> REGISTRY = new HashMap<>();

    private static final TypeAdapter<Integer> INT_ADAPTER = new TypeAdapter<>() {
        public Integer convert(Object raw) { return ((Number) raw).intValue(); }
        public String stringify(Integer value) { return String.valueOf(value); }
    };

    private static final TypeAdapter<Double> DOUBLE_ADAPTER = new TypeAdapter<>() {
        public Double convert(Object raw) { return ((Number) raw).doubleValue(); }
        public String stringify(Double value) { return String.valueOf(value); }
    };

    private static final TypeAdapter<Boolean> BOOLEAN_ADAPTER = new TypeAdapter<>() {
        public Boolean convert(Object raw) { return (Boolean) raw; }
        public String stringify(Boolean value) { return String.valueOf(value); }
    };

    private static final TypeAdapter<String> STRING_ADAPTER = new TypeAdapter<>() {
        public String convert(Object raw) { return (String) raw; }
        public String stringify(String value) { return value; }
    };

    private static final TypeAdapter<int[]> INT_ARRAY_ADAPTER = new TypeAdapter<>() {
        public int[] convert(Object raw) {
            List<?> list = (List<?>) raw;
            int[] arr = new int[list.size()];
            for (int i = 0; i < arr.length; i++) arr[i] = ((Number) list.get(i)).intValue();
            return arr;
        }
        public String stringify(int[] value) { return Arrays.toString(value); }
    };

    private static final TypeAdapter<int[][]> INT_MATRIX_ADAPTER = new TypeAdapter<>() {
        public int[][] convert(Object raw) {
            List<?> outer = (List<?>) raw;
            int[][] arr = new int[outer.size()][];
            for (int i = 0; i < arr.length; i++) {
                List<?> inner = (List<?>) outer.get(i);
                int[] row = new int[inner.size()];
                for (int j = 0; j < row.length; j++) row[j] = ((Number) inner.get(j)).intValue();
                arr[i] = row;
            }
            return arr;
        }
        public String stringify(int[][] value) { return Arrays.deepToString(value); }
    };

    private static final TypeAdapter<String[]> STRING_ARRAY_ADAPTER = new TypeAdapter<>() {
        public String[] convert(Object raw) {
            List<?> list = (List<?>) raw;
            String[] arr = new String[list.size()];
            for (int i = 0; i < arr.length; i++) arr[i] = (String) list.get(i);
            return arr;
        }
        public String stringify(String[] value) { return Arrays.toString(value); }
    };

    private static final TypeAdapter<ListNode> LINKED_LIST_ADAPTER = new TypeAdapter<>() {
        public ListNode convert(Object raw) {
            ListNode dummy = new ListNode(0), cur = dummy;
            for (Object o : (List<?>) raw) {
                cur.next = new ListNode(((Number) o).intValue());
                cur = cur.next;
            }
            return dummy.next;
        }
        public String stringify(ListNode value) {
            StringBuilder sb = new StringBuilder("[");
            for (ListNode n = value; n != null; n = n.next) {
                sb.append(n.val);
                if (n.next != null) sb.append(",");
            }
            return sb.append("]").toString();
        }
    };

    static {
        register(int.class, INT_ADAPTER);
        register(Integer.class, INT_ADAPTER);
        register(double.class, DOUBLE_ADAPTER);
        register(Double.class, DOUBLE_ADAPTER);
        register(boolean.class, BOOLEAN_ADAPTER);
        register(Boolean.class, BOOLEAN_ADAPTER);
        register(String.class, STRING_ADAPTER);
        register(int[].class, INT_ARRAY_ADAPTER);
        register(int[][].class, INT_MATRIX_ADAPTER);
        register(String[].class, STRING_ARRAY_ADAPTER);
        register(ListNode.class, LINKED_LIST_ADAPTER);

        // New type? One line, right here:
        // register(TreeNode.class, TREE_ADAPTER);
    }

    private static <T> void register(Class<T> type, TypeAdapter<T> adapter) {
        REGISTRY.put(type, adapter);
    }

    /** Used when converting a Solution parameter — a missing adapter is a real error. */
    @SuppressWarnings("unchecked")
    public static <T> TypeAdapter<T> get(Class<T> type) {
        TypeAdapter<?> adapter = REGISTRY.get(type);
        if (adapter == null) {
            throw new IllegalArgumentException(
                    "No TypeAdapter registered for " + type.getSimpleName() +
                            " — add one in TypeAdapters's static block.");
        }
        return (TypeAdapter<T>) adapter;
    }

    /** Used when stringifying a return value — no match just means "fall back to toString." */
    @SuppressWarnings("unchecked")
    public static <T> TypeAdapter<T> find(Class<T> type) {
        return (TypeAdapter<T>) REGISTRY.get(type);
    }

    private TypeAdapters() {}
}