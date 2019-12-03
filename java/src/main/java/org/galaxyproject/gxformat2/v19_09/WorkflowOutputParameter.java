package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowOutputParameter</I><br>
 * This interface is implemented by {@link WorkflowOutputParameterImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * Describe an output parameter of a workflow. The parameter must be connected to one parameter
 * defined in the workflow that will provide the value of the output parameter. It is legal to
 * connect a WorkflowInputParameter to a WorkflowOutputParameter.
 *
 * </BLOCKQUOTE>
 */
public interface WorkflowOutputParameter extends OutputParameter, Savable {
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
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowOutputParameter/outputSource</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Specifies workflow parameter that supply the value of to the output parameter. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getOutputSource();
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#type</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Specify valid types of data that may be assigned to this parameter. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<GalaxyType> getType();
}
