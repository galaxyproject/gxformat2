package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for <I>https://galaxyproject.org/gxformat2/v19_09#Report</I><br>
 * This interface is implemented by {@link ReportImpl}<br>
 *
 * <BLOCKQUOTE>
 *
 * Definition of an invocation report for this workflow. Currently the only field is 'markdown'.
 *
 * </BLOCKQUOTE>
 */
public interface Report extends Savable {
  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#Report/markdown</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Galaxy flavored Markdown to define an invocation report. *
   *
   * </BLOCKQUOTE>
   */
  String getMarkdown();
}
