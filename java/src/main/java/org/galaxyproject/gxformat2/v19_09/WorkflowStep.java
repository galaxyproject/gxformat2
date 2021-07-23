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

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
* Auto-generated interface for <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStep</I><BR>This interface is implemented by {@link WorkflowStepImpl}<BR> <BLOCKQUOTE>
 This represents a non-input step a Galaxy Workflow.
 
 # A note about `state` and `tool_state` fields.
 
 Only one or the other should be specified. These are two ways to represent the "state"
 of a tool at this workflow step. Both are essentially maps from parameter names to
 parameter values.
 
 `tool_state` is much more low-level and expects a flat dictionary with each value a JSON
 dump. Nested tool structures such as conditionals and repeats should have all their values
 in the JSON dumped string. In general `tool_state` may be present in workflows exported from
 Galaxy but shouldn't be written by humans.
 
 `state` can contained a typed map. Repeat values can be represented as YAML arrays. An alternative
 to representing `state` this way is defining inputs with default values.
  </BLOCKQUOTE>
 */
public interface WorkflowStep extends Identified, Labeled, Documented, HasStepPosition, ReferencesTool, HasStepErrors, HasUUID, Savable {
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#Identified/id</I><BR>
   * <BLOCKQUOTE>
   * The unique identifier for this object.   * </BLOCKQUOTE>
   */

  java.util.Optional<String> getId();
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#Labeled/label</I><BR>
   * <BLOCKQUOTE>
   * A short, human-readable label of this object.   * </BLOCKQUOTE>
   */

  java.util.Optional<String> getLabel();
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#Documented/doc</I><BR>
   * <BLOCKQUOTE>
   * A documentation string for this object, or an array of strings which should be concatenated.   * </BLOCKQUOTE>
   */

  Object getDoc();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepPosition/position</I><BR>

   */

  java.util.Optional<StepPosition> getPosition();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool/tool_id</I><BR>
   * <BLOCKQUOTE>
   * The tool ID used to run this step of the workflow (e.g. 'cat1' or 'toolshed.g2.bx.psu.edu/repos/nml/collapse_collections/collapse_dataset/4.0').
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<String> getTool_id();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool/tool_shed_repository</I><BR>
   * <BLOCKQUOTE>
   * The Galaxy Tool Shed repository that should be installed in order to use this tool.
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<ToolShedRepository> getTool_shed_repository();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool/tool_version</I><BR>
   * <BLOCKQUOTE>
   * The tool version corresponding used to run this step of the workflow. For tool shed installed tools, the ID generally uniquely specifies a version
   * and this field is optional.
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<String> getTool_version();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepErrors/errors</I><BR>
   * <BLOCKQUOTE>
   * During Galaxy export there may be some problem validating the tool state, tool used, etc..
   * that will be indicated by this field. The Galaxy user should be warned of these problems before
   * the workflow can be used in Galaxy.
   * 
   * This field should not be used in human written Galaxy workflow files.
   * 
   * A typical problem is the referenced tool is not installed, this can be fixed by installed the tool
   * and re-saving the workflow and then re-exporting it.
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<String> getErrors();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#HasUUID/uuid</I><BR>
   * <BLOCKQUOTE>
   * UUID uniquely representing this element.
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<String> getUuid();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#in</I><BR>
   * <BLOCKQUOTE>
   * Defines the input parameters of the workflow step.  The process is ready to
   * run when all required input parameters are associated with concrete
   * values.  Input parameters include a schema for each parameter which is
   * used to validate the input object.  It may also be used build a user
   * interface for constructing the input object.
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<java.util.List<Object>> getIn();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#out</I><BR>
   * <BLOCKQUOTE>
   * Defines the parameters representing the output of the process.  May be
   * used to generate and/or validate the output object.
   * 
   * This can also be called 'outputs' for legacy reasons - but the resulting
   * workflow document is not a valid instance of this schema.
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<java.util.List<Object>> getOut();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#state</I><BR>
   * <BLOCKQUOTE>
   * Structured tool state.
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<Object> getState();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#tool_state</I><BR>
   * <BLOCKQUOTE>
   * Unstructured tool state.
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<Object> getTool_state();
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#type</I><BR>
   * <BLOCKQUOTE>
   * Workflow step module's type (defaults to 'tool').
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<WorkflowStepType> getType();
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#run</I><BR>
   * <BLOCKQUOTE>
   * Specifies a subworkflow to run.
   *    * </BLOCKQUOTE>
   */

  java.util.Optional<GalaxyWorkflow> getRun();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStep/runtime_inputs</I><BR>

   */

  java.util.Optional<java.util.List<Object>> getRuntime_inputs();
}
