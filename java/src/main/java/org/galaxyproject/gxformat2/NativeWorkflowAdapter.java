package org.galaxyproject.gxformat2;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class NativeWorkflowAdapter implements WorkflowAdapter {
  private Map<String, Object> workflow;

  public NativeWorkflowAdapter(final Map<String, Object> workflow) {
    this.workflow = workflow;
  }

  @Override
  public List<NormalizedStep> normalizedSteps() {
    Map<String, Map<String, Object>> steps =
        (Map<String, Map<String, Object>>) this.workflow.get("steps");
    Map<Integer, String> orderIndexToLabel = new HashMap();
    for (Map.Entry<String, Map<String, Object>> stepEntry : steps.entrySet()) {
      Map<String, Object> stepDef = stepEntry.getValue();
      String label = (String) stepDef.get("label");
      if (label == null) {
        label = stepEntry.getKey();
      }
      orderIndexToLabel.put(Integer.parseInt(stepEntry.getKey()), label);
    }
    final List<NormalizedStep> normalizedSteps = new ArrayList();
    for (Map.Entry<String, Map<String, Object>> stepEntry : steps.entrySet()) {
      final NormalizedStep step = new NormalizedStep();
      final Map<String, Object> stepDef = stepEntry.getValue();
      ensurePosition(stepDef, Integer.parseInt(stepEntry.getKey()));
      step.stepDefinition = stepDef;
      step.inputs = new ArrayList<Input>();
      String doc = (String) stepDef.get("annotation");
      if (doc.equals("")) {
        // just how it translates to Format 2. Doesn't preserve empty annotations.
        doc = null;
      }
      step.doc = doc;
      final Map<String, Object> inputConnections =
          (Map<String, Object>) stepDef.get("input_connections");

      for (final Map.Entry<String, Object> inputConnectionListEntry : inputConnections.entrySet()) {
        final List<Map<String, Object>> inputConnectionsList;
        if (inputConnectionListEntry.getValue() instanceof Map) {
          inputConnectionsList =
              Arrays.asList((Map<String, Object>) inputConnectionListEntry.getValue());
        } else {
          inputConnectionsList = (List<Map<String, Object>>) inputConnectionListEntry.getValue();
        }
        final String inputName = inputConnectionListEntry.getKey();
        for (final Map<String, Object> inputConnection : inputConnectionsList) {
          String outputName = (String) inputConnection.get("output_name");
          if (outputName.equals("output")) {
            // HACKY - this would be implicit in Format 2 :(
            outputName = null;
          }
          final Integer outputIndex = (Integer) inputConnection.get("id");
          final String outputLabel = orderIndexToLabel.get(outputIndex);
          final Input input = new Input();
          input.inputName = inputName;
          input.sourceOutputName = outputName;
          input.sourceStepLabel = outputLabel;
          step.inputs.add(input);
        }
      }
      String label = (String) stepDef.get("label");
      if (label == null) {
        label = (String) stepDef.get("label");
      }
      if (label == null) {
        label = Integer.toString((int) stepDef.get("id"));
      }
      step.label = label;
      normalizedSteps.add(step);
    }
    return normalizedSteps;
  }
}
