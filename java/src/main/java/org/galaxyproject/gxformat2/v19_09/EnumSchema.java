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

import org.galaxyproject.gxformat2.v19_09.utils.Saveable;

/**
 * Auto-generated interface for <I>https://w3id.org/cwl/salad#EnumSchema</I><br>
 * This interface is implemented by {@link EnumSchemaImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * Define an enumerated type.
 *
 * </BLOCKQUOTE>
 */
public interface EnumSchema extends Saveable {
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#symbols</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the set of valid symbols. *
   *
   * </BLOCKQUOTE>
   */
  java.util.List<String> getSymbols();
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#type</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Must be `enum` *
   *
   * </BLOCKQUOTE>
   */
  enum_d961d79c225752b9fadb617367615ab176b47d77 getType();
}
