package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStep</I><br>
 * This interface is implemented by {@link WorkflowStepImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * Workflow step.
 *
 * </BLOCKQUOTE>
 */
public interface WorkflowStep
    extends Identified, Labeled, Documented, HasStepPosition, ReferencesTool, Savable {
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
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepPosition/position</I><br>
   */
  java.util.Optional<StepPosition> getPosition();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool/tool_id</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The tool ID used to run this step of the workflow (e.g. 'cat1' or
   * 'toolshed.g2.bx.psu.edu/repos/nml/collapse_collections/collapse_dataset/4.0'). *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getTool_id();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool/tool_shed_repository</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * The Galaxy Tool Shed repository that should be installed in order to use this tool. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<ToolShedRepository> getTool_shed_repository();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool/tool_version</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The tool version corresponding used to run this step of the workflow. For tool shed installed
   * tools, the ID generally uniquely specifies a version and this field is optional. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getTool_version();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#in</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the input parameters of the workflow step. The process is ready to run when all
   * required input parameters are associated with concrete values. Input parameters include a
   * schema for each parameter which is used to validate the input object. It may also be used build
   * a user interface for constructing the input object. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<java.util.List<Object>> getIn();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#out</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the parameters representing the output of the process. May be used to generate and/or
   * validate the output object. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<java.util.List<Object>> getOut();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStep/state</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Structured tool state. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<Object> getState();
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#type</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Workflow step module's type (defaults to 'tool'). *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<WorkflowStepType> getType();
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#run</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Specifies a subworkflow to run. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<GalaxyWorkflow> getRun();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStep/runtime_inputs</I><br>
   */
  java.util.Optional<java.util.List<Object>> getRuntime_inputs();
}
