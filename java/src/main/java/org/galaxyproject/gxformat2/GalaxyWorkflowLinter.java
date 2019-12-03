package org.galaxyproject.gxformat2;

import java.util.Map;

public interface GalaxyWorkflowLinter {
  public void lint(final LintContext lintContext, final Map<String, Object> workflow);
}
