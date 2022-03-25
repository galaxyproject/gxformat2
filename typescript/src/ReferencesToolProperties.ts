
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool
 */
export interface ReferencesToolProperties  {
                    
  /**
   * The tool ID used to run this step of the workflow (e.g. 'cat1' or 'toolshed.g2.bx.psu.edu/repos/nml/collapse_collections/collapse_dataset/4.0').
   * 
   */
  tool_id?: undefined | string

  /**
   * The Galaxy Tool Shed repository that should be installed in order to use this tool.
   * 
   */
  tool_shed_repository?: undefined | Internal.ToolShedRepository

  /**
   * The tool version corresponding used to run this step of the workflow. For tool shed installed tools, the ID generally uniquely specifies a version
   * and this field is optional.
   * 
   */
  tool_version?: undefined | string
}