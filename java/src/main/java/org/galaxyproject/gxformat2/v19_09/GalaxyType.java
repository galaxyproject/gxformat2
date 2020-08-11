package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

public enum GalaxyType {
  INTEGER("integer"),
  TEXT("text"),
  FILE("File"),
  DATA("data"),
  COLLECTION("collection");

  private static String[] symbols = new String[] {"integer", "text", "File", "data", "collection"};
  private String docVal;

  private GalaxyType(final String docVal) {
    this.docVal = docVal;
  }

  public static GalaxyType fromDocumentVal(final String docVal) {
    for (final GalaxyType val : GalaxyType.values()) {
      if (val.docVal.equals(docVal)) {
        return val;
      }
    }
    throw new ValidationException(String.format("Expected one of %s", GalaxyType.symbols, docVal));
  }
}
