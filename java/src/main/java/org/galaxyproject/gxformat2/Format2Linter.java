package org.galaxyproject.gxformat2;

import java.util.Map;
import org.galaxyproject.gxformat2.v19_09.utils.RootLoader;
import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

public class Format2Linter implements GalaxyWorkflowLinter {
  public void lint(final LintContext lintContext, final Map<String, Object> workflow) {
    try {
      RootLoader.loadDocument(workflow);
    } catch (ValidationException e) {
      lintContext.error("Validation failed " + e.toString());
    }
  }
}
