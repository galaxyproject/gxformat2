package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepErrors</I><br>
 */
public interface HasStepErrors extends Savable {
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepErrors/errors</I><br>
   *
   * <BLOCKQUOTE>
   *
   * During Galaxy export there may be some problem validating the tool state, tool used, etc.. that
   * will be indicated by this field. The Galaxy user should be warned of these problems before the
   * workflow can be used in Galaxy.
   *
   * <p>This field should not be used in human written Galaxy workflow files.
   *
   * <p>A typical problem is the referenced tool is not installed, this can be fixed by installed
   * the tool and re-saving the workflow and then re-exporting it. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getErrors();
}
