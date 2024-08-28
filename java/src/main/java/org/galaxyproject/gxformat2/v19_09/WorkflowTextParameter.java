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
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowTextParameter</I><br>
 * This interface is implemented by {@link WorkflowTextParameterImpl}<br>
 */
public interface WorkflowTextParameter extends BaseInputParameter, Saveable {
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
   * Getter for property <I>https://w3id.org/cwl/salad#Documented/doc</I><br>
   *
   * <BLOCKQUOTE>
   *
   * A documentation string for this object, or an array of strings which should be concatenated. *
   *
   * </BLOCKQUOTE>
   */
  Object getDoc();
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#default</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The default value to use for this parameter if the parameter is missing from the input object,
   * or if the value of the parameter in the input object is `null`. Default values are applied
   * before evaluating expressions (e.g. dependent `valueFrom` fields). *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<Object> getDefault();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepPosition/position</I><br>
   */
  java.util.Optional<StepPosition> getPosition();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#BaseInputParameter/optional</I><br>
   *
   * <BLOCKQUOTE>
   *
   * If set to true, `WorkflowInputParameter` is not required to submit the workflow. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<Boolean> getOptional();
  /** Getter for property <I>https://w3id.org/cwl/salad#type</I><br> */
  Object getType();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowTextParameter/validators</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Apply one more validators to the input value. Input is valid if all validators succeed. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<java.util.List<Object>> getValidators();
}
