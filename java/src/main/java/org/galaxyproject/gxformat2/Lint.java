package org.galaxyproject.gxformat2;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;
import org.yaml.snakeyaml.Yaml;

public class Lint {
  public static int EXIT_CODE_SUCCESS = 0;
  public static int EXIT_CODE_LINT_FAILED = 1;
  public static int EXIT_CODE_FORMAT_ERROR = 2;
  public static int EXIT_CODE_FILE_PARSE_FAILED = 3;

  public static void main(String[] args) throws Exception {
    final int exitCode = lint(args);
    System.exit(exitCode);
  }

  public static int lint(final String[] args) throws Exception {
    final Path path = Paths.get(args[0]);
    final String workflowContents = new String(Files.readAllBytes(path), "UTF8");
    final Yaml yaml = new Yaml();
    final Map<String, Object> object = (Map<String, Object>) yaml.load(workflowContents);
    final String wfClass = (String) object.get("class");
    GalaxyWorkflowLinter linter;
    if (wfClass != null && wfClass.equals("GalaxyWorkflow")) {
      linter = new Format2Linter();
    } else {
      linter = new NativeLinter();
    }
    final LintContext lintContext = new LintContext();
    linter.lint(lintContext, object);
    lintContext.printMessages();
    int exitCode;
    if (lintContext.getFoundErrors()) {
      exitCode = EXIT_CODE_FORMAT_ERROR;
    } else if (lintContext.getFoundWarns()) {
      exitCode = EXIT_CODE_LINT_FAILED;
    } else {
      exitCode = EXIT_CODE_SUCCESS;
    }
    return exitCode;
  }
}
