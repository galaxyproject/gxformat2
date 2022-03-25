package org.galaxyproject.gxformat2.v19_09.utils;

import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;

public class Validator {
  public static void main(final String[] args) throws Exception {
    if (args.length != 1) {
      throw new Exception("No argument supplied to validate.");
    }
    // TODO: allow URLs and such.
    final File uri = new File(args[0]);
    Object doc = RootLoader.loadDocument(uri);
    ObjectMapper mapper = new ObjectMapper();
    mapper
        .setSerializationInclusion(Include.NON_NULL)
        .writerWithDefaultPrettyPrinter()
        .writeValue(System.out, doc);
    System.out.println();
  }
}
