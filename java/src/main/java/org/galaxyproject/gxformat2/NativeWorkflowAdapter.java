package org.galaxyproject.gxformat2;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class NativeWorkflowAdapter implements WorkflowAdapter {
  private Map<String, Object> workflow;

  static class LabelTracker {}

  public NativeWorkflowAdapter(final Map<String, Object> workflow) {
    this.workflow = workflow;
  }

  @Override
  public List<Map<String, Object>> normalizedSteps() {
    Map<String, Map<String, Object>> steps =
        (Map<String, Map<String, Object>>) this.workflow.get("steps");
    Map<Integer, String> orderIndexToLabel = new HashMap<Integer, String>();
    for (Map.Entry<String, Map<String, Object>> stepEntry : steps.entrySet()) {
      Map<String, Object> stepDef = stepEntry.getValue();
      String label = (String) stepDef.get("label");
      orderIndexToLabel.put(Integer.parseInt(stepEntry.getKey()), label);
    }
    List<Map<String, Object>> normalizedSteps = new ArrayList();
    for (Map.Entry<String, Map<String, Object>> stepEntry : steps.entrySet()) {
      normalizedSteps.add(stepEntry.getValue());
    }
    return normalizedSteps;
  }
}
