
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository
 */
export interface ToolShedRepositoryProperties  {
                    
  extensionFields?: Internal.Dictionary<any>

  /**
   * The name of the tool shed repository this tool can be found in.
   * 
   */
  name: string

  /**
   * The revision of the tool shed repository this tool can be found in.
   * 
   */
  changeset_revision: string

  /**
   * The owner of the tool shed repository this tool can be found in.
   * 
   */
  owner: string

  /**
   * The URI of the tool shed containing the repository this tool can be found in - typically this should be toolshed.g2.bx.psu.edu.
   * 
   */
  tool_shed: string
}