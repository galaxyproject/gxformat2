package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowInputParameter</I><br>
 * This interface is implemented by {@link WorkflowInputParameterImpl}<br>
 */
public interface WorkflowInputParameter extends InputParameter, Savable {
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
