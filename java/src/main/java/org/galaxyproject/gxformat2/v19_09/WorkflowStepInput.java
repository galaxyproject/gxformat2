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
 * Auto-generated interface for <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepInput</I>
 * <br>
 * This interface is implemented by {@link WorkflowStepInputImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * TODO:
 *
 * </BLOCKQUOTE>
 */
public interface WorkflowStepInput extends Identified, Sink, Labeled, Saveable {
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#Identified/id</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The unique identifier for this object. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getId();
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#source</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Specifies one or more workflow parameters that will provide input to the underlying step
   * parameter. *
   *
   * </BLOCKQUOTE>
   */
  Object getSource();
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#Labeled/label</I><br>
   *
   * <BLOCKQUOTE>
   *
   * A short, human-readable label of this object. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getLabel();
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#default</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The default value for this parameter to use if either there is no `source` field, or the value
   * produced by the `source` is `null`. The default must be applied prior to scattering or
   * evaluating `valueFrom`. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<Object> getDefault();
}
