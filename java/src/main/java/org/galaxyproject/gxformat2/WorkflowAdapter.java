package org.galaxyproject.gxformat2;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public interface WorkflowAdapter {
  List<NormalizedStep> normalizedSteps();

  class NormalizedStep {
    Map<String, Object> stepDefinition;
    List<Input> inputs;
    String label;
    String doc;
  }

  class Input {
    String sourceOutputName;
    String sourceStepLabel;
    String inputName;
  }

  default void ensurePosition(final Map<String, Object> step, final int orderIndex) {
    if (!step.containsKey("position")) {
      Map<String, Integer> position = new HashMap();
      position.put("left", 10 * orderIndex);
      position.put("top", 10 * orderIndex);
      step.put("position", position);
    }
  }
}
