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
 * Auto-generated interface for <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput</I>
 * <br>
 * This interface is implemented by {@link WorkflowStepOutputImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * Associate an output parameter of the underlying process with a workflow parameter. The workflow
 * parameter (given in the `id` field) be may be used as a `source` to connect with input parameters
 * of other workflow steps, or with an output parameter of the process.
 *
 * <p>A unique identifier for this workflow output parameter. This is the identifier to use in the
 * `source` field of `WorkflowStepInput` to connect the output value to downstream parameters.
 *
 * </BLOCKQUOTE>
 */
public interface WorkflowStepOutput extends Identified, Saveable {
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
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/add_tags</I><br>
   */
  java.util.Optional<java.util.List<String>> getAdd_tags();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/change_datatype</I><br>
   */
  java.util.Optional<String> getChange_datatype();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/delete_intermediate_datasets</I>
   * <br>
   */
  java.util.Optional<Boolean> getDelete_intermediate_datasets();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/hide</I>
   * <br>
   */
  java.util.Optional<Boolean> getHide();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/remove_tags</I><br>
   */
  java.util.Optional<java.util.List<String>> getRemove_tags();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/rename</I>
   * <br>
   */
  java.util.Optional<String> getRename();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/set_columns</I><br>
   */
  java.util.Optional<java.util.List<String>> getSet_columns();
}
