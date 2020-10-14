package org.galaxyproject.gxformat2;

import java.io.File;
import org.junit.Test;

public class LintExamplesTest {

  @Test
  public void testLinting() throws Exception {
    for (final File file : TestUtils.getExamples("lint")) {
      final String path = file.getAbsolutePath();
      // HACK: Java linter doesn't handle Markdown parsing yet?
      // HACK: Java linter doesn't know about int/float default validation yet either :(
      if (path.indexOf("markdown") >= 0
          || path.indexOf("int") >= 0
          || path.indexOf("float") >= 0
          || path.indexOf("string_input") >= 0) {
        continue;
      }
      final String exitCodeString = file.getName().substring(0, 1);
      final int expectedExitCode = Integer.parseInt(exitCodeString);
      final int actualExitCode = Lint.lint(new String[] {path});
      if (expectedExitCode != actualExitCode) {
        final String template =
            "File [%s] didn't lint properly - expected exit code [%d], got [%d].";
        assert false : template.format(template, path, expectedExitCode, actualExitCode);
      }
    }
  }
}
