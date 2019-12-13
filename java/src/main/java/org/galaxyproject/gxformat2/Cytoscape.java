package org.galaxyproject.gxformat2;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Cytoscape {

  public static List<Map<String, Object>> getElements(final String path) throws Exception {
    // assert args.length == 2;
    final Map<String, Object> object = (Map<String, Object>) IoUtils.readYamlFromPath(path);
    final String wfClass = (String) object.get("class");
    WorkflowAdapter adapter;
    if (wfClass == null) {
      adapter = new NativeWorkflowAdapter(object);
    } else {
      throw new NullPointerException("Adapter for Cytoscape to Format 2 not yet implemented");
    }
    int orderIndex = 0;
    final List<Map<String, Object>> elements = new ArrayList();
    for (Map<String, Object> step : adapter.normalizedSteps()) {
      String stepId =
          step.get("label") != null ? (String) step.get("label") : Integer.toString(orderIndex);
      String stepType = step.get("type") != null ? (String) step.get("type") : "tool";
      List<String> classes = new ArrayList(Arrays.asList("type_" + stepType));
      if (stepType.equals("tool") || stepType.equals("subworkflow")) {
        classes.add("runnable");
      } else {
        classes.add("input");
      }
      final Map<String, Object> nodeElement = new HashMap<String, Object>();
      nodeElement.put("classes", classes);
      nodeElement.put("id", stepId);
      elements.add(nodeElement);
      orderIndex++;
    }
    return elements;
  }
}
