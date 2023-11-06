package org.galaxyproject.gxformat2.v19_09.utils;

import java.util.List;
import java.util.Map;
import org.snakeyaml.engine.v2.api.Load;
import org.snakeyaml.engine.v2.api.LoadSettings;
import org.snakeyaml.engine.v2.schema.CoreSchema;

public class YamlUtils {

  public static Map<String, Object> mapFromString(final String text) {
    LoadSettings settings = LoadSettings.builder().setSchema(new CoreSchema()).build();
    Load load = new Load(settings);
    final Map<String, Object> result = (Map<String, Object>) load.loadFromString(text);
    return result;
  }

  public static List<Object> listFromString(final String text) {
    LoadSettings settings = LoadSettings.builder().setSchema(new CoreSchema()).build();
    Load load = new Load(settings);
    final List<Object> result = (List<Object>) load.loadFromString(text);
    return result;
  }
}
