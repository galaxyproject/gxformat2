package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository</I><br>
 * This interface is implemented by {@link ToolShedRepositoryImpl}<br>
 */
public interface ToolShedRepository extends Savable {
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/name</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The name of the tool shed repository this tool can be found in. *
   *
   * </BLOCKQUOTE>
   */
  String getName();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/changeset_revision</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * The revision of the tool shed repository this tool can be found in. *
   *
   * </BLOCKQUOTE>
   */
  String getChangeset_revision();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/owner</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The owner of the tool shed repository this tool can be found in. *
   *
   * </BLOCKQUOTE>
   */
  String getOwner();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/tool_shed</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The URI of the tool shed containing the repository this tool can be found in - typically this
   * should be toolshed.g2.bx.psu.edu. *
   *
   * </BLOCKQUOTE>
   */
  String getTool_shed();
}
