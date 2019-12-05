package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/gxformat2common#StepPosition</I><br>
 * This interface is implemented by {@link StepPositionImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * This field specifies the location of the step's node when rendered in the workflow editor.
 *
 * </BLOCKQUOTE>
 */
public interface StepPosition extends Savable {
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#StepPosition/top</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * Relative vertical position of the step's node when rendered in the workflow editor. *
   *
   * </BLOCKQUOTE>
   */
  Object getTop();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#StepPosition/left</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Relative horizontal position of the step's node when rendered in the workflow editor. *
   *
   * </BLOCKQUOTE>
   */
  Object getLeft();
}
