package org.galaxyproject.gxformat2;

import java.io.File;
import org.junit.Test;

public class LintExamplesTest {

  @Test
  public void testLinting() throws Exception {
    final File examplesDirectory = new File("../tests/examples");
    assert examplesDirectory.exists() : "test examples directory doesn't exist";
    assert examplesDirectory.isDirectory();
    for (final File file : examplesDirectory.listFiles()) {
      final String path = file.getAbsolutePath();
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
