
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/gxformat2common#HasStepErrors
 */
export interface HasStepErrorsProperties  {
                    
  /**
   * During Galaxy export there may be some problem validating the tool state, tool used, etc..
   * that will be indicated by this field. The Galaxy user should be warned of these problems before
   * the workflow can be used in Galaxy.
   * 
   * This field should not be used in human written Galaxy workflow files.
   * 
   * A typical problem is the referenced tool is not installed, this can be fixed by installed the tool
   * and re-saving the workflow and then re-exporting it.
   * 
   */
  errors?: undefined | string
}