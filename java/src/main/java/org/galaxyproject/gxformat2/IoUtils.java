package org.galaxyproject.gxformat2;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.yaml.snakeyaml.Yaml;

public class IoUtils {

  public static Object readYamlFromPath(final String pathAsString) throws IOException {
    final Path path = Paths.get(pathAsString);
    return readYamlFromPath(path);
  }

  public static Object readYamlFromPath(final Path path) throws IOException {
    final String workflowContents = new String(Files.readAllBytes(path), "UTF8");
    final Yaml yaml = new Yaml();
    return yaml.load(workflowContents);
  }
}
