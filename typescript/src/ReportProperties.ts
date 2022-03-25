
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/v19_09#Report
 *
 * Definition of an invocation report for this workflow. Currently the only
 * field is 'markdown'.
 * 
 */
export interface ReportProperties  {
                    
  extensionFields?: Internal.Dictionary<any>

  /**
   * Galaxy flavored Markdown to define an invocation report.
   * 
   */
  markdown: string
}