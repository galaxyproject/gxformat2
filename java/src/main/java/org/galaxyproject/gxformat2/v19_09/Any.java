package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

public enum Any {
  ANY("Any");

  private static String[] symbols = new String[] {"Any"};
  private String docVal;

  private Any(final String docVal) {
    this.docVal = docVal;
  }

  public static Any fromDocumentVal(final String docVal) {
    for (final Any val : Any.values()) {
      if (val.docVal.equals(docVal)) {
        return val;
      }
    }
    throw new ValidationException(String.format("Expected one of %s", Any.symbols, docVal));
  }
}
