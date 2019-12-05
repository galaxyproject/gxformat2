package org.galaxyproject.gxformat2;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class NativeLinter implements GalaxyWorkflowLinter {
  public static String LINT_FAILED_NO_OUTPUTS = "Workflow contained no outputs";
  public static String LINT_FAILED_OUTPUT_NO_LABEL = "Workflow contained output without a label";

  public void lint(final LintContext lintContext, final Map<String, Object> workflow) {
    LintUtils.ensureKey(lintContext, workflow, "format-version", String.class, "0.1");
    LintUtils.ensureKey(lintContext, workflow, "a_galaxy_workflow", String.class, "true");

    final Map<String, Object> steps = LintUtils.stepMap(lintContext, workflow);
    boolean foundOutputs = false;
    boolean foundOutputsWithoutLabel = false;

    for (Map.Entry<String, Object> stepEntry : steps.entrySet()) {
      final String orderIndexStr = stepEntry.getKey();
      try {
        final int orderIndex = Integer.parseInt(orderIndexStr);
      } catch (NumberFormatException e) {
        lintContext.error("expected step_key to be integer not [%s]", orderIndexStr);
      }
      if (!(stepEntry.getValue() instanceof Map)) {
        lintContext.error("expected step value to be Map not [%s]", stepEntry.getValue());
      }
      Map<String, Object> step = (Map<String, Object>) stepEntry.getValue();
      List<String> workflowOutputs =
          LintUtils.ensureKeyIfPresent(
              lintContext, step, "workflow_outputs", new ArrayList<String>(), List.class);
      for (Object workflowOutputObject : workflowOutputs) {
        foundOutputs = true;
        if (!(workflowOutputObject instanceof Map)) {
          lintContext.error("Not a map");
        }
        final Map<String, String> workflowOutput = (Map<String, String>) workflowOutputObject;
        final String label = workflowOutput.get("label");
        if (label == null || label.length() == 0) {
          foundOutputsWithoutLabel = true;
        }
      }
      final String stepType =
          LintUtils.ensureKeyIfPresent(lintContext, step, "type", "tool", String.class);
      assert stepType != null;
      if (stepType != null && stepType.equals("subworkflow")) {
        final Map<String, Object> subworkflow =
            (Map<String, Object>)
                LintUtils.ensureKey(lintContext, step, "subworkflow", Map.class, null);
        assert subworkflow != null;
        lint(lintContext, subworkflow);
      }
      LintUtils.lintStepErrors(lintContext, step);
    }
    Map<String, Object> reportMap =
        (Map<String, Object>)
            LintUtils.ensureKeyIfPresent(
                lintContext, workflow, "report", (Map<String, Object>) null, Map.class);
    if (reportMap != null) {
      LintUtils.ensureKey(lintContext, reportMap, "markdown", String.class, null);
    }
    if (!foundOutputs) {
      lintContext.warn(LINT_FAILED_NO_OUTPUTS);
    }
    if (foundOutputsWithoutLabel) {
      lintContext.warn(LINT_FAILED_OUTPUT_NO_LABEL);
    }
  }
}
