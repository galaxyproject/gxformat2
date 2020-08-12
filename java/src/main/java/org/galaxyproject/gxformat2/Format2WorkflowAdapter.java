package org.galaxyproject.gxformat2;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Format2WorkflowAdapter implements WorkflowAdapter {
  private Map<String, Object> workflow;

  public Format2WorkflowAdapter(final Map<String, Object> workflow) {
    this.workflow = workflow;
  }

  @Override
  public List<NormalizedStep> normalizedSteps() {
    List<Map<String, Object>> steps = stepsAsList(this.workflow, true);
    steps = convertInputsToSteps(this.workflow, steps);
    final List<NormalizedStep> normalizedSteps = new ArrayList();
    int orderIndex = 0;
    for (Map<String, Object> stepDef : steps) {
      final NormalizedStep step = new NormalizedStep();
      ensurePosition(stepDef, orderIndex);
      step.stepDefinition = stepDef;
      step.inputs = new ArrayList<Input>();
      Map<String, Object> in = new HashMap();
      if (stepDef.containsKey("in")) {
        in = (Map<String, Object>) stepDef.get("in");
      }
      for (final Map.Entry<String, Object> inputDef : in.entrySet()) {
        final String inputName = inputDef.getKey();
        String output = (String) inputDef.getValue();
        int splitAt = output.indexOf('/');
        String outputName = null;
        if (splitAt >= 0) {
          outputName = output.substring(splitAt + 1);
          output = output.substring(0, splitAt);
        }
        final WorkflowAdapter.Input input = new WorkflowAdapter.Input();
        input.sourceStepLabel = output;
        input.sourceOutputName = outputName;
        input.inputName = inputName;
        step.inputs.add(input);
      }
      step.doc = (String) stepDef.get("doc");
      step.label = (String) stepDef.get("label");
      normalizedSteps.add(step);
      orderIndex++;
    }
    return normalizedSteps;
  }

  private List<Map<String, Object>> convertInputsToSteps(
      Map<String, Object> workflow, List<Map<String, Object>> steps) {
    Map rawInputs = (Map) workflow.get("inputs");
    List<Map<String, Object>> newSteps = new ArrayList();
    List<Map<String, Object>> inputs = convertMapToIdListIfNeeded(rawInputs, false);
    for (final Map<String, Object> input : inputs) {
      final HashMap<String, Object> inputAsStep = new HashMap(input);
      String rawLabel = (String) inputAsStep.remove("label");
      String rawId = (String) inputAsStep.remove("id");
      String label = rawLabel != null ? rawLabel : rawId;

      String inputType = (String) inputAsStep.remove("type");
      if (inputType == null) {
        inputType = "data";
      }
      final String stepType;
      if (inputType.equals("File") || inputType.equals("data") || inputType.equals("data_input")) {
        stepType = "data_input";
      } else if (inputType.equals("collection")
          || inputType.equals("data_collection")
          || inputType.equals("data_collection_input")) {
        stepType = "data_collection_input";
      } else {
        stepType = "parameter_input";
        inputAsStep.put("parameter_type", inputType);
      }
      inputAsStep.put("type", stepType);
      inputAsStep.put("label", label);
      newSteps.add(inputAsStep);
    }
    for (Map<String, Object> step : steps) {
      newSteps.add(step);
    }
    return newSteps;
  }

  static List<Map<String, Object>> stepsAsList(
      final Map<String, Object> workflow, final boolean addLabel) {
    final Object stepsRaw = workflow.get("steps");
    return convertMapToIdListIfNeeded(stepsRaw, addLabel);
  }

  static List<Map<String, Object>> convertMapToIdListIfNeeded(Object stepsRaw, boolean addLabel) {
    if (stepsRaw instanceof List) {
      return (List<Map<String, Object>>) stepsRaw;
    }
    final List<Map<String, Object>> asList = new ArrayList();
    final Map<String, Object> stepsMap = (Map<String, Object>) stepsRaw;
    for (final Map.Entry<String, Object> entry : stepsMap.entrySet()) {
      Map<String, Object> step;
      if (entry.getValue() instanceof Map) {
        step = (Map<String, Object>) entry.getValue();
      } else {
        step = new HashMap();
        step.put("type", entry.getValue());
      }
      if (addLabel) {
        step.put("label", entry.getKey());
      } else {
        step.put("id", entry.getKey());
      }
      asList.add(step);
    }
    return asList;
  }
}
