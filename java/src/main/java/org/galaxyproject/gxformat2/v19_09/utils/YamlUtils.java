package org.galaxyproject.gxformat2.v19_09.utils;

import java.util.Map;
import org.yaml.snakeyaml.Yaml;

public class YamlUtils {

  public static Map<String, Object> mapFromString(final String text) {
    Yaml yaml = new Yaml();
    final Map<String, Object> result = yaml.load(text);
    return result;
  }
}
