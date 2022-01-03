
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/gxformat2common#StepPosition
 *
 * This field specifies the location of the step's node when rendered in the workflow editor.
 */
export interface StepPositionProperties  {
                    
  extensionFields?: Internal.Dictionary<any>

  /**
   * Relative vertical position of the step's node when rendered in the workflow editor.
   * 
   */
  top: number

  /**
   * Relative horizontal position of the step's node when rendered in the workflow editor.
   * 
   */
  left: number
}