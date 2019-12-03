package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

public enum PrimitiveType {
  NULL("null"),
  BOOLEAN("boolean"),
  INT("int"),
  LONG("long"),
  FLOAT("float"),
  DOUBLE("double"),
  STRING("string");

  private static String[] symbols =
      new String[] {"null", "boolean", "int", "long", "float", "double", "string"};
  private String docVal;

  private PrimitiveType(final String docVal) {
    this.docVal = docVal;
  }

  public static PrimitiveType fromDocumentVal(final String docVal) {
    for (final PrimitiveType val : PrimitiveType.values()) {
      if (val.docVal.equals(docVal)) {
        return val;
      }
    }
    throw new ValidationException(
        String.format("Expected one of %s", PrimitiveType.symbols, docVal));
  }
}
