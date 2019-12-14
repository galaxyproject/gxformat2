package org.galaxyproject.gxformat2;

import java.util.List;
import java.util.Map;

public interface WorkflowAdapter {
  public List<Map<String, Object>> normalizedSteps();
}
