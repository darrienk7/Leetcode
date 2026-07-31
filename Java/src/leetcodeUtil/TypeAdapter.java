package leetcodeUtil;

/**
 * Knows how to convert a parsed literal (Integer, List, nested List, etc. — whatever
 * parseValue() produces) into a real Java value of type T, and how to print a T back
 * out for display. One adapter = one LeetCode-relevant type.
 */
public interface TypeAdapter<T> {
    T convert(Object raw);
    String stringify(T value);
}