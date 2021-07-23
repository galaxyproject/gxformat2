package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

public enum WorkflowStepType {
  TOOL("tool"),
  SUBWORKFLOW("subworkflow"),
  PAUSE("pause");

  private static String[] symbols = new String[] {"tool", "subworkflow", "pause"};
  private String docVal;

  private WorkflowStepType(final String docVal) {
    this.docVal = docVal;
  }

  public static WorkflowStepType fromDocumentVal(final String docVal) {
    for (final WorkflowStepType val : WorkflowStepType.values()) {
      if (val.docVal.equals(docVal)) {
        return val;
      }
    }
    throw new ValidationException(
        String.format("Expected one of %s", WorkflowStepType.symbols, docVal));
  }
}
