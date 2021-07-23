package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool</I><br>
 */
public interface ReferencesTool extends Savable {
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
}
