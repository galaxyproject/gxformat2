package org.galaxyproject.gxformat2;

import java.io.File;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.Assert;

public class CytoscapeExamplesTest {

  // WIP!!!
  // @Test
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
      Assert.assertEquals(elementsById.size(), expectedElementsById.size());
    }
  }

  private static Map<String, Map<String, Object>> getElementsById(
      List<Map<String, Object>> elements) {
    Map<String, Map<String, Object>> elementsById = new HashMap();
    for (Map<String, Object> element : elements) {
      elementsById.put((String) element.get("id"), element);
    }
    return elementsById;
  }
}
