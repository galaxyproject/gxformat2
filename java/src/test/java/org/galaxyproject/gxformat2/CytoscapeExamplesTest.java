package org.galaxyproject.gxformat2;

import java.io.File;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.Assert;
import org.junit.Test;

public class CytoscapeExamplesTest {

  @Test
  public void testExamples() throws Exception {
    for (final File file : TestUtils.getExamples("cytoscape")) {
      final String path = file.getAbsolutePath();
      if (path.endsWith("json")) {
        continue;
      }
      final String fileName = file.getName();
      final int extensionLength;
      if (fileName.endsWith(".ga")) {
        extensionLength = 3;
      } else {
        extensionLength = 4;
      }
      final Path expected =
          file.toPath()
              .resolveSibling(
                  fileName.substring(0, fileName.length() - extensionLength) + ".cytoscape.json");
      List<Map<String, Object>> expectedElements =
          (List<Map<String, Object>>) IoUtils.readYamlFromPath(expected);
      List<Map<String, Object>> elements = Cytoscape.getElements(path);
      Map<String, Map<String, Object>> elementsById = getElementsById(elements);
      Map<String, Map<String, Object>> expectedElementsById = getElementsById(expectedElements);
      Assert.assertEquals(expectedElementsById.size(), elementsById.size());
      for (final Map.Entry<String, Map<String, Object>> elementEntry : elementsById.entrySet()) {
        final String elementKey = elementEntry.getKey();
        Assert.assertTrue(expectedElementsById.containsKey(elementKey));
        assertElementsEqual(expectedElementsById.get(elementKey), elementEntry.getValue());
      }
    }
  }

  private static void assertElementsEqual(
      final Map<String, Object> expectedElements, final Map<String, Object> actualObjects) {
    for (Map.Entry entry : expectedElements.entrySet()) {
      Object key = entry.getKey();
      Assert.assertTrue("Actual elements lacks key " + key, actualObjects.containsKey(key));
      final Object expectedValue = entry.getValue();
      final Object actualValue = actualObjects.get(key);
      if (actualValue instanceof Map) {
        Assert.assertTrue(expectedValue instanceof Map);
        assertElementsEqual((Map<String, Object>) actualValue, (Map<String, Object>) expectedValue);
      } else if (actualValue instanceof Long || actualValue instanceof Integer) {
        Assert.assertTrue(expectedValue instanceof Long || expectedValue instanceof Integer);
        Assert.assertEquals(asLong(expectedValue), asLong(actualValue));
      } else {
        Assert.assertEquals("Elements not equal for key " + key, expectedValue, actualValue);
      }
    }
  }

  static long asLong(Object object) {
    if (object instanceof Integer) {
      return ((Integer) object).longValue();
    } else {
      return (Long) object;
    }
  }

  private static Map<String, Map<String, Object>> getElementsById(
      List<Map<String, Object>> elements) {
    Map<String, Map<String, Object>> elementsById = new HashMap();
    for (Map<String, Object> element : elements) {
      elementsById.put((String) ((Map<String, Object>) element.get("data")).get("id"), element);
    }
    return elementsById;
  }
}
