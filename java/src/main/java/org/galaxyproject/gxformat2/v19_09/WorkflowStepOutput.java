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
}
