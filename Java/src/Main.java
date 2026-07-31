import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import leetcodeUtil.*;

public class Main {
    static Solution sol = new Solution();

    public static void main(String[] args) throws Exception {

        runTests();

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
        if (o == null) return "null";
        TypeAdapter<Object> adapter = TypeAdapters.find((Class<Object>) o.getClass());
        if (adapter != null) return adapter.stringify(o);
        if (o instanceof Object[]) return Arrays.deepToString((Object[]) o);
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

    private static void runTests() throws Exception {
        Class<?>[] paramTypes = getSolutionMethod().getParameterTypes();

        List<String> lines = Files.readAllLines(Path.of("testcases.txt"));
        lines.removeIf(String::isBlank);
        for (int i = 0; i + paramTypes.length <= lines.size(); i += paramTypes.length) {
            Object[] args = new Object[paramTypes.length];
            for (int j = 0; j < paramTypes.length; j++) {
                args[j] = TypeAdapters.get(paramTypes[j]).convert(parseValue(lines.get(i + j)));
            }
            test(args);
        }
    }

}