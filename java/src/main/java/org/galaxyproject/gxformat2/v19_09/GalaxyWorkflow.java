package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow</I><br>
 * This interface is implemented by {@link GalaxyWorkflowImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * A Galaxy workflow description. This record corresponds to the description of a workflow that
 * should be executable on a Galaxy server that includes the contained tool definitions.
 *
 * <p>The workflows API or the user interface of Galaxy instances that are of version 19.09 or newer
 * should be able to import a document defining this record.
 *
 * <p>## A note about `label` field.
 *
 * <p>This is the name of the workflow in the Galaxy user interface. This is the mechanism that
 * users will primarily identify the workflow using. Legacy support - this may also be called 'name'
 * and Galaxy will consume the workflow document fine and treat this attribute correctly - however
 * in order to validate against this workflow definition schema the attribute should be called
 * `label`.
 *
 * </BLOCKQUOTE>
 */
public interface GalaxyWorkflow extends Process, HasUUID, Savable {
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
   * Getter for property <I>https://w3id.org/cwl/cwl#inputs</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the input parameters of the process. The process is ready to run when all required
   * input parameters are associated with concrete values. Input parameters include a schema for
   * each parameter which is used to validate the input object. It may also be used to build a user
   * interface for constructing the input object.
   *
   * <p>When accepting an input object, all input parameters must have a value. If an input
   * parameter is missing from the input object, it must be assigned a value of `null` (or the value
   * of `default` for that parameter, if provided) for the purposes of validation and evaluation of
   * expressions. *
   *
   * </BLOCKQUOTE>
   */
  java.util.List<Object> getInputs();
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#outputs</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the parameters representing the output of the process. May be used to generate and/or
   * validate the output object. *
   *
   * </BLOCKQUOTE>
   */
  java.util.List<Object> getOutputs();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#HasUUID/uuid</I><br>
   *
   * <BLOCKQUOTE>
   *
   * UUID uniquely representing this element. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getUuid();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/class</I><br>
   */
  String getClass_();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/steps</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The individual steps that make up the workflow. Each step is executed when all of its input
   * data links are fulfilled. *
   *
   * </BLOCKQUOTE>
   */
  java.util.List<Object> getSteps();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/report</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Workflow invocation report template. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<Report> getReport();
}
