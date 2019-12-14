package org.galaxyproject.gxformat2;

import java.io.File;
import java.util.Arrays;

public class TestUtils {
  public static Iterable<File> getExamples(final String exampleType) {
    final File examplesDirectory = new File("../tests/examples/" + exampleType);
    assert examplesDirectory.exists() : "test examples directory doesn't exist";
    assert examplesDirectory.isDirectory();
    return Arrays.asList(examplesDirectory.listFiles());
  }
}
