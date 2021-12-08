// Copyright Common Workflow Language project contributors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

public enum GalaxyType {
  NULL("null"),
  BOOLEAN("boolean"),
  INT("int"),
  LONG("long"),
  FLOAT("float"),
  DOUBLE("double"),
  STRING("string"),
  INTEGER("integer"),
  TEXT("text"),
  FILE("File"),
  DATA("data"),
  COLLECTION("collection");

  private static String[] symbols =
      new String[] {
        "null",
        "boolean",
        "int",
        "long",
        "float",
        "double",
        "string",
        "integer",
        "text",
        "File",
        "data",
        "collection"
      };
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
