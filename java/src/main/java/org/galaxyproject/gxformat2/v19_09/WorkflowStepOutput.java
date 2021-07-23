package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

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
public interface WorkflowStepOutput extends Identified, Savable {
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
  java.util.Optional<java.util.List<Object>> getAdd_tags();
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
  java.util.Optional<java.util.List<Object>> getRemove_tags();
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/rename</I>
   * <br>
   */
  java.util.Optional<String> getRename();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/set_columns</I><br>
   */
  java.util.Optional<java.util.List<Object>> getSet_columns();
}
