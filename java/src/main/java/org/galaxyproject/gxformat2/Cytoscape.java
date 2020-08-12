package org.galaxyproject.gxformat2;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Cytoscape {
  public static final String MAIN_TS_PREFIX = "toolshed.g2.bx.psu.edu/repos/";

  public static List<Map<String, Object>> getElements(final String path) throws Exception {
    final Map<String, Object> object = (Map<String, Object>) IoUtils.readYamlFromPath(path);
    final String wfClass = (String) object.get("class");
    WorkflowAdapter adapter;
    if (wfClass == null) {
      adapter = new NativeWorkflowAdapter(object);
    } else {
      adapter = new Format2WorkflowAdapter(object);
    }
    int orderIndex = 0;
    final List<Map<String, Object>> elements = new ArrayList();
    for (final WorkflowAdapter.NormalizedStep normalizedStep : adapter.normalizedSteps()) {
      final Map<String, Object> step = normalizedStep.stepDefinition;
      String stepId =
          step.get("label") != null ? (String) step.get("label") : Integer.toString(orderIndex);
      String stepType = step.get("type") != null ? (String) step.get("type") : "tool";
      String effectiveType = stepType;
      if (stepType.equals("data_input")) {
        effectiveType = "data";
      } else if (stepType.equals("data_collection_input")) {
        effectiveType = "collection";
      } else if (stepType.equals("parameter_input")) {
        effectiveType = (String) step.get("parameter_type");
      }
      List<String> classes = new ArrayList(Arrays.asList("type_" + effectiveType));
      if (stepType.equals("tool") || stepType.equals("subworkflow")) {
        classes.add("runnable");
      } else {
        classes.add("input");
      }
      String toolId = (String) step.get("tool_id");
      if (toolId != null && toolId.startsWith(MAIN_TS_PREFIX)) {
        toolId = toolId.substring(MAIN_TS_PREFIX.length());
      }
      String label = normalizedStep.label;
      if ((label == null || isOrderIndexLabel(label)) && toolId != null) {
        label = "tool:" + toolId;
      }
      final String repoLink;
      if (step.containsKey("tool_shed_repository")) {
        final Map<String, String> repo = (Map<String, String>) step.get("tool_shed_repository");
        repoLink =
            "https://"
                + repo.get("tool_shed")
                + "/view/"
                + repo.get("owner")
                + "/"
                + repo.get("name")
                + "/"
                + repo.get("changeset_revision");
      } else {
        repoLink = null;
      }
      final String doc = normalizedStep.doc;
      final Map<String, Object> nodeData = new HashMap<String, Object>();
      nodeData.put("id", stepId);
      nodeData.put("label", label);
      nodeData.put("tool_id", step.get("tool_id"));
      nodeData.put("doc", normalizedStep.doc);
      nodeData.put("repo_link", repoLink);
      nodeData.put("step_type", effectiveType);
      final Map<String, Object> nodeElement = new HashMap<String, Object>();
      nodeElement.put("group", "nodes");
      nodeElement.put("data", nodeData);
      nodeElement.put("classes", classes);
      nodeElement.put("position", elementPosition(step));
      elements.add(nodeElement);

      for (final WorkflowAdapter.Input input : normalizedStep.inputs) {
        final String edgeId = stepId + "__to__" + input.sourceStepLabel;
        final Map<String, Object> edgeData = new HashMap();
        edgeData.put("id", edgeId);
        edgeData.put("source", input.sourceStepLabel);
        edgeData.put("target", stepId);
        edgeData.put("input", input.inputName);
        edgeData.put("output", input.sourceOutputName);
        final Map<String, Object> edgeElement = new HashMap();
        edgeElement.put("group", "edges");
        edgeElement.put("data", edgeData);
        elements.add(edgeElement);
      }
      orderIndex++;
    }
    return elements;
  }

  static boolean isOrderIndexLabel(final String label) {
    try {
      Integer.parseInt(label);
      return true;
    } catch (NumberFormatException e) {
      return false;
    }
  }

  private static Map<String, Long> elementPosition(final Map<String, Object> step) {
    Map<String, Object> stepPosition = (Map<String, Object>) step.get("position");
    Map<String, Long> elementPosition = new HashMap();
    elementPosition.put("x", getIntegerValue(stepPosition, "left"));
    elementPosition.put("y", getIntegerValue(stepPosition, "top"));
    return elementPosition;
  }

  private static Long getIntegerValue(final Map<String, Object> fromMap, final String key) {
    final Object value = fromMap.get(key);
    if (value instanceof Float || value instanceof Double) {
      return (long) Math.floor((double) value);
    } else if (value instanceof Integer) {
      return ((Integer) value).longValue();
    } else {
      return (long) value;
    }
  }
}
