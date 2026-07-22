import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import leetcodeUtil.*;
import static leetcodeUtil.ArgType.*;

public class Main {
    static Solution sol = new Solution();

    public static void main(String[] args) throws Exception {

        runTests(INT_MATRIX, INT);

    }

    @SafeVarargs
    private static <T> void test(T... args) throws InvocationTargetException, IllegalAccessException {
        System.out.println(stringify(getSolutionMethod().invoke(sol, args)));
    }

    private static Method getSolutionMethod() {
        Method[] methods = Solution.class.getDeclaredMethods();
        for (Method m : methods) {
            if (Modifier.isPublic(m.getModifiers())) {
                return m;
            }
        }
        return null;
    }

    private static String stringify(Object o) {
        if (o instanceof int[]) return Arrays.toString((int[]) o);
        if (o instanceof int[][]) return Arrays.deepToString((int[][]) o);
        if (o instanceof Object[]) return Arrays.deepToString((Object[]) o);
        if (o instanceof ListNode) {
            StringBuilder sb = new StringBuilder("[");
            for (ListNode n = (ListNode) o; n != null; n = n.next) {
                sb.append(n.val);
                if (n.next != null) sb.append(",");
            }
            return sb.append("]").toString();
        }
        return String.valueOf(o);
    }

    private static Object parseValue(String s) {
        s = s.trim();
        if (s.startsWith("[")) {
            List<Object> list = new ArrayList<>();
            int depth = 0, start = 1;
            for (int i = 1; i < s.length() - 1; i++) {
                char c = s.charAt(i);
                if (c == '[') depth++;
                else if (c == ']') depth--;
                else if (c == ',' && depth == 0) {
                    list.add(parseValue(s.substring(start, i)));
                    start = i + 1;
                }
            }
            if (start < s.length() - 1) list.add(parseValue(s.substring(start, s.length() - 1)));
            return list;
        }
        if (s.startsWith("\"") && s.endsWith("\"")) return s.substring(1, s.length() - 1);
        return switch (s) {
            case "null" -> null;
            case "true" -> true;
            case "false" -> false;
            default -> s.contains(".") ? (Object) Double.parseDouble(s) : (Object) Integer.parseInt(s);
        };
    }

    private static Object convert(Object raw, ArgType type) {
        switch (type) {
            case INT:      return ((Number) raw).intValue();
            case DOUBLE:   return ((Number) raw).doubleValue();
            case BOOLEAN:  return (Boolean) raw;
            case STRING:   return (String) raw;
            case INT_ARRAY: {
                List<?> list = (List<?>) raw;
                int[] arr = new int[list.size()];
                for (int i = 0; i < arr.length; i++) arr[i] = ((Number) list.get(i)).intValue();
                return arr;
            }
            case INT_MATRIX: {
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
            case STRING_ARRAY: {
                List<?> list = (List<?>) raw;
                String[] arr = new String[list.size()];
                for (int i = 0; i < arr.length; i++) arr[i] = (String) list.get(i);
                return arr;
            }
            case LINKED_LIST: {
                ListNode dummy = new ListNode(0), cur = dummy;
                for (Object o : (List<?>) raw) {
                    cur.next = new ListNode(((Number) o).intValue());
                    cur = cur.next;
                }
                return dummy.next;
            }
            default: throw new IllegalArgumentException("Unsupported type: " + type);
        }
    }

    private static void runTests(ArgType... signature) throws Exception {
        List<String> lines = Files.readAllLines(Path.of("testcases.txt"));
        lines.removeIf(String::isBlank);
        for (int i = 0; i + signature.length <= lines.size(); i += signature.length) {
            Object[] args = new Object[signature.length];
            for (int j = 0; j < signature.length; j++) {
                args[j] = convert(parseValue(lines.get(i + j)), signature[j]);
            }
            test(args);
        }
    }

}

