package org.galaxyproject.gxformat2;

import java.util.HashMap;
import java.util.Map;

class LintUtils {
  static <T> T ensureKey(
      LintContext lintContext, Object hasKeys, String key, Class<T> hasClass, Object hasValue) {
    if (!(hasKeys instanceof Map)) {
      lintContext.error("expected [%s] to be a dictionary type", hasKeys);
      return null;
    }
    final Map<String, Object> map = (Map<String, Object>) hasKeys;
    if (!map.containsKey(key)) {
      lintContext.error("expected to have key [%s] but absent", key);
    }
    final Object value = map.get(key);
    return ensureKeyHasValue(lintContext, map, key, value, hasClass, hasValue);
  }

  static <T> T ensureKeyIfPresent(
      LintContext lintContext, Object hasKeys, String key, T defaultValue, Class<T> hasClass) {
    if (!(hasKeys instanceof Map)) {
      lintContext.error("expected [%s] to be a dictionary type", hasKeys);
      return null;
    }
    final Map<String, Object> map = (Map<String, Object>) hasKeys;
    if (!map.containsKey(key)) {
      return defaultValue;
    }
    final Object value = map.get(key);
    return ensureKeyHasValue(lintContext, map, key, value, hasClass, null);
  }

  static <T> T ensureKeyHasValue(
      LintContext lintContext,
      Map hasKeys,
      String key,
      Object value,
      Class<T> hasClass,
      Object hasValue) {
    if (value != null && !hasClass.isInstance(value)) {
      lintContext.error(
          "expected value [%s] with key [%s] to be of class %s", key, value, hasClass);
      return null;
    }
    if (hasValue != null && !hasValue.equals(value)) {
      lintContext.error("expected value [%s] with key [%s] to be %s", key, value, hasValue);
    }
    return (T) value;
  }

  static void lintStepErrors(LintContext lintContext, Map<String, Object> step) {
    final String errors = ensureKeyIfPresent(lintContext, step, "errors", null, String.class);
    if (errors != null) {
      lintContext.warn("tool step contains error indicated during Galaxy export - " + errors);
    }
  }

  static Map<String, Object> stepMap(LintContext lintContext, Map<String, Object> workflow) {
    Map<String, Object> steps =
        (Map<String, Object>) LintUtils.ensureKey(lintContext, workflow, "steps", Map.class, null);
    if (steps == null) {
      steps = new HashMap<String, Object>();
    }
    return steps;
  }
}
